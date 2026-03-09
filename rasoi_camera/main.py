"""
RasoiAI Camera — Standalone FastAPI application for Raspberry Pi.

Run with:
    python main.py
    # or
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload

Environment variables (via .env):
    GEMINI_API_KEY      — Required for vision analysis
    MAIN_APP_URL        — Main RasoiAI backend (default: http://localhost:8000)
    GEMINI_VISION_MODEL — Gemini model name    (default: gemini-2.5-flash)
"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env before any other imports that read env vars
load_dotenv(Path(__file__).parent / ".env")

from camera_handler import cleanup_gpio  # noqa: E402
from router import router                # noqa: E402


# ── Lifespan — startup / shutdown hooks ───────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    print("[rasoi_camera] Starting up — GPIO initialised")
    yield
    # Shutdown
    cleanup_gpio()
    print("[rasoi_camera] Shut down — GPIO cleaned up")


# ── Application ───────────────────────────────────────────────
app = FastAPI(
    title="RasoiAI Camera",
    description="RPi camera module for ingredient scanning",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the main frontend and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "*",  # RPi is on the local network
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount camera router
app.include_router(router, prefix="/api/camera", tags=["Camera"])


@app.get("/")
async def root():
    """Health check."""
    return {
        "name": "RasoiAI Camera",
        "version": "1.0.0",
        "status": "running",
        "main_app": os.getenv("MAIN_APP_URL", "http://localhost:8000"),
    }


# ── Example: Analyse endpoint (commented out) ────────────────
# @app.post("/api/analyze")
# async def analyze_latest():
#     """
#     Analyse the latest captured image by calling vision_client directly.
#     Equivalent to: capture → vision.py → identified ingredients.
#     """
#     from rasoi_camera.vision_client import analyze_image
#     from rasoi_camera.camera_handler import get_latest_image_path
#     path = get_latest_image_path()
#     if path is None:
#         return {"error": "No image captured yet"}
#     result = analyze_image(path)
#     return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
