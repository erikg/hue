# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Erik Greenwald
"""
Philips Hue API Client Library
Handles communication with the Hue Bridge
"""
import requests
import json
from typing import Dict, List, Optional, Any


class HueClient:
    """Client for interacting with Philips Hue Bridge"""
    
    def __init__(self, bridge_ip: str, api_key: Optional[str] = None):
        """
        Initialize Hue client
        
        Args:
            bridge_ip: IP address of the Hue Bridge
            api_key: API key for authentication (optional, can be set later)
        """
        self.bridge_ip = bridge_ip
        self.api_key = api_key
        self.base_url = f"http://{bridge_ip}/api"
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to Hue Bridge
        
        Args:
            method: HTTP method (GET, PUT, POST)
            endpoint: API endpoint (without /api prefix)
            data: Optional request body
            
        Returns:
            Response JSON as dictionary
        """
        url = f"{self.base_url}/{self.api_key}/{endpoint}" if self.api_key else f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=5)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=5)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Hue Bridge: {e}")
    
    def create_user(self, device_type: str = "hue-cli") -> str:
        """
        Create a new API user (first-time setup)
        
        Args:
            device_type: Device type identifier
            
        Returns:
            API key (username)
        """
        data = {"devicetype": device_type}
        response = self._request("POST", "", data=data)
        
        if isinstance(response, list) and len(response) > 0:
            if "error" in response[0]:
                error = response[0]["error"]
                if error.get("type") == 101:
                    raise ValueError("Link button not pressed. Please press the link button on the bridge and try again.")
                raise ValueError(f"Hue Bridge error: {error.get('description', 'Unknown error')}")
            elif "success" in response[0]:
                return response[0]["success"]["username"]
        
        raise ValueError("Unexpected response from Hue Bridge")
    
    def get_lights(self) -> Dict[str, Dict]:
        """
        Get all lights
        
        Returns:
            Dictionary mapping light IDs to light data
        """
        return self._request("GET", "lights")
    
    def get_light(self, light_id: str) -> Dict:
        """
        Get specific light state
        
        Args:
            light_id: Light ID
            
        Returns:
            Light data dictionary
        """
        return self._request("GET", f"lights/{light_id}")
    
    def set_light_state(self, light_id: str, state: Dict[str, Any]) -> List[Dict]:
        """
        Update light state
        
        Args:
            light_id: Light ID
            state: State dictionary with keys like 'on', 'bri', 'hue', 'sat', 'xy', 'ct', etc.
            
        Returns:
            Response from bridge
        """
        return self._request("PUT", f"lights/{light_id}/state", data=state)
    
    def set_light_on(self, light_id: str, on: bool = True) -> List[Dict]:
        """Turn light on or off"""
        return self.set_light_state(light_id, {"on": on})
    
    def set_light_brightness(self, light_id: str, brightness: int) -> List[Dict]:
        """
        Set light brightness
        
        Args:
            light_id: Light ID
            brightness: Brightness value (0-254)
        """
        return self.set_light_state(light_id, {"bri": max(0, min(254, brightness))})
    
    def set_light_color(self, light_id: str, hue: Optional[int] = None, 
                       saturation: Optional[int] = None, 
                       brightness: Optional[int] = None) -> List[Dict]:
        """
        Set light color using HSB
        
        Args:
            light_id: Light ID
            hue: Hue value (0-65535)
            saturation: Saturation value (0-254)
            brightness: Brightness value (0-254)
        """
        state = {}
        if hue is not None:
            state["hue"] = max(0, min(65535, hue))
        if saturation is not None:
            state["sat"] = max(0, min(254, saturation))
        if brightness is not None:
            state["bri"] = max(0, min(254, brightness))
        
        return self.set_light_state(light_id, state)
    
    def set_light_color_temp(self, light_id: str, ct: int) -> List[Dict]:
        """
        Set light color temperature
        
        Args:
            light_id: Light ID
            ct: Color temperature in mireds (153-500, lower is cooler)
        """
        return self.set_light_state(light_id, {"ct": max(153, min(500, ct))})


def discover_bridge() -> Optional[str]:
    """
    Discover Hue Bridge on the network using meethue.com API
    
    Returns:
        Bridge IP address or None if not found
    """
    try:
        response = requests.get("https://discovery.meethue.com", timeout=5)
        response.raise_for_status()
        bridges = response.json()
        
        if bridges and len(bridges) > 0:
            return bridges[0].get("internalipaddress")
    except requests.exceptions.RequestException:
        pass
    
    return None
