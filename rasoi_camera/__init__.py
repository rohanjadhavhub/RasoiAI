"""
RasoiAI Camera Module — RPi hardware-triggered ingredient scanner.

Public API:
    capture_image()          — capture a JPEG via libcamera-still
    get_latest_image_path()  — path to the most recent capture
    cleanup_gpio()           — release GPIO resources on shutdown
    router                   — FastAPI APIRouter for camera endpoints
"""
from camera_handler import capture_image, get_latest_image_path, cleanup_gpio
from router import router

__all__ = [
    "capture_image",
    "get_latest_image_path",
    "cleanup_gpio",
    "router",
]
