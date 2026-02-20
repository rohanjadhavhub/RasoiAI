"""
User Database Operations for RasoiAI — PostgreSQL (Neon) only
Stores user credentials synced from Auth0.
"""
import psycopg2
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.config import get_settings


class UserDatabase:
    """User database operations — PostgreSQL via psycopg2"""

    def __init__(self):
        settings = get_settings()
        self.database_url = settings.database_url
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is not set. Please set it in .env")
        self._create_tables()

    # ── connection ────────────────────────────────────────────

    def get_connection(self):
        """Get PostgreSQL connection."""
        return psycopg2.connect(
            self.database_url,
            connect_timeout=10,
            options="-c statement_timeout=30000",
        )

    # ── helpers ───────────────────────────────────────────────

    def _rows_to_dicts(self, cursor) -> List[Dict[str, Any]]:
        """Convert cursor results to list of dicts."""
        columns = [desc[0] for desc in cursor.description]
        rows = []
        for row in cursor.fetchall():
            d = dict(zip(columns, row))
            # Convert datetime objects to ISO strings for Pydantic compatibility
            for k, v in d.items():
                if isinstance(v, datetime):
                    d[k] = v.isoformat()
            rows.append(d)
        return rows

    def _row_to_dict(self, cursor) -> Optional[Dict[str, Any]]:
        """Fetch one row as a dict, or None."""
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in cursor.description]
        d = dict(zip(columns, row))
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        return d

    # ── table creation ────────────────────────────────────────

    def _create_tables(self):
        """Create tables in PostgreSQL."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    auth0_sub TEXT UNIQUE NOT NULL,
                    email TEXT,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_login TIMESTAMP DEFAULT NOW()
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favourites (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    recipe_id INTEGER NOT NULL,
                    recipe_name TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, recipe_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    recipe_id INTEGER NOT NULL,
                    recipe_name TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, recipe_id)
                )
            """)
            conn.commit()
        finally:
            conn.close()

    # ── user CRUD ─────────────────────────────────────────────

    def upsert_user(
        self,
        auth0_sub: str,
        email: Optional[str] = None,
        username: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create or update user from Auth0 claims.
        On first login: creates user row.
        On subsequent logins: updates last_login, email, username.
        Returns the user dict.
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE auth0_sub = %s", (auth0_sub,)
            )
            existing = self._row_to_dict(cursor)

            now = datetime.utcnow().isoformat()

            if existing:
                cursor.execute(
                    """
                    UPDATE users
                    SET last_login = %s,
                        email = COALESCE(%s, email),
                        username = COALESCE(%s, username)
                    WHERE auth0_sub = %s
                    """,
                    (now, email, username, auth0_sub),
                )
                conn.commit()
            else:
                cursor.execute(
                    """
                    INSERT INTO users (auth0_sub, email, username, created_at, last_login)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (auth0_sub, email, username, now, now),
                )
                conn.commit()

            return self.get_user_by_sub(auth0_sub)
        finally:
            conn.close()

    def get_user_by_sub(self, auth0_sub: str) -> Optional[Dict[str, Any]]:
        """Get user by Auth0 subject ID."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE auth0_sub = %s", (auth0_sub,)
            )
            return self._row_to_dict(cursor)
        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by internal ID."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return self._row_to_dict(cursor)
        finally:
            conn.close()

    # ─── Favourites ───────────────────────────────────────────

    def add_favourite(
        self, user_id: int, recipe_id: int, recipe_name: Optional[str] = None
    ) -> bool:
        """Add a recipe to user's favourites. Returns True if added, False if already exists."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """
                INSERT INTO favourites (user_id, recipe_id, recipe_name, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, recipe_id) DO NOTHING
                """,
                (user_id, recipe_id, recipe_name, now),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def remove_favourite(self, user_id: int, recipe_id: int) -> bool:
        """Remove a recipe from user's favourites. Returns True if removed."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM favourites WHERE user_id = %s AND recipe_id = %s",
                (user_id, recipe_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_favourites(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all favourited recipes for a user."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT recipe_id, recipe_name, created_at
                FROM favourites
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return self._rows_to_dicts(cursor)
        finally:
            conn.close()

    def is_favourite(self, user_id: int, recipe_id: int) -> bool:
        """Check if a recipe is in user's favourites."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM favourites WHERE user_id = %s AND recipe_id = %s",
                (user_id, recipe_id),
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()

    # ─── Bookmarks ────────────────────────────────────────────

    def add_bookmark(
        self, user_id: int, recipe_id: int, recipe_name: Optional[str] = None
    ) -> bool:
        """Add a recipe to user's bookmarks. Returns True if added, False if already exists."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """
                INSERT INTO bookmarks (user_id, recipe_id, recipe_name, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, recipe_id) DO NOTHING
                """,
                (user_id, recipe_id, recipe_name, now),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def remove_bookmark(self, user_id: int, recipe_id: int) -> bool:
        """Remove a recipe from user's bookmarks. Returns True if removed."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM bookmarks WHERE user_id = %s AND recipe_id = %s",
                (user_id, recipe_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_bookmarks(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all bookmarked recipes for a user."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT recipe_id, recipe_name, created_at
                FROM bookmarks
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return self._rows_to_dicts(cursor)
        finally:
            conn.close()

    def is_bookmark(self, user_id: int, recipe_id: int) -> bool:
        """Check if a recipe is in user's bookmarks."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM bookmarks WHERE user_id = %s AND recipe_id = %s",
                (user_id, recipe_id),
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()


# Singleton instance
_user_db_instance: Optional[UserDatabase] = None


def get_user_database() -> UserDatabase:
    """Get or create user database instance."""
    global _user_db_instance
    if _user_db_instance is None:
        _user_db_instance = UserDatabase()
    return _user_db_instance
