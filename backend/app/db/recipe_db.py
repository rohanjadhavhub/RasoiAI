""" 
RasoiAI Recipe Database — PostgreSQL (Neon) via psycopg2
"""

import psycopg2
from typing import List, Dict, Any, Optional

from app.core.config import get_settings


class RecipeDatabase:
    """Recipe database operations — PostgreSQL via psycopg2"""

    def __init__(self):
        settings = get_settings()
        self.database_url = settings.database_url
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is not set. Please set it in .env")
        self._ensure_table()

    # ── connection ────────────────────────────────────────────

    def get_connection(self):
        """Get PostgreSQL connection."""
        return psycopg2.connect(
            self.database_url,
            connect_timeout=10,
            options="-c statement_timeout=30000",
        )

    # ── helpers ───────────────────────────────────────────────

    def _ensure_table(self):
        """Create the recipes table if it doesn't exist."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id SERIAL PRIMARY KEY,
                    recipe TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    instruction TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_recipe_name ON recipes(recipe)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_ingredients ON recipes(ingredients)"
            )
            conn.commit()
        finally:
            conn.close()

    def _rows_to_dicts(self, cursor) -> List[Dict[str, Any]]:
        """Convert cursor results to list of dicts."""
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # ── generic execute ───────────────────────────────────────

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dicts."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return self._rows_to_dicts(cursor)
        finally:
            conn.close()

    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Execute write query and return last row id."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            q = query.rstrip().rstrip(";")
            if "RETURNING" not in q.upper():
                q += " RETURNING id"
            cursor.execute(q, params)
            row = cursor.fetchone()
            conn.commit()
            return row[0] if row else 0
        finally:
            conn.close()

    # ── recipe queries ────────────────────────────────────────

    def search_by_ingredients(
        self,
        ingredients: List[str],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search recipes by ingredients using LIKE matching."""
        if not ingredients:
            return []

        conditions = []
        for ing in ingredients:
            ing_lower = ing.lower()
            conditions.append(
                f"(LOWER(ingredients) LIKE '%{ing_lower}%')"
            )

        where_clause = " OR ".join(conditions)

        score_parts = []
        for ing in ingredients:
            ing_lower = ing.lower()
            score_parts.append(
                f"CASE WHEN LOWER(ingredients) LIKE '%{ing_lower}%' THEN 10 ELSE 0 END"
            )

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
        LIMIT {limit}
        """

        return self.execute_query(query)

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """Get specific recipe by ID."""
        query = """
        SELECT id as recipe_id, recipe, ingredients, instruction
        FROM recipes
        WHERE id = %s
        """
        results = self.execute_query(query, (recipe_id,))
        return results[0] if results else None

    def get_recipe_by_name(self, recipe_name: str) -> Optional[Dict[str, Any]]:
        """Get specific recipe by name."""
        query = """
        SELECT id as recipe_id, recipe, ingredients, instruction
        FROM recipes
        WHERE LOWER(recipe) = LOWER(%s)
        LIMIT 1
        """
        results = self.execute_query(query, (recipe_name,))
        return results[0] if results else None

    def get_all_recipes(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all recipes with limit."""
        query = f"""
        SELECT id as recipe_id, recipe, ingredients, instruction
        FROM recipes
        LIMIT {limit}
        """
        return self.execute_query(query)

    def get_recipe_count(self) -> int:
        """Get total recipe count."""
        query = "SELECT COUNT(*) as count FROM recipes"
        result = self.execute_query(query)
        return result[0]["count"] if result else 0


# Singleton instance
_db_instance: Optional[RecipeDatabase] = None


def get_database() -> RecipeDatabase:
    """Get or create database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = RecipeDatabase()
    return _db_instance
