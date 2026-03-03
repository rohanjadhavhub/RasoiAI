"""
Session and preference Pydantic models
"""
from pydantic import BaseModel
from typing import List, Optional, Dict

from app.schemas.enums import CuisineType, MealType, DietaryType, SpiceLevel
from app.schemas.recipe import RecipeBase


class UserPreferences(BaseModel):
    """User cooking preferences"""
    cuisine: Optional[CuisineType] = CuisineType.ANY
    time_limit: Optional[int] = 60  # minutes
    meal_type: Optional[MealType] = None
    dietary: Optional[DietaryType] = None
    spice_level: Optional[SpiceLevel] = SpiceLevel.MEDIUM


class SessionData(BaseModel):
    """Session data storage"""
    session_id: str
    ingredients: List[str] = []
    preferences: Optional[UserPreferences] = None
    selected_recipe: Optional[RecipeBase] = None
    conversation_history: List[Dict[str, str]] = []
