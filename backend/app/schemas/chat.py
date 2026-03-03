"""
Chat-related Pydantic models
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ChatRequest(BaseModel):
    """Chat request"""
    session_id: str
    message: str
    recipe_context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    suggestions: List[str] = []
    response_type: str = "chat"
    updated_recipe: Optional[Dict[str, Any]] = None
