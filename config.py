# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Erik Greenwald
"""
Configuration management for Hue CLI/Daemon
"""
import json
import os
from pathlib import Path
from typing import Optional


CONFIG_DIR = Path.home() / ".hue"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir():
    """Ensure config directory exists"""
    CONFIG_DIR.mkdir(exist_ok=True, mode=0o700)


def load_config() -> dict:
    """Load configuration from file"""
    ensure_config_dir()
    
    if not CONFIG_FILE.exists():
        return {}
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config: dict):
    """Save configuration to file"""
    ensure_config_dir()
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Set restrictive permissions
    os.chmod(CONFIG_FILE, 0o600)


def get_bridge_ip() -> Optional[str]:
    """Get configured bridge IP (from env var or config file)"""
    # Check environment variable first
    bridge_ip = os.environ.get("HUE_BRIDGE_IP")
    if bridge_ip:
        return bridge_ip

    # Fall back to config file
    config = load_config()
    return config.get("bridge_ip")


def set_bridge_ip(bridge_ip: str):
    """Set bridge IP in config"""
    config = load_config()
    config["bridge_ip"] = bridge_ip
    save_config(config)


def get_api_key() -> Optional[str]:
    """Get configured API key (from env var or config file)"""
    # Check environment variable first
    api_key = os.environ.get("HUE_API_KEY")
    if api_key:
        return api_key

    # Fall back to config file
    config = load_config()
    return config.get("api_key")


def set_api_key(api_key: str):
    """Set API key in config"""
    config = load_config()
    config["api_key"] = api_key
    save_config(config)
