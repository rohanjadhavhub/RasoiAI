"""
RasoiAI Database Package

Re-exports for convenience:
    from app.db import get_database, get_user_database
"""
from app.db.recipe_db import get_database, RecipeDatabase
from app.db.user_db import get_user_database, UserDatabase
