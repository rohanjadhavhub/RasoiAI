# RasoiAI Remote Scan — Raspberry Pi Camera Module

Hardware-triggered ingredient scanning for RasoiAI, running on a Raspberry Pi with a 5MP Camera Module Rev 1.3.

## Architecture

```
┌──────────────────────────────────────────────┐
│  Raspberry Pi (rasoi_camera/)                │
│                                              │
│  Button Press → libcamera-still → JPEG       │
│       ↓                                      │
│  Gemini Vision → Ingredient Extraction       │
│       ↓                                      │
│  HTTP POST ingredients ──────────────────────┼──→  Main RasoiAI Backend
│                                              │     POST /api/remote-ingredients
└──────────────────────────────────────────────┘     → sql_generator.py → recipes
```

## Hardware Setup

### Wiring

| Component | Pin         | Note                |
|-----------|-------------|---------------------|
| LED (+)   | BCM GPIO 17 | Via 330 Ω resistor  |
| LED (-)   | GND         | Any GND pin         |
| Camera    | CSI port    | 5MP Camera Rev 1.3  |

### Prerequisites

```bash
# Enable camera
sudo raspi-config   # → Interface Options → Camera → Enable

# Install system packages
sudo apt update
sudo apt install -y libcamera-apps python3-rpi-lgpio

# Install Python dependencies
cd rasoi_camera/
pip install -r requirements.txt
```

### Environment

```bash
cp .env.example .env
# Edit .env with your Gemini API key and main app URL
```

## Running

```bash
# On the Raspberry Pi
cd rasoi_camera/
python main.py
# Server starts at http://0.0.0.0:8001
```
# Http Tunnel

ssh -N -L 8001:localhost:8001 rohanjadhav@raspberrypi.local

## API Endpoints

All endpoints are under `/api/camera/`.

| Method | Endpoint             | Description                                       | Params                                      |
|--------|----------------------|---------------------------------------------------|---------------------------------------------|
| POST   | `/scan`              | Capture image                                     | `width`, `height`, `quality` (query params) |
| GET    | `/status`            | Latest image path & capture dir                   | —                                           |
| GET    | `/latest-image`      | Serve latest JPEG                                 | —                                           |
| POST   | `/analyze`           | Capture + Gemini Vision analysis                  | —                                           |
| POST   | `/scan-and-forward`  | Full pipeline: capture → analyse → get recipes    | `width`, `height`, `quality` (query params) |

### Main App Receiver

| Method | Endpoint                  | Description                                          |
|--------|---------------------------|------------------------------------------------------|
| POST   | `/api/remote-ingredients` | Accepts `{"ingredients": [...]}`, returns recipes     |

## End-to-End Flow

```
1. RPi: POST /api/camera/scan-and-forward
2. RPi: libcamera-still captures JPEG → captures/latest.jpg
3. RPi: Gemini Vision analyses image → ["potato", "onion", "tomato"]
4. RPi: POST /api/remote-ingredients → Main App
5. Main: sql_generator.py → recipe search → gap analysis
6. Main: Returns recipe recommendations → RPi → user
```

## Reading `captures/latest.jpg` from vision.py

The `captures/latest.jpg` symlink always points to the newest capture:

```python
from pathlib import Path
latest = Path("rasoi_camera/captures/latest.jpg")
image_bytes = latest.read_bytes()
```

## File Structure

```
rasoi_camera/
├── __init__.py          # Package re-exports
├── camera_handler.py    # GPIO + libcamera-still capture
├── vision_client.py     # Gemini Vision ingredient extraction
├── forwarder.py         # HTTP POST to main app
├── router.py            # FastAPI endpoints
├── main.py              # Standalone FastAPI app
├── frontend_scan.js     # Browser JS snippet
├── requirements.txt     # pip dependencies
├── .env.example         # Environment template
├── README_remoteScan.md # This file
└── captures/            # Auto-created image directory
    ├── scan_*.jpg
    └── latest.jpg → (symlink to newest)
```
