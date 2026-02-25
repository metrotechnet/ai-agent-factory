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
        print(f"[DEBUG] PROJECT_ROOT: {PROJECT_ROOT}")
        print(f"[DEBUG] KNOWLEDGE_BASE env var: {knowledge_base}")
        
        # Load common config (base configuration)
        common_config_path = PROJECT_ROOT / "knowledge-base" / "common" / "config.json"
        print(f"[DEBUG] Common config path: {common_config_path}")
        print(f"[DEBUG] Common config exists: {common_config_path.exists()}")
        
        common_config = {}
        if common_config_path.exists():
            with open(common_config_path, 'r', encoding='utf-8') as f:
                common_config = json.load(f)
            print(f"[DEBUG] Common config loaded successfully")
        
        # Load agent-specific config (override configuration)
        agent_config_path = PROJECT_ROOT / "knowledge-base" / knowledge_base / "config.json"
        print(f"[DEBUG] Agent config path: {agent_config_path}")
        print(f"[DEBUG] Agent config exists: {agent_config_path.exists()}")
        
        # List files in knowledge-base directory
        kb_dir = PROJECT_ROOT / "knowledge-base"
        if kb_dir.exists():
            print(f"[DEBUG] Contents of knowledge-base directory:")
            for item in kb_dir.iterdir():
                print(f"[DEBUG]   - {item.name} (is_dir: {item.is_dir()})")
                if item.is_dir():
                    try:
                        for subitem in item.iterdir():
                            print(f"[DEBUG]     - {subitem.name}")
                    except Exception as e:
                        print(f"[DEBUG]     Error listing {item.name}: {e}")
        
        if agent_config_path.exists():
            print(f"[DEBUG] Loading agent config from {agent_config_path}")
            with open(agent_config_path, 'r', encoding='utf-8') as f:
                agent_config = json.load(f)
            print(f"[DEBUG] Agent config loaded successfully")
            
            # Merge: common config as base, agent config as override
            merged = deep_merge(common_config, agent_config)
            print(f"[DEBUG] Configs merged successfully")
            return merged
        
        # If agent config doesn't exist but common does, return common
        if common_config:
            print(f"[DEBUG] Agent config not found, returning common config only")
            return common_config
        
        # Provide detailed error with debugging info
        print(f"[DEBUG] No config found, returning error")
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
