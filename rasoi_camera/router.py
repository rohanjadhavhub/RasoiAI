"""
Camera API Router — FastAPI endpoints for the RPi camera module.

Provides scan, status, image serving, analysis, and full scan-and-forward.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from camera_handler import capture_image, get_latest_image_path, CAPTURE_DIR
from vision_client import analyze_image, extract_ingredient_names
from forwarder import forward_ingredients

router = APIRouter()


@router.post("/scan")
async def scan(
    width: int = Query(default=2592, ge=320, le=4056, description="Image width"),
    height: int = Query(default=1944, ge=240, le=3040, description="Image height"),
    quality: int = Query(default=85, ge=1, le=100, description="JPEG quality"),
):
    """
    Trigger a camera capture with optional resolution/quality params.

    Returns the path to the saved image.
    """
    try:
        image_path = capture_image(width=width, height=height, quality=quality)
        return {
            "success": True,
            "image_path": str(image_path),
            "message": f"Image captured: {image_path.name}",
        }
    except RuntimeError as exc:
        # libcamera-still missing → 503; other runtime errors → 500
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=503, detail=str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/status")
async def status():
    """Return current capture status and directory info."""
    latest = get_latest_image_path()
    return {
        "latest_image": str(latest) if latest else None,
        "capture_dir": str(CAPTURE_DIR.resolve()),
    }


@router.get("/latest-image")
async def latest_image():
    """Serve the most recent JPEG capture as a file download."""
    latest = get_latest_image_path()
    if latest is None or not latest.exists():
        raise HTTPException(status_code=404, detail="No image captured yet")
    return FileResponse(
        path=str(latest),
        media_type="image/jpeg",
        filename=latest.name,
    )


@router.post("/analyze")
async def analyze():
    """
    Analyse the latest captured image using Gemini Vision.

    Returns identified ingredients with confidence scores.
    """
    latest = get_latest_image_path()
    if latest is None or not latest.exists():
        raise HTTPException(
            status_code=404,
            detail="No image captured yet. Call /scan first.",
        )

    try:
        analysis = analyze_image(latest)
        ingredient_names = extract_ingredient_names(analysis)
        return {
            "success": True,
            "analysis": analysis,
            "ingredient_names": ingredient_names,
        }
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/scan-and-forward")
async def scan_and_forward(
    width: int = Query(default=2592, ge=320, le=4056),
    height: int = Query(default=1944, ge=240, le=3040),
    quality: int = Query(default=85, ge=1, le=100),
):
    """
    Full pipeline: Capture → Analyse → Forward to main app.

    1. Captures an image via libcamera-still
    2. Sends image to Gemini Vision for ingredient extraction
    3. Forwards ingredient list to main RasoiAI backend
    4. Returns recipe recommendations

    This is the one-button endpoint for end-to-end operation.
    """
    # ── Step 1: Capture ──────────────────────────────────────
    try:
        image_path = capture_image(width=width, height=height, quality=quality)
    except RuntimeError as exc:
        if "not found" in str(exc).lower():
            raise HTTPException(status_code=503, detail=str(exc))
        raise HTTPException(status_code=500, detail=f"Capture failed: {exc}")

    # ── Step 2: Analyse ──────────────────────────────────────
    try:
        analysis = analyze_image(image_path)
        ingredient_names = extract_ingredient_names(analysis)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    if not ingredient_names:
        raise HTTPException(
            status_code=422,
            detail="No ingredients detected in the image.",
        )

    # ── Step 3: Forward to main app ──────────────────────────
    try:
        recipes = await forward_ingredients(ingredient_names)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to reach main app: {exc}",
        )

    return {
        "success": True,
        "image_path": str(image_path),
        "ingredients_detected": ingredient_names,
        "analysis_details": analysis,
        "recipes": recipes,
    }
