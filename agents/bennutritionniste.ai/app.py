from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from core.query_chromadb import ask_question_stream, ask_question_stream_gemini
from core.query_vertexaidb import ask_question_stream_vertex, ask_question_stream_vertex_gemini
import json
from pathlib import Path
from core.pipeline_instagram import run_pipeline
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta

# Load environment variables from the correct location
PROJECT_ROOT = Path(__file__).parent
env_path = PROJECT_ROOT / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Personal AI Agent")

# Mount static files and templates with absolute paths
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))

# In-memory session storage (use Redis or database in production)
conversation_sessions: Dict[str, Dict] = {}
SESSION_TIMEOUT = timedelta(hours=2)

class QueryRequest(BaseModel):
    question: str
    language: str = "fr"
    timezone: str = "UTC"
    locale: str = "fr-FR"
    session_id: Optional[str] = None
    
class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str

@app.post("/query")
async def query_agent(request: QueryRequest):
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    print(f"Session ID: {session_id}")
    # Clean old sessions
    _clean_old_sessions()
    
    # Initialize session if new
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            'messages': [],
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
    
    # Get conversation history
    session = conversation_sessions[session_id]
    conversation_history = session['messages']
    
    # Add user message to history
    user_message = {
        'role': 'user',
        'content': request.question,
        'timestamp': datetime.now().isoformat()
    }
    conversation_history.append(user_message)
    
    # Update last activity
    session['last_activity'] = datetime.now()
    
    def generate():
        # Send session_id in first chunk
        yield f"data: {json.dumps({'session_id': session_id, 'chunk': ''})}\n\n"
        
        assistant_response = ""
        for chunk in ask_question_stream(
            request.question, 
            language=request.language,
            timezone=request.timezone,
            locale=request.locale,
            conversation_history=conversation_history
        ):
            assistant_response += chunk
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        # Add assistant response to history
        assistant_message = {
            'role': 'assistant',
            'content': assistant_response,
            'timestamp': datetime.now().isoformat()
        }
        conversation_history.append(assistant_message)
    
    return StreamingResponse(
        generate(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )

def _clean_old_sessions():
    """Remove sessions older than SESSION_TIMEOUT"""
    now = datetime.now()
    expired_sessions = [
        sid for sid, session in conversation_sessions.items()
        if now - session['last_activity'] > SESSION_TIMEOUT
    ]
    for sid in expired_sessions:
        del conversation_sessions[sid]

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/get_config")
def get_translations():
    """Get translations for the frontend"""
    try:
        translations_path = Path(__file__).parent / "config" / "config.json"
        with open(translations_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        return translations
    except FileNotFoundError:
        return {"error": "config not found"}
    except Exception as e:
        return {"error": f"Error loading config: {str(e)}"}

@app.post("/api/reset_session")
def reset_session(session_id: str = None):
    """Reset a conversation session"""
    if session_id and session_id in conversation_sessions:
        del conversation_sessions[session_id]
        return {"status": "success", "message": "Session reset"}
    return {"status": "info", "message": "No active session to reset"}

@app.get("/api/session_info")
def get_session_info(session_id: str):
    """Get information about a session"""
    if session_id in conversation_sessions:
        session = conversation_sessions[session_id]
        return {
            "exists": True,
            "message_count": len(session['messages']),
            "created_at": session['created_at'].isoformat(),
            "last_activity": session['last_activity'].isoformat()
        }
    return {"exists": False}

@app.post("/update")
def update_pipeline(limit: int = 5):
    run_pipeline(limit=limit)
    return {"status": "Pipeline exécuté, nouvelles vidéos indexées"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
