"""
Agent Management - Single-agent configuration (Nutria)
"""
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.parent


def get_agents():
    """
    Get agent information for single-agent deployment.
    Returns nutria agent info.
    
    Returns:
        Dictionary with agent info
    """
    return {
        "agents": {
            "nutria": {
                "id": "nutria",
                "name": "Nutria",
                "description": "Agent IA nutritionniste",
                "logo": "/static/logos/logo-nutria.png"
            }
        },
        "default": "nutria"
    }


def get_agent_keys():
    """
    Get access keys for single-agent deployment.
    No authentication required for single-agent setup.
    
    Returns:
        Empty dictionary
    """
    return {}


def validate_agent_access(agent_id: str, access_key: str) -> bool:
    """Validate agent access - always True for single-agent setup"""
    return True


def get_agent_by_id(agent_id: str):
    """Get agent configuration by ID"""
    if agent_id == "nutria":
        return {
            "id": "nutria",
            "name": "Nutria",
            "description": "Agent IA nutritionniste",
            "logo": "/static/logos/logo-nutria.png"
        }
    return None
