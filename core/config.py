"""Configuration loader for TOML files."""

import tomllib
from pathlib import Path
from typing import Any, Dict
from core.settings import settings


def load_toml_config(config_path: str = "config/config.toml") -> Dict[str, Any]:
    """
    Load configuration from TOML file.
    
    Args:
        config_path: Path to the TOML configuration file
        
    Returns:
        Dictionary containing configuration values
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        return {}
    
    with open(config_file, "rb") as f:
        return tomllib.load(f)


def get_config() -> Dict[str, Any]:
    """
    Get merged configuration from TOML and environment variables.
    Environment variables take precedence over TOML values.
    
    Returns:
        Merged configuration dictionary
    """
    toml_config = load_toml_config()
    
    # Merge with settings (environment variables take precedence)
    config = {
        "app": {
            "name": toml_config.get("app", {}).get("name", "Interview API"),
            "version": toml_config.get("app", {}).get("version", "0.1.0"),
            "debug": settings.debug,
        },
        "api": {
            "prefix": settings.api_v1_prefix,
            "title": toml_config.get("api", {}).get("title", "Interview API"),
            "description": toml_config.get("api", {}).get("description", ""),
        },
        "database": {
            "url": settings.database_url,
            "pool_size": toml_config.get("database", {}).get("pool_size", 5),
            "max_overflow": toml_config.get("database", {}).get("max_overflow", 10),
            "pool_timeout": toml_config.get("database", {}).get("pool_timeout", 30),
            "echo": toml_config.get("database", {}).get("echo", False),
        },
        "logging": {
            "level": settings.log_level,
            "format": toml_config.get("logging", {}).get("format", "json"),
        },
        "semantic_kernel": {
            "api_key": settings.semantic_kernel_api_key,
            "endpoint": settings.semantic_kernel_endpoint,
            "model": settings.semantic_kernel_model,
            "temperature": toml_config.get("semantic_kernel", {}).get("temperature", 0.7),
            "max_tokens": toml_config.get("semantic_kernel", {}).get("max_tokens", 2000),
        },
    }
    
    return config

