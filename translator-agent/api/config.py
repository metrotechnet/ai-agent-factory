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
        #Print all config files for debugging
        config_dir = PROJECT_ROOT / "config"
        if config_dir.exists():
            print(f"Config directory contents: {[d.name for d in config_dir.iterdir()]}")
        else:
            print(f"Config directory not found at {config_dir}")

        # Load common config (base configuration)
        common_config_path = PROJECT_ROOT / "config" / "common_config.json"
        common_config = {}
        if common_config_path.exists():
            with open(common_config_path, 'r', encoding='utf-8') as f:
                common_config = json.load(f)
        
        # Load agent-specific config (override configuration)
        agent_config_path = PROJECT_ROOT / "config" / "agent_config.json"
        
        if agent_config_path.exists():
            with open(agent_config_path, 'r', encoding='utf-8') as f:
                agent_config = json.load(f)
            
            # Merge: common config as base, agent config as override
            return deep_merge(common_config, agent_config)
        
        # If agent config doesn't exist but common does, return common
        if common_config:
            return common_config
        
        # Provide detailed error with debugging info
        config_dir = PROJECT_ROOT / "config"
        available_configs = []
        if config_dir.exists():
            available_configs = [d.name for d in config_dir.iterdir() if d.is_dir()]
        
        return {
            "error": f"config not found at {agent_config_path}",
            "debug": {
                "project_root": str(PROJECT_ROOT),
                "config_path": str(agent_config_path),
                "is_config_path": "found" if config_dir.exists() else "not found",
                "available_configs": available_configs
            }
        }
        
    except FileNotFoundError:
        agent_config_path = PROJECT_ROOT / "config" / "agent_config.json"
        return {
            "error": f"config not found at {agent_config_path}",
            "debug": {"knowledge_base": "agent"}
        }
    except Exception as e:
        agent_config_path = PROJECT_ROOT /  "config" / "agent_config.json"
        return {
            "error": f"Error loading config from {agent_config_path}: {str(e)}",
            "debug": {"knowledge_base": "agent"}
        }
