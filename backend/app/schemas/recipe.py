"""
Recipe-related Pydantic models
"""
from pydantic import BaseModel
from typing import List


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
