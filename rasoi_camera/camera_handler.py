"""
Camera Handler — GPIO-controlled image capture via libcamera-still / rpicam-still.

Designed for Raspberry Pi with 5MP Camera Module Rev 1.3.
Gracefully degrades on non-RPi dev environments (GPIO calls are skipped).
"""
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Capture output directory ──────────────────────────────────
CAPTURE_DIR = Path(__file__).parent / "captures"
CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

# ── Camera command auto-detection ─────────────────────────────
# Bookworm renamed libcamera-still → rpicam-still
_CAPTURE_CMD = shutil.which("rpicam-still") or shutil.which("libcamera-still")

# ── GPIO Configuration ────────────────────────────────────────
LED_PIN = 17          # BCM numbering — flash LED via 330 Ω resistor
_gpio_available = False
_gpio_setup_done = False


def _setup_gpio() -> None:
    """Initialise GPIO pin 17 as OUTPUT. Called once at module import."""
    global _gpio_available, _gpio_setup_done, GPIO

    if _gpio_setup_done:
        return

    try:
        import RPi.GPIO as _GPIO  # type: ignore[import-untyped]
        GPIO = _GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)
        _gpio_available = True
    except (ImportError, RuntimeError):
        # Not running on a Raspberry Pi — skip GPIO entirely
        _gpio_available = False
    finally:
        _gpio_setup_done = True


# Run setup on import
_setup_gpio()


def capture_image(
    width: int = 2592,
    height: int = 1944,
    quality: int = 85,
) -> Path:
    """
    Capture a JPEG image using rpicam-still (Bookworm) or libcamera-still.

    Sequence:
        1. Turn flash LED ON
        2. Wait 300 ms for illumination to stabilise
        3. Run capture command (hard timeout 15 s)
        4. Turn flash LED OFF (always, even on error)
        5. Create/update ``captures/latest.jpg`` symlink

    Args:
        width:   Image width in pixels  (default: full 5MP width)
        height:  Image height in pixels  (default: full 5MP height)
        quality: JPEG quality 1-100      (default: 85)

    Returns:
        Path to the saved JPEG file.

    Raises:
        RuntimeError: If no camera command is found or the capture fails.
    """
    if _CAPTURE_CMD is None:
        raise RuntimeError(
            "Neither rpicam-still nor libcamera-still found. "
            "Install with: sudo apt install rpicam-apps  (or libcamera-apps on Bullseye)"
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = CAPTURE_DIR / f"scan_{timestamp}.jpg"

    try:
        # 1. LED ON
        if _gpio_available:
            GPIO.output(LED_PIN, GPIO.HIGH)

        # 2. Stabilisation delay
        time.sleep(0.3)

        # 3. Capture
        cmd = [
            _CAPTURE_CMD,
            "--nopreview",
            "--immediate",
            "--width", str(width),
            "--height", str(height),
            "--quality", str(quality),
            "-o", str(output_path),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"{_CAPTURE_CMD} failed (exit {result.returncode}): {result.stderr}"
            )
    finally:
        # 4. LED OFF — always
        if _gpio_available:
            GPIO.output(LED_PIN, GPIO.LOW)

    # 5. Atomically update the latest.jpg symlink
    latest_link = CAPTURE_DIR / "latest.jpg"
    latest_link.unlink(missing_ok=True)
    latest_link.symlink_to(output_path.name)

    return output_path


def get_latest_image_path() -> Optional[Path]:
    """
    Return the path pointed to by ``captures/latest.jpg``, or None if
    no capture has been taken yet.
    """
    latest_link = CAPTURE_DIR / "latest.jpg"
    if latest_link.exists():
        # Resolve the symlink to an absolute path
        return latest_link.resolve()
    return None


def cleanup_gpio() -> None:
    """Release GPIO resources. Call on application shutdown."""
    if _gpio_available:
        GPIO.cleanup()
