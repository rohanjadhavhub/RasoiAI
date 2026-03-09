"""
RasoiAI - FastAPI Main Application
Indian Recipe Recommendation System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import get_settings
from app.routes import images, recipes, chat, auth, user_history, remote_scan

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Intelligent Indian Recipe Recommendation System",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
uploads_dir = Path(settings.upload_dir)
uploads_dir.mkdir(exist_ok=True)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Include routers
app.include_router(images.router, prefix="/api", tags=["Images"])
app.include_router(recipes.router, prefix="/api", tags=["Recipes"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(user_history.router, prefix="/api", tags=["User History"])
app.include_router(remote_scan.router, prefix="/api", tags=["Remote Scan"])


# ── LangGraph Checkpointer Lifecycle ─────────────────────────

@app.on_event("startup")
async def startup_langgraph():
    """Initialise LangGraph PostgreSQL checkpointer on app startup."""
    try:
        from app.services.chat_graph import init_checkpointer
        await init_checkpointer()
    except Exception as e:
        print(f"[Startup] LangGraph checkpointer init failed: {e}")
        print("[Startup] Chat will fall back to stateless mode.")


@app.on_event("shutdown")
async def shutdown_langgraph():
    """Close LangGraph connection pool on app shutdown."""
    try:
        from app.services.chat_graph import close_checkpointer
        await close_checkpointer()
    except Exception as e:
        print(f"[Shutdown] LangGraph cleanup error: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/db-test")
async def db_test():
    """Test PostgreSQL (Neon) connectivity."""
    from app.db import get_database
    try:
        db = get_database()
        count = db.get_recipe_count()
        return {"status": "connected", "recipe_count": count}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
