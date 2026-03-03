"""
User action Pydantic models (requests, favourites, bookmarks)
"""
from pydantic import BaseModel
from typing import List, Optional

from app.schemas.session import UserPreferences


class ConfirmIngredientsRequest(BaseModel):
    """Request to confirm ingredients"""
    session_id: str
    confirmed_ingredients: List[str]
    preferences: Optional[UserPreferences] = None


class GetRecommendationsRequest(BaseModel):
    """Request to get recommendations"""
    session_id: str


class RecipeActionRequest(BaseModel):
    """Request to add a recipe to favourites or bookmarks"""
    recipe_id: int
    recipe_name: Optional[str] = None


class SavedRecipeResponse(BaseModel):
    """A single saved recipe entry"""
    recipe_id: int
    recipe_name: Optional[str] = None
    created_at: str
