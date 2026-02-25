"""
Configuration Management - Configuration loading and merging
"""
from pathlib import Path
import json
import os
from typing import Optional


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


def get_config():
    """
    Get configuration for single-agent deployment.
    Merges common config with agent-specific config.
    Agent config takes precedence over common config.
    
    Returns:
        Configuration dictionary for agent
    """
    try:
        # Get knowledge base from environment variable or use default
        knowledge_base = os.getenv("KNOWLEDGE_BASE", "agent")
        
        # Load common config (base configuration)
        common_config_path = PROJECT_ROOT / "knowledge-base" / "common" / "config.json"
        common_config = {}
        if common_config_path.exists():
            with open(common_config_path, 'r', encoding='utf-8') as f:
                common_config = json.load(f)
        
        # Load agent-specific config (override configuration)
        agent_config_path = PROJECT_ROOT / "knowledge-base" / knowledge_base / "config.json"
        
        if agent_config_path.exists():
            with open(agent_config_path, 'r', encoding='utf-8') as f:
                agent_config = json.load(f)
            
            # Merge: common config as base, agent config as override
            return deep_merge(common_config, agent_config)
        
        # If agent config doesn't exist but common does, return common
        if common_config:
            return common_config
        
        # Provide detailed error with debugging info
        kb_dir = PROJECT_ROOT / "knowledge-base"
        available_kbs = []
        if kb_dir.exists():
            available_kbs = [d.name for d in kb_dir.iterdir() if d.is_dir()]
        
        return {
            "error": f"config not found at {agent_config_path}",
            "debug": {
                "project_root": str(PROJECT_ROOT),
                "knowledge_base": knowledge_base,
                "config_path": str(agent_config_path),
                "common_config_path": str(common_config_path),
                "kb_dir_exists": kb_dir.exists(),
                "available_knowledge_bases": available_kbs
            }
        }
        
    except FileNotFoundError:
        knowledge_base = os.getenv("KNOWLEDGE_BASE", "agent")
        agent_config_path = PROJECT_ROOT / "knowledge-base" / knowledge_base / "config.json"
        return {
            "error": f"config not found at {agent_config_path}",
            "debug": {"knowledge_base": knowledge_base}
        }
    except Exception as e:
        knowledge_base = os.getenv("KNOWLEDGE_BASE", "agent")
        agent_config_path = PROJECT_ROOT / "knowledge-base" / knowledge_base / "config.json"
        return {
            "error": f"Error loading config from {agent_config_path}: {str(e)}",
            "debug": {"knowledge_base": knowledge_base}
        }
