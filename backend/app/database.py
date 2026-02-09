"""
SQLite Database Operations for RasoiAI
"""
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path


class RecipeDatabase:
    """Recipe database operations"""
    
    def __init__(self, db_path: str = "data/recipes.db"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dicts"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()
    
    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Execute write query and return last row id"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def search_by_ingredients(
        self, 
        ingredients: List[str], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search recipes by ingredients using LIKE matching"""
        if not ingredients:
            return []
        
        # Build LIKE conditions for each ingredient
        conditions = []
        for ing in ingredients:
            ing_lower = ing.lower()
            conditions.append(
                f"(LOWER(ingredients) LIKE '%{ing_lower}%')"
            )
        
        where_clause = " OR ".join(conditions)
        
        # Calculate match score
        score_parts = []
        for ing in ingredients:
            ing_lower = ing.lower()
            score_parts.append(
                f"CASE WHEN LOWER(ingredients) LIKE '%{ing_lower}%' THEN 10 ELSE 0 END"
            )
        
        score_clause = " + ".join(score_parts)
        
        query = f"""
        SELECT 
            rowid as recipe_id,
            recipe,
            ingredients,
            instruction,
            ({score_clause}) as match_score
        FROM recipes
        WHERE {where_clause}
        ORDER BY match_score DESC
        LIMIT {limit}
        """
        
        return self.execute_query(query)
    
    def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """Get specific recipe by ID"""
        query = """
        SELECT rowid as recipe_id, recipe, ingredients, instruction
        FROM recipes
        WHERE rowid = ?
        """
        results = self.execute_query(query, (recipe_id,))
        return results[0] if results else None
    
    def get_recipe_by_name(self, recipe_name: str) -> Optional[Dict[str, Any]]:
        """Get specific recipe by name"""
        query = """
        SELECT rowid as recipe_id, recipe, ingredients, instruction
        FROM recipes
        WHERE LOWER(recipe) = LOWER(?)
        LIMIT 1
        """
        results = self.execute_query(query, (recipe_name,))
        return results[0] if results else None
    
    def get_all_recipes(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all recipes with limit"""
        query = f"""
        SELECT rowid as recipe_id, recipe, ingredients, instruction
        FROM recipes
        LIMIT {limit}
        """
        return self.execute_query(query)
    
    def get_recipe_count(self) -> int:
        """Get total recipe count"""
        query = "SELECT COUNT(*) as count FROM recipes"
        result = self.execute_query(query)
        return result[0]['count'] if result else 0


# Singleton instance
_db_instance: Optional[RecipeDatabase] = None


def get_database(db_path: str = "data/recipes.db") -> RecipeDatabase:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = RecipeDatabase(db_path)
    return _db_instance
