"""
Pydantic Models for API requests and responses
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum


# Enums for preferences
class CuisineType(str, Enum):
    NORTH_INDIAN = "North Indian"
    SOUTH_INDIAN = "South Indian"
    EAST_INDIAN = "East Indian"
    WEST_INDIAN = "West Indian"
    ANY = "Any"


class MealType(str, Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    SNACK = "Snack"


class DietaryType(str, Enum):
    VEGETARIAN = "Vegetarian"
    NON_VEGETARIAN = "Non-Vegetarian"
    VEGAN = "Vegan"
    JAIN = "Jain"


class SpiceLevel(str, Enum):
    MILD = "Mild"
    MEDIUM = "Medium"
    SPICY = "Spicy"


# Ingredient models
class IdentifiedIngredient(BaseModel):
    """Single identified ingredient from vision AI"""
    name: str
    alternate_names: List[str] = []
    category: str
    confidence: float
    quantity_estimate: Optional[str] = None
    notes: Optional[str] = None


class IngredientAnalysisResponse(BaseModel):
    """Response from ingredient analysis"""
    session_id: str
    identified_ingredients: List[IdentifiedIngredient]
    uncertain_items: List[IdentifiedIngredient] = []
    packaged_items: List[IdentifiedIngredient] = []


# Preference models
class UserPreferences(BaseModel):
    """User cooking preferences"""
    cuisine: Optional[CuisineType] = CuisineType.ANY
    time_limit: Optional[int] = 60  # minutes
    meal_type: Optional[MealType] = None
    dietary: Optional[DietaryType] = None
    spice_level: Optional[SpiceLevel] = SpiceLevel.MEDIUM


# Recipe models
class RecipeBase(BaseModel):
    """Base recipe information"""
    recipe_id: int
    recipe: str
    ingredients: str
    instruction: str


class RecipeWithAnalysis(RecipeBase):
    """Recipe with gap analysis"""
    match_score: int
    have: List[str] = []
    missing_critical: List[str] = []
    missing_optional: List[str] = []
    readiness: str  # READY, ALMOST_THERE, NEED_SHOPPING


class RecipeRecommendations(BaseModel):
    """Grouped recipe recommendations"""
    ready_to_cook: List[RecipeWithAnalysis] = []
    almost_there: List[RecipeWithAnalysis] = []
    need_shopping: List[RecipeWithAnalysis] = []


# Request models
class ConfirmIngredientsRequest(BaseModel):
    """Request to confirm ingredients"""
    session_id: str
    confirmed_ingredients: List[str]
    preferences: Optional[UserPreferences] = None


class GetRecommendationsRequest(BaseModel):
    """Request to get recommendations"""
    session_id: str


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


# Session models
class SessionData(BaseModel):
    """Session data storage"""
    session_id: str
    ingredients: List[str] = []
    preferences: Optional[UserPreferences] = None
    selected_recipe: Optional[RecipeBase] = None
    conversation_history: List[Dict[str, str]] = []


# ─── User History Models ──────────────────────────────────


class RecipeActionRequest(BaseModel):
    """Request to add a recipe to favourites or bookmarks"""
    recipe_id: int
    recipe_name: Optional[str] = None


class SavedRecipeResponse(BaseModel):
    """A single saved recipe entry"""
    recipe_id: int
    recipe_name: Optional[str] = None
    created_at: str

