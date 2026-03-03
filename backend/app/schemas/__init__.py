"""
RasoiAI Schemas Package

Re-exports all models for convenience:
    from app.schemas import ChatRequest, RecipeBase, ...
"""

# Enums
from app.schemas.enums import CuisineType, MealType, DietaryType, SpiceLevel

# Ingredient models
from app.schemas.ingredient import IdentifiedIngredient, IngredientAnalysisResponse

# Recipe models
from app.schemas.recipe import RecipeBase, RecipeWithAnalysis, RecipeRecommendations

# Chat models
from app.schemas.chat import ChatRequest, ChatResponse

# Session / preference models
from app.schemas.session import UserPreferences, SessionData

# User action models
from app.schemas.user import (
    ConfirmIngredientsRequest,
    GetRecommendationsRequest,
    RecipeActionRequest,
    SavedRecipeResponse,
)
