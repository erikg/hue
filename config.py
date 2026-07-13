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
    # mkdir's mode is ignored when the dir already exists, so tighten explicitly
    os.chmod(CONFIG_DIR, 0o700)


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

    # Write to a temp file in the same dir (created with restrictive
    # permissions from the start, no world-readable window) and atomically
    # swap it into place. This avoids a truncated/corrupt config on a
    # mid-write crash, and re-tightens perms even if CONFIG_FILE already
    # existed with looser permissions (O_CREAT's mode arg is ignored for an
    # existing file, but os.replace() carries the temp file's 0o600 over it).
    tmp_file = str(CONFIG_FILE) + ".tmp"
    fd = os.open(tmp_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(config, f, indent=2)
        os.replace(tmp_file, CONFIG_FILE)
    except Exception:
        try:
            os.remove(tmp_file)
        except OSError:
            pass
        raise


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
