"""
Ingredient-related Pydantic models
"""
from pydantic import BaseModel
from typing import List, Optional


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
