"""
Agent Routes - Agent configuration endpoints
"""
from fastapi import APIRouter, Query
from typing import Optional
import os
from pathlib import Path

from api.config import get_config

router = APIRouter()


@router.get("/api/get_config")
def get_config_endpoint():
    """
    Get configuration for single-agent deployment.
    
    Returns:
        Configuration dictionary 
    """
    return get_config()


@router.get("/api/debug/list_files")
def list_files_endpoint(path: str = "/app"):
    """
    Debug endpoint to list files in a directory.
    Only works if path exists.
    """
    try:
        target_path = Path(path)
        if not target_path.exists():
            return {"error": f"Path does not exist: {path}"}
        
        files = []
        dirs = []
        
        for item in target_path.iterdir():
            if item.is_file():
                files.append({
                    "name": item.name,
                    "size": item.stat().st_size,
                    "path": str(item)
                })
            elif item.is_dir():
                dirs.append({
                    "name": item.name,
                    "path": str(item)
                })
        
        return {
            "path": str(target_path),
            "exists": True,
            "directories": sorted(dirs, key=lambda x: x["name"]),
            "files": sorted(files, key=lambda x: x["name"])
        }
    except Exception as e:
        return {"error": str(e), "path": path}
