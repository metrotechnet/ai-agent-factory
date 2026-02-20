"""
Configuration Management - Configuration loading and merging
"""
from pathlib import Path
import json
from typing import Optional
from api.agents import validate_agent_access, get_agent_by_id


PROJECT_ROOT = Path(__file__).parent.parent


def deep_merge(base_config: dict, override_config: dict) -> dict:
    """
    Deep merge two configuration dictionaries.
    Override values take precedence over base values.
    
    Args:
        base_config: Base configuration dictionary
        override_config: Override configuration dictionary
        
    Returns:
        Merged configuration dictionary
    """
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = deep_merge(result[key], value)
        else:
            # Override value
            result[key] = value
    
    return result


def get_config(agent: Optional[str] = None, access_key: Optional[str] = None):
    """
    Get configuration for single-agent deployment (nutria).
    Returns the nutria agent configuration.
    
    Args:
        agent: Optional agent ID (ignored, always returns nutria)
        access_key: Optional access key (ignored for single-agent setup)
        
    Returns:
        Configuration dictionary for nutria agent
    """
    try:
        # Single-agent setup - always return nutria config
        agent_config_path = PROJECT_ROOT / "knowledge-base" / "agent" / "config.json"
        
        if agent_config_path.exists():
            with open(agent_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {"error": "config not found"}
        
    except FileNotFoundError:
        return {"error": "config not found"}
    except Exception as e:
        return {"error": f"Error loading config: {str(e)}"}
