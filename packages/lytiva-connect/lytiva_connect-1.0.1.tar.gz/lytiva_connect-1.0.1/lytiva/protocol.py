"""Core protocol logic for Lytiva devices."""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

class LytivaDevice:
    """Represents a Lytiva device and its protocol logic."""

    def __init__(
        self, 
        address: str | int, 
        device_type: str = "dimmer",
        min_mireds: int = 154,
        max_mireds: int = 370
    ) -> None:
        """Initialize the device."""
        try:
            self.address = int(address)
        except (ValueError, TypeError):
            self.address = str(address)
            
        self.device_type = device_type
        self.version = "v1.0"
        self.min_mireds = min_mireds
        self.max_mireds = max_mireds

    def get_turn_on_payload(
        self, 
        brightness: Optional[int] = None, 
        kelvin: Optional[int] = None, 
        rgb: Optional[tuple[int, int, int]] = None
    ) -> Dict[str, Any]:
        """Generate payload to turn the light on."""
        payload = {
            "version": self.version,
            "type": self.device_type,
            "address": self.address,
        }

        # Brightness (dimming 0-100)
        if brightness is not None:
            payload["dimming"] = int(brightness * 100 / 255)
        elif self.device_type in ("dimmer", "cct"):
            payload["dimming"] = 100  # Default to max if turning on

        # CCT
        if self.device_type == "cct" and kelvin is not None:
            mired = kelvin_to_mireds(kelvin)
            mired = max(min(mired, self.max_mireds), self.min_mireds)
            
            range_mireds = max(1, (self.max_mireds - self.min_mireds))
            ct_percent = int((mired - self.min_mireds) * 100 / range_mireds)
            ct_scaled = 100 - ct_percent
            payload["color_temperature"] = ct_scaled

        # RGB
        if self.device_type == "rgb" and rgb is not None:
            r, g, b = rgb
            payload.update({"r": r, "g": g, "b": b})

        return payload

    def get_turn_off_payload(self) -> Dict[str, Any]:
        """Generate payload to turn the light off."""
        payload = {
            "version": self.version,
            "type": self.device_type,
            "address": self.address,
            "dimming": 0
        }
        
        if self.device_type == "rgb":
            payload.update({"r": 0, "g": 0, "b": 0})
            
        return payload

    def decode_status(self, payload_str: str) -> Dict[str, Any]:
        """Decode a status payload string into a standardized dictionary."""
        try:
            if isinstance(payload_str, dict):
                payload = payload_str
            else:
                payload = json.loads(payload_str)
        except (ValueError, TypeError):
            return {}

        if str(payload.get("address")) != str(self.address):
            return {}

        dtype = payload.get("type") or self.device_type
        result = {}
        
        # Helper for nested or flat data
        def get_val(key):
            nested = payload.get(dtype)
            if isinstance(nested, dict) and (val := nested.get(key)) is not None:
                return val
            return payload.get(key)

        # Brightness / Dimming
        if (d := get_val("dimming")) is not None:
            result["brightness"] = round(d * 255 / 100)
            result["is_on"] = d > 0
        else:
            # Check state if dimming not present
            state = payload.get("state")
            if state is not None:
                result["is_on"] = (state in ("ON", "on", True, 1))

        # CCT
        if dtype == "cct":
            ct = get_val("color_temperature")
            kelvin = get_val("kelvin")
            
            if kelvin is not None:
                result["kelvin"] = int(kelvin)
            elif ct is not None:
                ct_inverted = 100 - ct
                mired = self.min_mireds + (ct_inverted * (self.max_mireds - self.min_mireds) / 100)
                result["kelvin"] = mireds_to_kelvin(int(mired))

        # RGB
        if dtype == "rgb":
            rgb_data = payload.get("rgb") or payload
            r = rgb_data.get("r") if rgb_data.get("r") is not None else rgb_data.get("red")
            g = rgb_data.get("g") if rgb_data.get("g") is not None else rgb_data.get("green")
            b = rgb_data.get("b") if rgb_data.get("b") is not None else rgb_data.get("blue")
            
            if all(v is not None for v in (r, g, b)):
                result["rgb_color"] = (r, g, b)
                if "is_on" not in result:
                    result["is_on"] = any((r, g, b))

        return result

def mireds_to_kelvin(mireds: Optional[int | str]) -> int:
    """Convert mireds to kelvin with Lytiva defaults."""
    try:
        if mireds is None or str(mireds) == "None":
            return 2700
        m = int(float(mireds))
        if m <= 0: return 2700
        return round(1000000 / m)
    except (ValueError, TypeError):
        return 2700

def kelvin_to_mireds(kelvin: Optional[int | str]) -> int:
    """Convert kelvin to mireds with Lytiva defaults."""
    try:
        if kelvin is None or str(kelvin) == "None":
            return 370
        k = int(float(kelvin))
        if k <= 0: return 370
        return round(1000000 / k)
    except (ValueError, TypeError):
        return 370
