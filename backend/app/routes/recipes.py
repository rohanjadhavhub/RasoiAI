"""
Recipe Routes - Search and Recommendations
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.database import get_database
from app.models import (
    ConfirmIngredientsRequest,
    GetRecommendationsRequest,
    RecipeRecommendations,
    RecipeWithAnalysis,
    UserPreferences
)
from app.services.gap_analysis import analyze_recipe_gaps
from app.services.sql_generator import generate_recipe_query

router = APIRouter()

# Reference to sessions from images module
from app.routes.images import sessions


@router.post("/confirm-ingredients")
async def confirm_ingredients(request: ConfirmIngredientsRequest):
    """
    Confirm detected ingredients and save preferences
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update session with confirmed ingredients and preferences
    sessions[request.session_id]["ingredients"] = request.confirmed_ingredients
    sessions[request.session_id]["preferences"] = request.preferences
    
    return {
        "status": "confirmed",
        "ingredients_count": len(request.confirmed_ingredients),
        "preferences": request.preferences
    }


@router.post("/get-recommendations", response_model=RecipeRecommendations)
async def get_recommendations(request: GetRecommendationsRequest):
    """
    Get recipe recommendations based on confirmed ingredients
    """
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    ingredients = session.get("ingredients", [])
    preferences = session.get("preferences")
    
    if not ingredients:
        raise HTTPException(status_code=400, detail="No ingredients confirmed")
    
    # Get database instance
    db = get_database()
    
    # Search recipes by ingredients
    recipes = db.search_by_ingredients(ingredients, limit=20)
    
    if not recipes:
        return RecipeRecommendations(
            ready_to_cook=[],
            almost_there=[],
            need_shopping=[]
        )
    
    # Analyze each recipe for gaps
    analyzed_recipes = []
    for recipe in recipes:
        gap_result = analyze_recipe_gaps(recipe["ingredients"], ingredients)
        
        analyzed_recipes.append(RecipeWithAnalysis(
            recipe_id=recipe["recipe_id"],
            recipe=recipe["recipe"],
            ingredients=recipe["ingredients"],
            instruction=recipe["instruction"],
            match_score=recipe.get("match_score", 0),
            have=gap_result["have"],
            missing_critical=gap_result["missing_critical"],
            missing_optional=gap_result["missing_optional"],
            readiness=gap_result["readiness"]
        ))
    
    # Sort by readiness and match score
    analyzed_recipes.sort(key=lambda x: (
        0 if x.readiness == "READY" else (1 if x.readiness == "ALMOST_THERE" else 2),
        -x.match_score
    ))
    
    # Group by readiness
    ready = [r for r in analyzed_recipes if r.readiness == "READY"]
    almost = [r for r in analyzed_recipes if r.readiness == "ALMOST_THERE"]
    shopping = [r for r in analyzed_recipes if r.readiness == "NEED_SHOPPING"]
    
    return RecipeRecommendations(
        ready_to_cook=ready[:5],
        almost_there=almost[:3],
        need_shopping=shopping[:2]
    )


@router.get("/recipe/{recipe_id}")
async def get_recipe(recipe_id: int):
    """
    Get detailed recipe by ID
    """
    db = get_database()
    recipe = db.get_recipe_by_id(recipe_id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return recipe


@router.get("/recipes")
async def list_recipes(
    limit: int = Query(default=20, le=100),
    search: Optional[str] = None
):
    """
    List all recipes or search by name/ingredient
    """
    db = get_database()
    
    if search:
        # Search by ingredient
        recipes = db.search_by_ingredients([search], limit=limit)
    else:
        recipes = db.get_all_recipes(limit=limit)
    
    return {
        "count": len(recipes),
        "recipes": recipes
    }


@router.get("/recipes/search")
async def search_recipes(
    ingredients: str = Query(..., description="Comma-separated ingredients"),
    limit: int = Query(default=10, le=50)
):
    """
    Search recipes by multiple ingredients
    """
    ingredient_list = [ing.strip() for ing in ingredients.split(",") if ing.strip()]
    
    if not ingredient_list:
        raise HTTPException(status_code=400, detail="No ingredients provided")
    
    db = get_database()
    recipes = db.search_by_ingredients(ingredient_list, limit=limit)
    
    # Add gap analysis
    results = []
    for recipe in recipes:
        gap_result = analyze_recipe_gaps(recipe["ingredients"], ingredient_list)
        results.append({
            **recipe,
            **gap_result
        })
    
    return {
        "query_ingredients": ingredient_list,
        "count": len(results),
        "recipes": results
    }
