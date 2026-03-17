"""
config.py
Agent configuration endpoints for the Bibliosense agent API.
Provides access to agent config for single-agent deployment.
"""
from fastapi import APIRouter, Query
from typing import Optional

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
