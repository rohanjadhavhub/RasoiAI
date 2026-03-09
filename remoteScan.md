You are an expert embedded-systems and Python developer. I am building **RasoiAI**, a smart kitchen assistant running on a Raspberry Pi with a 5MP Camera Module Rev 1.3.

## Project context
- OS: Raspberry Pi OS (Bookworm / 64-bit)
- Web framework: FastAPI (Python 3.11+)
- Camera tool: `libcamera-still` (NOT the deprecated `picamera`)
- GPIO: RPi.GPIO library, BCM numbering
- Flash LED: connected to BCM GPIO 17 via a 330 Ω resistor
- Existing vision pipeline: `vision.py` — already wired to Gemini Vision; it accepts a file path and returns structured analysis
- Feature branch: `remoteScan`

## Task
Implement a hardware-triggered photo-capture system consisting of:

1. **`rasoi_camera/camera_handler.py`** — a pure-Python module that:
   - Sets up GPIO pin 17 as OUTPUT on import
   - Exposes a `capture_image(width, height, quality) -> Path` function that:
     a. Turns the LED ON
     b. Waits 300 ms for illumination
     c. Calls `libcamera-still` via `subprocess.run` with `--nopreview --immediate`
     d. Turns the LED OFF in a `finally` block (so it always extinguishes even on error)
     e. Saves the image to `captures/scan_<YYYYMMDD_HHMMSS>.jpg`
     f. Atomically updates a `captures/latest.jpg` symlink so `vision.py` always finds the newest frame
   - Exposes `get_latest_image_path() -> Path | None`
   - Exposes `cleanup_gpio()` for use on app shutdown
   - Gracefully skips all GPIO calls if `RPi.GPIO` is not importable (non-RPi dev environment)

2. **`rasoi_camera/router.py`** — a FastAPI `APIRouter` with three endpoints:
   - `POST /scan` — triggers capture; query params: `width`, `height`, `quality`; returns `{ success, image_path, message }`
   - `GET /status` — returns `{ latest_image, capture_dir }`
   - `GET /latest-image` — serves the JPEG as a `FileResponse`
   - Raise appropriate `HTTPException` codes (503 if libcamera missing, 500 on runtime error, 404 if no image yet)

3. **`rasoi_camera/__init__.py`** — re-exports the public surface

4. **`main.py`** — shows how to mount the router at `/api/camera` and wire `cleanup_gpio` into FastAPI's lifespan context manager; include a commented example of a `/api/analyze` endpoint that calls `vision.py` after a scan

5. **`frontend_scan.js`** — a plain JS snippet (`triggerRemoteScan()`) that:
   - POSTs to `/api/camera/scan`
   - Loads `/api/camera/latest-image?t=<timestamp>` into an `<img>` tag
   - Shows status text and disables the button during the request

6. **`README_remoteScan.md`** — setup table (apt packages, pip, wiring, raspi-config), API endpoint table with params, and a one-liner showing how `vision.py` reads `captures/latest.jpg`

## Requirements
- All code must be modular, production-clean, and well-commented
- Use Python type hints throughout
- Use `pathlib.Path` for all file operations (no raw strings)
- The `libcamera-still` subprocess must have a hard `timeout=15` seconds
- GPIO setup must happen once at module import via a private `_setup_gpio()` call
- Output files go in a `captures/` directory (auto-created with `mkdir(parents=True, exist_ok=True)`)
- No global mutable state except the GPIO setup flag