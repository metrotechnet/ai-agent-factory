"""
Update API Routes

This module defines endpoints for triggering the Google Drive document indexing pipeline.
"""
from fastapi import APIRouter, Request, Query
from datetime import datetime


router = APIRouter()
from api.update_gdrive import run_pipeline


@router.post("/update")
def update_pipeline(
    request: Request,
    project_name: str = Query(..., description="Project/knowledge base name to update"),
    collection_name: str = Query(..., description="ChromaDB collection name to update"),
    folder_id: str = Query(..., description="Google Drive folder ID to index"),
):
    """
    Trigger the Google Drive document indexing pipeline.

    This endpoint is typically called by Cloud Scheduler daily at 3 AM.

    Args:
        request (Request): FastAPI request object.
        project_name (str): Project/knowledge base identifier.
        collection_name (str): ChromaDB collection name to update.
        folder_id (str): Google Drive folder ID to index.

    Returns:
        dict: Status and message about the pipeline execution.
    """
    try:
        print(f"[{datetime.now().isoformat()}] Pipeline update triggered for project: {project_name}, collection: {collection_name}, folder: {folder_id}")
        print(f"User-Agent: {request.headers.get('user-agent', 'Unknown')}")
        result = run_pipeline(agent=project_name, collection_name=collection_name, folder_id=folder_id)
        if result.get("error"):
            print(f"\u274c Pipeline error: {result['error']}")
            return {
                "status": "error",
                "message": result['error'],
                "authenticated": result.get("authenticated", False)
            }
        processed = result.get("processed", 0)
        total = result.get("total", 0)
        print(f"\u2705 Pipeline completed for {project_name}/{collection_name}: {processed}/{total} documents processed")
        return {
            "status": "success",
            "message": f"Pipeline executed successfully for {project_name}/{collection_name}",
            "project_name": project_name,
            "collection_name": collection_name,
            "processed": processed,
            "total": total,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"\u274c Pipeline exception: {str(e)}")
        return {
            "status": "error",
            "message": f"Pipeline failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

