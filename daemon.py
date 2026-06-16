#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Erik Greenwald
"""
Hue Daemon - REST API server for controlling Philips Hue lights
"""
import sys
from flask import Flask, jsonify, request
from hue_client import HueClient
from config import get_bridge_ip, get_api_key, set_bridge_ip, set_api_key
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global client instance
_client = None


def get_client() -> HueClient:
    """Get or create Hue client instance"""
    global _client
    
    bridge_ip = get_bridge_ip()
    api_key = get_api_key()
    
    if not bridge_ip:
        raise ValueError("Bridge IP not configured. Use CLI to configure.")
    
    if not api_key:
        raise ValueError("API key not configured. Use CLI to authenticate.")
    
    if _client is None or _client.bridge_ip != bridge_ip or _client.api_key != api_key:
        _client = HueClient(bridge_ip, api_key)
    
    return _client


@app.errorhandler(ValueError)
def handle_value_error(e):
    return jsonify({"error": str(e)}), 400


@app.errorhandler(ConnectionError)
def handle_connection_error(e):
    return jsonify({"error": str(e)}), 503


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


@app.route("/lights", methods=["GET"])
def list_lights():
    """List all lights"""
    try:
        client = get_client()
        lights = client.get_lights()
        return jsonify(lights)
    except Exception as e:
        logger.error(f"Error listing lights: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/lights/<light_id>", methods=["GET"])
def get_light(light_id):
    """Get specific light state"""
    try:
        client = get_client()
        light = client.get_light(light_id)
        return jsonify(light)
    except Exception as e:
        logger.error(f"Error getting light {light_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/lights/<light_id>/state", methods=["PUT"])
def update_light_state(light_id):
    """Update light state"""
    try:
        client = get_client()
        state = request.get_json()
        
        if not state:
            return jsonify({"error": "No state data provided"}), 400
        
        result = client.set_light_state(light_id, state)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"Error updating light {light_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/lights/<light_id>/on", methods=["PUT"])
def set_light_on(light_id):
    """Turn light on or off"""
    try:
        client = get_client()
        data = request.get_json() or {}
        on = data.get("on", True)
        
        result = client.set_light_on(light_id, on)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"Error setting light {light_id} on/off: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/lights/<light_id>/brightness", methods=["PUT"])
def set_brightness(light_id):
    """Set light brightness"""
    try:
        client = get_client()
        data = request.get_json() or {}
        brightness = data.get("brightness", 128)
        
        result = client.set_light_brightness(light_id, brightness)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"Error setting brightness for light {light_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/config/bridge", methods=["GET", "PUT"])
def config_bridge():
    """Get or set bridge IP"""
    if request.method == "GET":
        bridge_ip = get_bridge_ip()
        return jsonify({"bridge_ip": bridge_ip})
    else:
        data = request.get_json() or {}
        bridge_ip = data.get("bridge_ip")
        if not bridge_ip:
            return jsonify({"error": "bridge_ip required"}), 400
        set_bridge_ip(bridge_ip)
        return jsonify({"success": True, "bridge_ip": bridge_ip})


@app.route("/config/api_key", methods=["GET", "PUT"])
def config_api_key():
    """Get or set API key"""
    if request.method == "GET":
        api_key = get_api_key()
        return jsonify({"api_key": "***" if api_key else None})
    else:
        data = request.get_json() or {}
        api_key = data.get("api_key")
        if not api_key:
            return jsonify({"error": "api_key required"}), 400
        set_api_key(api_key)
        return jsonify({"success": True})


def main():
    """Run the daemon server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hue Daemon - REST API for Philips Hue")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to (default: 8080)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    logger.info(f"Starting Hue daemon on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
