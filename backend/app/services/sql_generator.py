"""
SQL Generator Service - Dynamic SQL query generation using Gemini
"""
import json
from typing import List, Dict, Any, Optional
from google import genai

from app.core.config import get_settings
from app.db import get_database

settings = get_settings()

# Configure Gemini client
client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None


SQL_GENERATION_PROMPT = """You are a SQL expert specializing in recipe search queries.

Generate an optimized PostgreSQL query to find matching recipes based on:

User's Ingredients: {ingredients}
Preferences: {preferences}

Database Schema:
Table: recipes
Columns:
- id (INTEGER PRIMARY KEY) - Recipe ID
- recipe (TEXT) - Recipe name
- ingredients (TEXT) - Comma-separated ingredient list
- instruction (TEXT) - Cooking instructions

Query Requirements:
1. Use the `id` column as `recipe_id` (SELECT id as recipe_id)
2. Main ingredients MUST be present (use OR for alternate names)
   - Example: "potato" OR "aloo" OR "batata"
3. Assume common Indian spices/aromatics are available (don't filter for them):
   - Spices: turmeric, cumin, coriander powder, red chili, mustard seeds, garam masala
   - Aromatics: onion, tomato, ginger, garlic, green chili
   - Basics: salt, oil, ghee
4. Calculate match_score favoring recipes with more ingredient matches
5. Use LOWER() for case-insensitive matching
6. Order by match_score DESC
7. LIMIT 15 results

Generate ONLY the SQL query, no explanations or markdown.
"""


async def generate_recipe_query(
    ingredients: List[str],
    preferences: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate SQL query using AI or fallback to basic query

    Args:
        ingredients: List of user ingredients
        preferences: Optional user preferences

    Returns:
        SQL query string
    """
    if not settings.gemini_api_key:
        return _generate_basic_query(ingredients)

    try:
        prompt = SQL_GENERATION_PROMPT.format(
            ingredients=ingredients,
            preferences=preferences or {}
        )

        response = client.models.generate_content(
            model=settings.gemini_text_model,
            contents=prompt
        )
        query = response.text.strip()

        # Clean up response
        if query.startswith("```"):
            lines = query.split("\n")
            query = "\n".join(lines[1:-1])

        # Validate query is SELECT
        if not query.upper().startswith("SELECT"):
            return _generate_basic_query(ingredients)

        return query

    except Exception as e:
        print(f"SQL generation error: {e}")
        return _generate_basic_query(ingredients)


def _generate_basic_query(ingredients: List[str]) -> str:
    """Generate basic SQL query without AI"""
    if not ingredients:
        return "SELECT id as recipe_id, recipe, ingredients, instruction FROM recipes LIMIT 10"

    # Build LIKE conditions
    conditions = []
    score_parts = []

    for ing in ingredients:
        ing_lower = ing.lower()
        conditions.append(f"LOWER(ingredients) LIKE '%{ing_lower}%'")
        score_parts.append(
            f"CASE WHEN LOWER(ingredients) LIKE '%{ing_lower}%' THEN 10 ELSE 0 END"
        )

    where_clause = " OR ".join(conditions)
    score_clause = " + ".join(score_parts)

    query = f"""
    SELECT
        id as recipe_id,
        recipe,
        ingredients,
        instruction,
        ({score_clause}) as match_score
    FROM recipes
    WHERE {where_clause}
    ORDER BY match_score DESC
    LIMIT 15
    """

    return query


async def execute_ai_query(
    ingredients: List[str],
    preferences: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Generate and execute AI-powered query

    Args:
        ingredients: List of user ingredients
        preferences: Optional preferences

    Returns:
        List of matching recipes
    """
    query = await generate_recipe_query(ingredients, preferences)

    db = get_database()

    try:
        results = db.execute_query(query)
        return results
    except Exception as e:
        print(f"Query execution error: {e}")
        # Fallback to basic search
        return db.search_by_ingredients(ingredients)
