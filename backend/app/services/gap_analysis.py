"""
Gap Analysis Service - Analyze missing ingredients for recipes
"""
from typing import List, Dict, Any
import re


# Ingredients assumed to be available in most Indian households
ASSUMED_AVAILABLE = {
    # Basic spices
    "salt", "oil", "cooking oil", "vegetable oil", "ghee", "water",
    "turmeric", "turmeric powder", "haldi",
    "cumin", "cumin seeds", "cumin powder", "jeera",
    "coriander powder", "dhania powder",
    "red chili", "red chili powder", "lal mirch",
    "mustard seeds", "rai", "sarson",
    "garam masala",
    "black pepper", "pepper", "kali mirch",
    
    # Aromatics
    "onion", "onions", "pyaz",
    "tomato", "tomatoes", "tamatar",
    "ginger", "adrak",
    "garlic", "lahsun",
    "green chili", "green chilies", "hari mirch",
    
    # Common herbs
    "curry leaves", "kadi patta",
    "coriander leaves", "dhania", "cilantro",
    
    # Basics
    "sugar", "jaggery",
}

# Main ingredients that define a dish (strict matching)
MAIN_INGREDIENT_CATEGORIES = {
    "vegetable", "protein", "grain", "legume", "dairy"
}

# Ingredient name variations mapping
INGREDIENT_ALIASES = {
    "potato": ["aloo", "batata", "potatoes"],
    "cauliflower": ["gobi", "phool gobi", "gobhi"],
    "paneer": ["cottage cheese", "indian cheese"],
    "spinach": ["palak", "saag"],
    "peas": ["matar", "green peas"],
    "eggplant": ["baingan", "brinjal", "aubergine"],
    "okra": ["bhindi", "lady finger", "ladyfinger"],
    "bitter gourd": ["karela", "bitter melon"],
    "bottle gourd": ["lauki", "doodhi", "ghiya"],
    "ridge gourd": ["tori", "turai"],
    "chickpeas": ["chole", "chana", "kabuli chana"],
    "kidney beans": ["rajma", "red beans"],
    "lentils": ["dal", "daal"],
    "chicken": ["murgh", "murga"],
    "mutton": ["gosht", "lamb"],
    "fish": ["machhi", "machhli"],
    "egg": ["eggs", "anda", "ande"],
    "rice": ["chawal", "basmati"],
    "wheat flour": ["atta", "gehu ka atta", "whole wheat flour"],
    "gram flour": ["besan", "chickpea flour"],
}


def normalize_ingredient(ingredient: str) -> str:
    """Normalize ingredient name to base form"""
    ing = ingredient.lower().strip()
    
    # Remove quantities and measurements
    ing = re.sub(r'\d+[\s]*(?:tsp|tbsp|cup|cups|kg|g|ml|l|pieces?|medium|small|large|inch)?[\s]*', '', ing)
    
    # Remove common prefixes/suffixes
    ing = re.sub(r'(?:fresh|dried|chopped|sliced|diced|grated|minced|crushed|boiled|cooked|raw)\s*', '', ing)
    
    # Remove trailing descriptions
    ing = re.sub(r'\s*[-–]\s*.*$', '', ing)
    ing = re.sub(r'\s*\(.*\)', '', ing)
    
    return ing.strip()


def is_assumed_available(ingredient: str) -> bool:
    """Check if ingredient is assumed to be available in Indian households"""
    normalized = normalize_ingredient(ingredient)
    
    # Direct match
    if normalized in ASSUMED_AVAILABLE:
        return True
    
    # Partial match
    for assumed in ASSUMED_AVAILABLE:
        if assumed in normalized or normalized in assumed:
            return True
    
    return False


def ingredients_match(user_ing: str, recipe_ing: str) -> bool:
    """Check if user ingredient matches recipe ingredient"""
    user_norm = normalize_ingredient(user_ing)
    recipe_norm = normalize_ingredient(recipe_ing)
    
    # Direct match
    if user_norm == recipe_norm:
        return True
    
    # Partial match
    if user_norm in recipe_norm or recipe_norm in user_norm:
        return True
    
    # Check aliases
    for base, aliases in INGREDIENT_ALIASES.items():
        all_names = [base] + aliases
        user_matches = any(name in user_norm or user_norm in name for name in all_names)
        recipe_matches = any(name in recipe_norm or recipe_norm in name for name in all_names)
        
        if user_matches and recipe_matches:
            return True
    
    return False


def parse_recipe_ingredients(ingredients_str: str) -> List[str]:
    """Parse comma-separated ingredient string into list"""
    # Split by common delimiters
    ingredients = re.split(r'[,;]', ingredients_str)
    
    # Clean and normalize
    cleaned = []
    for ing in ingredients:
        ing = ing.strip()
        if ing and len(ing) > 1:
            cleaned.append(ing)
    
    return cleaned


def analyze_recipe_gaps(
    recipe_ingredients: str, 
    user_ingredients: List[str]
) -> Dict[str, Any]:
    """
    Analyze gaps between recipe requirements and user's ingredients
    
    Args:
        recipe_ingredients: Comma-separated ingredient string from recipe
        user_ingredients: List of ingredients user has
        
    Returns:
        Dict with have, missing_critical, missing_optional, readiness
    """
    recipe_items = parse_recipe_ingredients(recipe_ingredients)
    
    have = []
    missing_critical = []
    missing_optional = []
    
    for recipe_item in recipe_items:
        # Check if assumed available
        if is_assumed_available(recipe_item):
            continue  # Don't show to user
        
        # Check if user has it
        user_has = any(
            ingredients_match(user_ing, recipe_item) 
            for user_ing in user_ingredients
        )
        
        if user_has:
            have.append(normalize_ingredient(recipe_item))
        else:
            # Determine if critical or optional
            normalized = normalize_ingredient(recipe_item)
            
            # Optional if it's a garnish or enhancement
            optional_keywords = ["garnish", "optional", "for serving", "kasuri", "sev"]
            is_optional = any(kw in recipe_item.lower() for kw in optional_keywords)
            
            if is_optional:
                missing_optional.append(normalized)
            else:
                missing_critical.append(normalized)
    
    # Determine readiness
    if len(missing_critical) == 0:
        readiness = "READY"
    elif len(missing_critical) <= 2:
        readiness = "ALMOST_THERE"
    else:
        readiness = "NEED_SHOPPING"
    
    return {
        "have": have,
        "missing_critical": missing_critical,
        "missing_optional": missing_optional,
        "readiness": readiness
    }
