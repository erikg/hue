# Philips Hue Control System

A Python-based system for controlling Philips Hue lights with both a REST API daemon and a command-line interface suitable for scripting.

## Features

- **REST API Daemon**: HTTP API for controlling lights programmatically
- **CLI Tool**: Command-line interface designed for scripting and automation
- **Bridge Discovery**: Automatic discovery of Hue Bridge on the network
- **Configuration Management**: Secure storage of bridge IP and API key

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make scripts executable:
```bash
chmod +x cli.py daemon.py
```

## Initial Setup

Run the setup command to discover your bridge and authenticate:

```bash
./cli.py setup
```

This will:
1. Automatically discover your Hue Bridge
2. Prompt you to press the link button on the bridge
3. Create an API key and save it securely

## CLI Usage

The CLI is designed for scripting and automation. All commands support `--json` flag for JSON output.

### List all lights
```bash
./cli.py list
./cli.py list --json  # JSON output
```

### Get light state
```bash
./cli.py get <light_id>
./cli.py get 1 --json
```

### Turn lights on/off
```bash
./cli.py on <light_id> --on
./cli.py on <light_id> --off
```

### Set brightness (0-254)
```bash
./cli.py brightness <light_id> 128
```

### Set color (HSB)
```bash
./cli.py color <light_id> --hue 10000 --sat 254 --bri 200
```

### Set color temperature (153-500 mireds)
```bash
./cli.py colortemp <light_id> 300
```

### Set state from JSON file
```bash
echo '{"on": true, "bri": 200, "hue": 10000}' > state.json
./cli.py set <light_id> state.json
```

### Show configuration
```bash
./cli.py config
```

## REST API Daemon

Start the daemon:
```bash
./daemon.py --host 0.0.0.0 --port 8080
```

### API Endpoints

- `GET /health` - Health check
- `GET /lights` - List all lights
- `GET /lights/<light_id>` - Get light state
- `PUT /lights/<light_id>/state` - Update light state (JSON body)
- `PUT /lights/<light_id>/on` - Turn light on/off (`{"on": true/false}`)
- `PUT /lights/<light_id>/brightness` - Set brightness (`{"brightness": 0-254}`)
- `GET /config/bridge` - Get bridge IP
- `PUT /config/bridge` - Set bridge IP (`{"bridge_ip": "..."}`)
- `GET /config/api_key` - Check if API key is configured
- `PUT /config/api_key` - Set API key (`{"api_key": "..."}`)

### Example API Usage

```bash
# List all lights
curl http://localhost:8080/lights

# Get specific light
curl http://localhost:8080/lights/1

# Turn light on
curl -X PUT http://localhost:8080/lights/1/on -H "Content-Type: application/json" -d '{"on": true}'

# Set brightness
curl -X PUT http://localhost:8080/lights/1/brightness -H "Content-Type: application/json" -d '{"brightness": 200}'

# Set custom state
curl -X PUT http://localhost:8080/lights/1/state -H "Content-Type: application/json" -d '{"on": true, "bri": 254, "hue": 10000, "sat": 254}'
```

## Configuration

Configuration is stored in `~/.hue/config.json` with restrictive permissions (600).

## Scripting Examples

### Bash script to toggle lights
```bash
#!/bin/bash
LIGHT_ID=1
STATE=$(./cli.py get $LIGHT_ID --json | jq -r '.state.on')
if [ "$STATE" = "true" ]; then
    ./cli.py on $LIGHT_ID --off
else
    ./cli.py on $LIGHT_ID --on
fi
```

### Python script using REST API
```python
import requests

BASE_URL = "http://localhost:8080"

# Turn on light 1
response = requests.put(f"{BASE_URL}/lights/1/on", json={"on": True})
print(response.json())

# Set brightness
response = requests.put(f"{BASE_URL}/lights/1/brightness", json={"brightness": 200})
print(response.json())
```

## License

MIT
