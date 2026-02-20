"""
Agent Routes - Agent configuration endpoints
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
