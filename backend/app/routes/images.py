"""
Image Upload and Analysis Routes
"""
import uuid
import base64
from pathlib import Path
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image
import io

from app.config import get_settings
from app.models import IngredientAnalysisResponse, IdentifiedIngredient
from app.services.vision import analyze_ingredients_from_images

router = APIRouter()
settings = get_settings()

# Simple in-memory session storage (use Redis in production)
sessions = {}


@router.post("/upload-images")
async def upload_images(files: List[UploadFile] = File(...)):
    """
    Upload 2-3 ingredient images for analysis
    """
    # Validate number of files
    if len(files) < 1:
        raise HTTPException(status_code=400, detail="At least 1 image is required")
    if len(files) > settings.max_images:
        raise HTTPException(
            status_code=400, 
            detail=f"Maximum {settings.max_images} images allowed"
        )
    
    # Create session
    session_id = str(uuid.uuid4())
    
    # Process and save images
    saved_paths = []
    image_data_list = []
    
    for file in files:
        # Validate file extension
        ext = file.filename.split(".")[-1].lower()
        if ext not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {ext}. Allowed: {settings.allowed_extensions}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        file_size_mb = len(content) / (1024 * 1024)
        if file_size_mb > settings.max_image_size_mb:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file_size_mb:.1f}MB. Max: {settings.max_image_size_mb}MB"
            )
        
        # Save file
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(exist_ok=True)
        
        filename = f"{session_id}_{file.filename}"
        filepath = upload_dir / filename
        
        with open(filepath, "wb") as f:
            f.write(content)
        
        saved_paths.append(str(filepath))
        image_data_list.append(content)
    
    # Store session data
    sessions[session_id] = {
        "image_paths": saved_paths,
        "image_data": image_data_list,
        "ingredients": [],
        "preferences": None
    }
    
    return {
        "session_id": session_id,
        "uploaded_count": len(saved_paths),
        "message": "Images uploaded successfully. Call /api/analyze-ingredients to process."
    }


@router.post("/analyze-ingredients", response_model=IngredientAnalysisResponse)
async def analyze_ingredients(session_id: str):
    """
    Analyze uploaded images to identify ingredients using Vision AI
    """
    # Check session exists
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    image_data = session.get("image_data", [])
    
    if not image_data:
        raise HTTPException(status_code=400, detail="No images found in session")
    
    try:
        # Call Vision AI service
        result = await analyze_ingredients_from_images(image_data)
        
        # Store identified ingredients in session
        all_ingredients = [ing.name for ing in result.get("identified_ingredients", [])]
        sessions[session_id]["ingredients"] = all_ingredients
        
        return IngredientAnalysisResponse(
            session_id=session_id,
            identified_ingredients=result.get("identified_ingredients", []),
            uncertain_items=result.get("uncertain_items", []),
            packaged_items=result.get("packaged_items", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision AI error: {str(e)}")


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session data"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "ingredients": session.get("ingredients", []),
        "preferences": session.get("preferences"),
        "has_images": len(session.get("image_paths", [])) > 0
    }
