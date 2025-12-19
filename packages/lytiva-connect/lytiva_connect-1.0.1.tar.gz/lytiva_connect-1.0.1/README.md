# Lytiva Connect Library

A standalone Python library for interacting with Lytiva smart devices via MQTT. This library handles the protocol logic for Lytiva lights, including dimmers, CCT (Color Temperature), and RGB devices.

## Installation

```bash
pip install lytiva-connect
```

## How to use with MQTT

Lytiva devices communicate via JSON payloads over MQTT. This library helps you generate those payloads and parse the status messages returned by devices.

### 1. Basic Light Control (Dimmer)

To turn on a light and set its brightness:

```python
import json
from lytiva import LytivaDevice

# Initialize device at address 10
device = LytivaDevice(address=10, device_type="dimmer")

# Generate the ON payload with 75% brightness (191 out of 255)
payload_dict = device.get_turn_on_payload(brightness=191)
payload_json = json.dumps(payload_dict)

# Publish payload_json to your MQTT command topic
# Example topic: LYT/{unique_id}/NODE/CONTROL
print(f"Publish to MQTT: {payload_json}")
# Output: {"address": 10, "type": "dimmer", "dimming": 75}
```

### 2. CCT (Color Temperature) Control

```python
device = LytivaDevice(address=20, device_type="cct")

# Set brightness to 100% and temperature to 4000K
payload = device.get_turn_on_payload(brightness=255, kelvin=4000)
# Output: {"address": 20, "type": "cct", "dimming": 100, "color_temperature": 50}
```

### 3. RGB Color Control

```python
device = LytivaDevice(address=30, device_type="rgb")

# Set color to Red (255, 0, 0)
payload = device.get_turn_on_payload(rgb=(255, 0, 0))
# Output: {"address": 30, "type": "rgb", "r": 255, "g": 0, "b": 0, "dimming": 100}
```

### 4. Decoding Status Messages
Lytiva devices return status with nested objects. This library decodes them into simple Python dictionaries:

```python
# Example topic : LYT/{unique_id}/NODE/E/STATUS
# Actual message format:
raw_mqtt_message = '{"address": 10, "type": "cct", "cct": {"dimming": 40, "color_temperature": 100}}'

status = device.decode_status(raw_mqtt_message)
print(status)
# Returns: {'is_on': True, 'brightness': 102, 'kelvin': 6500}
```

## Features
- Scalable payload generation for all Lytiva device types.
- Nested JSON support for robust status decoding.
- Automatic Color Temperature scaling (0-100) and Kelvin conversion.
- Helper functions for Mireds/Kelvin conversion.