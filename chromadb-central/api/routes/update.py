"""
Update API Routes

This module defines endpoints for triggering the Google Drive document indexing pipeline.
"""
from fastapi import APIRouter, Request, Query
from datetime import datetime


router = APIRouter()
from api.update_chromadb import run_update_pipeline


@router.post("/update")
def update_pipeline(
    request: Request,
    project_name: str = Query(..., description="Project/knowledge base name to update"),
    collection_name: str = Query(..., description="ChromaDB collection name to update"),
    folder_id: str = Query(..., description="Google Drive folder ID to index"),
):
    """
    Trigger the Google Drive document indexing pipeline.

    Downloads all files from the GDrive folder, extracts text, generates
    transcripts_chromadb.json, then runs the project's index_chromadb_json.py
    to rebuild the ChromaDB collection.

    This endpoint is typically called by Cloud Scheduler daily at 3 AM.
    """
    try:
        print(f"[{datetime.now().isoformat()}] Pipeline update triggered for project: {project_name}, collection: {collection_name}, folder: {folder_id}")
        print(f"User-Agent: {request.headers.get('user-agent', 'Unknown')}")
        result = run_update_pipeline(project_name=project_name, collection_name=collection_name, folder_id=folder_id)
        if result.get("error"):
            print(f"❌ Pipeline error: {result['error']}")
            return {
                "status": "error",
                "message": result['error'],
                "authenticated": result.get("authenticated", False)
            }
        print(f"✅ Pipeline completed for {project_name}: downloaded={result.get('downloaded')}, extracted={result.get('extracted')}, indexed={result.get('indexed')}")
        return {
            "status": "success",
            "message": f"Pipeline executed successfully for {project_name}",
            "project_name": project_name,
            "downloaded": result.get("downloaded", 0),
            "extracted": result.get("extracted", 0),
            "indexed": result.get("indexed", False),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Pipeline exception: {str(e)}")
        return {
            "status": "error",
            "message": f"Pipeline failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

