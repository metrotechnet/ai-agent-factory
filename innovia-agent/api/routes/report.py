"""
report.py
Endpoints for logging, comments, likes, and report downloads in the Bibliosense agent API.
Handles question log access and HTML report rendering.
"""
from fastapi import APIRouter, Body, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os

from api.logging import add_comment_to_question, add_like_to_question, _download_log_from_gcs

router = APIRouter()

PROJECT_ROOT = Path(__file__).parent.parent.parent
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))


@router.post("/api/add_comment")
def add_comment_api(
    question_id: str = Body(...),
    comment: str = Body(...)
):
    """Endpoint to add a comment to a question"""
    success = add_comment_to_question(question_id, comment)
    if success:
        return {"status": "success", "message": "Comment added"}
    else:
        return {"status": "error", "message": "Question ID not found"}


@router.post("/api/like_answer")
def like_answer(
    question_id: str = Body(...),
    like: bool = Body(...)
):
    """Add or update a like/dislike vote for a question. Replaces any previous vote."""
    return add_like_to_question(question_id, like)


@router.get("/api/download_log")
def download_question_log(key: str = Query(...)):
    """Endpoint to download the questions log"""
    if key != os.getenv("ADMIN_ACCESS_KEY"):
        return {"status": "error", "message": "Unauthorized"}
    data = _download_log_from_gcs()
    if not data:
        return {"status": "error", "message": "Log file not found"}
    return JSONResponse(
        content=data,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=question_log.json"}
    )


@router.get("/log_report", response_class=HTMLResponse)
def serve_log_report(request: Request, key: str = Query(...)):
    """Endpoint to display the log report"""
    # Only allow access if key is correct
    if key != os.getenv("ADMIN_ACCESS_KEY"):
        return HTMLResponse(
            "<h3 style='color:red;text-align:center;margin-top:2em'>Unauthorized: Invalid key</h3>", 
            status_code=401
        )
    return templates.TemplateResponse("log_report.html", {"request": request})
