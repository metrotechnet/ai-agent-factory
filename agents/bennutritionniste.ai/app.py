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

# Load environment variables from the correct location
PROJECT_ROOT = Path(__file__).parent
env_path = PROJECT_ROOT / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Personal AI Agent")

# Mount static files and templates with absolute paths
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))

class QueryRequest(BaseModel):
    question: str
    language: str = "fr"
    timezone: str = "UTC"
    locale: str = "fr-FR"

@app.post("/query")
async def query_agent(request: QueryRequest):
    def generate():
        for chunk in ask_question_stream(
            request.question, 
            language=request.language,
            timezone=request.timezone,
            locale=request.locale
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
    
    return StreamingResponse(
        generate(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )

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

@app.post("/update")
def update_pipeline(limit: int = 5):
    run_pipeline(limit=limit)
    return {"status": "Pipeline exécuté, nouvelles vidéos indexées"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
