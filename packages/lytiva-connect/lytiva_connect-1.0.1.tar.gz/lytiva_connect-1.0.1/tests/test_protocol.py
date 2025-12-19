"""Tests for Lytiva protocol library."""
import json
import pytest
from lytiva import LytivaDevice, mireds_to_kelvin, kelvin_to_mireds

def test_device_on_payload_dimmer():
    """Test dimmer ON payload."""
    device = LytivaDevice(address=10, device_type="dimmer")
    payload = device.get_turn_on_payload(brightness=128)
    # assert "state" not in payload
    assert payload["dimming"] == 50
    assert payload["address"] == 10

def test_device_on_payload_cct():
    """Test CCT ON payload."""
    device = LytivaDevice(address=20, device_type="cct")
    payload = device.get_turn_on_payload(brightness=255, kelvin=3000)
    assert payload["dimming"] == 100
    assert payload["color_temperature"] == 74  # Based on 3000K scaling

def test_device_on_payload_rgb():
    """Test RGB ON payload."""
    device = LytivaDevice(address=30, device_type="rgb")
    payload = device.get_turn_on_payload(rgb=(255, 0, 0))
    assert payload["r"] == 255
    assert "red" not in payload

def test_device_off_payload():
    """Test OFF payload."""
    device = LytivaDevice(address=10, device_type="dimmer")
    payload = device.get_turn_off_payload()
    assert payload["dimming"] == 0

def test_decode_status_dimmer():
    """Test decoding dimmer status."""
    device = LytivaDevice(address=10, device_type="dimmer")
    # Test root level status
    status = device.decode_status('{"address": 10, "type": "dimmer", "dimming": 50}')
    assert status["is_on"] is True
    assert status["brightness"] == 128
    
    # Test nested status
    status = device.decode_status('{"address": 10, "type": "dimmer", "dimmer": {"dimming": 20}}')
    assert status["brightness"] == 51

def test_decode_status_cct():
    """Test decoding CCT status."""
    device = LytivaDevice(address=20, device_type="cct")
    # Test nested payload from user example
    status = device.decode_status('{"address": 20, "type": "cct", "cct": {"dimming": 40, "color_temperature": 100}}')
    assert status["brightness"] == 102
    assert status["kelvin"] == lytiva.mireds_to_kelvin(154) # Coldest
    
def test_decode_status_rgb():
    """Test decoding RGB status."""
    device = LytivaDevice(address=30, device_type="rgb")
    status = device.decode_status('{"address": 30, "type": "rgb", "rgb": {"r": 255, "g": 0, "b": 0}}')
    assert status["rgb_color"] == (255, 0, 0)
    assert status["is_on"] is True
def test_conversion_helpers():
    """Test mireds/kelvin conversions."""
    assert mireds_to_kelvin(370) == 2703
    assert kelvin_to_mireds(2700) == 370
    assert mireds_to_kelvin(None) == 2700
    assert kelvin_to_mireds(None) == 370
