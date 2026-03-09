"""
Remote Scan Routes — Receive ingredients from RPi camera module.

The RPi runs Gemini Vision locally to extract ingredients, then POSTs
the ingredient list here for recipe lookup via sql_generator.py.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import get_database
from app.services.sql_generator import generate_recipe_query
from app.services.gap_analysis import analyze_recipe_gaps

router = APIRouter()


class RemoteIngredientsRequest(BaseModel):
    """Payload from the RPi camera module."""
    ingredients: List[str]
    preferences: Optional[Dict[str, Any]] = None


@router.post("/remote-ingredients")
async def receive_remote_ingredients(request: RemoteIngredientsRequest):
    """
    Receive ingredients extracted by the RPi camera module and return
    recipe recommendations.

    Flow:
        RPi captures image → Gemini Vision → ingredient names → POST here
        → sql_generator.py → recipe search → gap analysis → response

    Request body:
        {
            "ingredients": ["potato", "onion", "tomato"],
            "preferences": {}    // optional
        }
    """
    if not request.ingredients:
        raise HTTPException(status_code=400, detail="No ingredients provided")

    db = get_database()

    try:
        # Search recipes using the main app's ingredient search
        recipes = db.search_by_ingredients(request.ingredients, limit=15)

        if not recipes:
            return {
                "source": "remote_scan",
                "ingredients_received": request.ingredients,
                "count": 0,
                "recipes": [],
            }

        # Add gap analysis for each recipe
        results = []
        for recipe in recipes:
            gap_result = analyze_recipe_gaps(
                recipe["ingredients"], request.ingredients
            )
            results.append({
                **recipe,
                **gap_result,
            })

        # Sort by readiness, then match score
        results.sort(key=lambda r: (
            0 if r["readiness"] == "READY" else (
                1 if r["readiness"] == "ALMOST_THERE" else 2
            ),
            -r.get("match_score", 0),
        ))

        return {
            "source": "remote_scan",
            "ingredients_received": request.ingredients,
            "count": len(results),
            "recipes": results,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Recipe search failed: {exc}",
        )
