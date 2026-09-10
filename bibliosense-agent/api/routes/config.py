"""
config.py
Agent configuration endpoints for the Bibliosense agent API.
Provides access to agent config for single-agent deployment.
"""
import os
from fastapi import APIRouter, Query
from typing import Optional

from api.config import get_config
from api.query_chromadb import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_PROJECT_NAME,
    VECTOR_DB_DIRNAME,
    _get_local_collection,
    _resolve_kb_root,
)

router = APIRouter()


@router.get("/api/get_config")
def get_config_endpoint():
    """
    Get configuration for single-agent deployment.
    
    Returns:
        Configuration dictionary 
    """
    return get_config()


@router.get("/api/debug/db_status")
def debug_db_status(
    key: str = Query(...),
    project_name: Optional[str] = Query(None),
    collection_name: Optional[str] = Query(None),
):
    """Debug endpoint to validate local ChromaDB availability on server."""
    if key != os.getenv("ADMIN_ACCESS_KEY"):
        return {"status": "error", "message": "Unauthorized"}

    project = project_name if isinstance(project_name, str) and project_name.strip() else DEFAULT_PROJECT_NAME
    collection = collection_name if isinstance(collection_name, str) and collection_name.strip() else DEFAULT_COLLECTION_NAME
    kb_root = _resolve_kb_root()
    db_path = kb_root / project / VECTOR_DB_DIRNAME

    payload = {
        "status": "ok",
        "knowledge_base_root": str(kb_root),
        "project_name": project,
        "collection_name": collection,
        "db_path": str(db_path),
        "kb_root_exists": kb_root.exists(),
        "db_path_exists": db_path.exists(),
    }

    try:
        local_collection = _get_local_collection(project, collection)
        payload["collection_count"] = local_collection.count()
    except Exception as e:
        payload["status"] = "error"
        payload["message"] = "Local ChromaDB is not ready"
        payload["details"] = str(e)

    return payload
