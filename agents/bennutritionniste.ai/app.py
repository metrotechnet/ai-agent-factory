# Endpoint to like or dislike an answer by question_id
from fastapi import status


from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi import Query

from dotenv import load_dotenv
from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from core.query_chromadb import ask_question_stream, ask_question_stream_gemini
from core.query_vertexaidb import ask_question_stream_vertex, ask_question_stream_vertex_gemini
import json
from pathlib import Path
from core.pipeline_gdrive import run_pipeline
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timedelta

import threading

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

# Path to question log file
QUESTION_LOG_PATH = PROJECT_ROOT / "question_log.json"
# Lock for thread-safe file access
question_log_lock = threading.Lock()

def save_question_response(question_id, question, response):
    """Save question, response, and id to the log file."""
    entry = {
        "question_id": question_id,
        "question": question,
        "response": response,
        "timestamp": datetime.now().isoformat(),
        "comments": []
    }
    with question_log_lock:
        try:
            if QUESTION_LOG_PATH.exists():
                with open(QUESTION_LOG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
        except Exception:
            data = []
        data.append(entry)
        with open(QUESTION_LOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def add_comment_to_question(question_id, comment):
    """Add a comment to a question by id."""
    with question_log_lock:
        try:
            if QUESTION_LOG_PATH.exists():
                with open(QUESTION_LOG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                return False
        except Exception:
            return False
        for entry in data:
            if entry.get("question_id") == question_id:
                # Remplace tous les commentaires par le nouveau commentaire
                entry["comments"] = [{
                    "comment": comment,
                    "timestamp": datetime.now().isoformat()
                }]
                with open(QUESTION_LOG_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return True
        return False

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
    
    question_id = str(uuid.uuid4())
    def generate():
        # Send session_id and question_id in first chunk
        yield f"data: {json.dumps({'session_id': session_id, 'question_id': question_id, 'chunk': ''})}\n\n"

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

        # Save question, response, and id to file
        save_question_response(question_id, request.question, assistant_response)

    return StreamingResponse(
        generate(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )

# Endpoint to add a comment to a question by id
@app.post("/api/add_comment")
def add_comment_api(
    question_id: str = Body(...),
    comment: str = Body(...)
):
    success = add_comment_to_question(question_id, comment)
    if success:
        return {"status": "success", "message": "Comment added"}
    else:
        return {"status": "error", "message": "Question ID not found"}
    
@app.post("/api/like_answer")
def like_answer(
    question_id: str = Body(...),
    like: bool = Body(...)
):
    """Add a like or dislike to a question by id. Stores as a list of likes/dislikes (for possible multiple votes)."""
    with question_log_lock:
        try:
            if QUESTION_LOG_PATH.exists():
                with open(QUESTION_LOG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                return {"status": "error", "message": "Log file not found"}
        except Exception:
            return {"status": "error", "message": "Could not read log file"}
        for entry in data:
            if entry.get("question_id") == question_id:
                if "likes" not in entry:
                    entry["likes"] = []
                entry["likes"].append({
                    "like": like,
                    "timestamp": datetime.now().isoformat()
                })
                with open(QUESTION_LOG_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return {"status": "success", "message": "Vote recorded"}
        return {"status": "error", "message": "Question ID not found"}    
    
# Endpoint to download the question_log.json file (protected by key in URL argument)
from fastapi import Query
@app.get("/api/download_log")
def download_question_log(key: str = Query(...)):
    if key != "dboubou363":
        return {"status": "error", "message": "Unauthorized"}
    if not QUESTION_LOG_PATH.exists():
        return {"status": "error", "message": "Log file not found"}
    return FileResponse(
        path=str(QUESTION_LOG_PATH),
        filename="question_log.json",
        media_type="application/json"
    )

# Endpoint to serve log_report.html (requires ?key=...)
@app.get("/log_report", response_class=HTMLResponse)
def serve_log_report(request: Request, key: str = Query(...)):
    # Only allow access if key is correct
    if key != "dboubou363":
        return HTMLResponse("<h3 style='color:red;text-align:center;margin-top:2em'>Unauthorized: Invalid key</h3>", status_code=401)
    return templates.TemplateResponse("log_report.html", {"request": request})

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
def update_pipeline(request: Request):
    """
    Endpoint to trigger Google Drive document indexing pipeline.
    Called by Cloud Scheduler daily at 3 AM.
    """
    try:
        print(f"[{datetime.now().isoformat()}] Pipeline update triggered")
        print(f"User-Agent: {request.headers.get('user-agent', 'Unknown')}")
        
        result = run_pipeline()
        
        if result.get("error"):
            print(f"❌ Pipeline error: {result['error']}")
            return {
                "status": "error",
                "message": result['error'],
                "authenticated": result.get("authenticated", False)
            }
        
        processed = result.get("processed", 0)
        total = result.get("total", 0)
        
        print(f"✅ Pipeline completed: {processed}/{total} documents processed")
        
        return {
            "status": "success",
            "message": f"Pipeline executed successfully",
            "processed": processed,
            "total": total,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Pipeline exception: {str(e)}")
        return {
            "status": "error",
            "message": f"Pipeline failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
