"""
RasoiAI Configuration
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "RasoiAI"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database — Neon PostgreSQL (required)
    database_url: str = ""
    
    # Auth0 settings
    auth0_domain: str = ""
    auth0_api_audience: str = ""
    auth0_algorithms: list = ["RS256"]
    
    # Gemini AI
    gemini_api_key: str = ""
    gemini_vision_model: str = "gemini-2.5-flash"
    gemini_text_model: str = "gemini-2.5-flash"
    
    # Upload settings
    max_images: int = 3
    max_image_size_mb: int = 5
    allowed_extensions: set = {"jpg", "jpeg", "png", "heic", "webp"}
    upload_dir: str = "uploads"
    
    # Session settings
    session_expiry_hours: int = 24
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
