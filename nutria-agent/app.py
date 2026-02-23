# =====================================================
# Imports - Main application imports
# =====================================================
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path

# Import route modules
from api.routes import query, translation, tts, report, config as config_routes, sessions, update

# =====================================================
# Configuration & Application Setup
# =====================================================
PROJECT_ROOT = Path(__file__).parent
env_path = PROJECT_ROOT / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="IMX Agent Factory")

# Configure CORS with dynamic origins
import os

# Get Firebase project ID from environment
firebase_project_id = os.getenv("FIREBASE_PROJECT_ID", "your-project")

# Build allowed origins dynamically
allowed_origins = [
    f"https://{firebase_project_id}.web.app",
    f"https://{firebase_project_id}.firebaseapp.com",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5000"
]

# Allow additional origins from ADDITIONAL_CORS_ORIGINS env var (comma-separated)
additional_origins = os.getenv("ADDITIONAL_CORS_ORIGINS", "")
if additional_origins:
    allowed_origins.extend([origin.strip() for origin in additional_origins.split(",") if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))

# =====================================================
# Include API Routes
# =====================================================
app.include_router(query.router, tags=["query"])
app.include_router(translation.router, tags=["translation"])
app.include_router(tts.router, tags=["tts"])
app.include_router(report.router, tags=["report"])
app.include_router(config_routes.router, tags=["config"])
app.include_router(sessions.router, tags=["sessions"])
app.include_router(update.router, tags=["update"])

# =====================================================
# Main Routes
# =====================================================
@app.get("/")
def home():
    """API root endpoint - frontend is hosted on Firebase"""
    return {"status": "ok", "message": "IMX Agent Factory API"}


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}


# =====================================================
# Run Application
# =====================================================
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)