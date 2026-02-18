"""
User Database Operations for RasoiAI
Stores user credentials synced from Auth0
"""
import sqlite3
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime


class UserDatabase:
    """User database operations"""

    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = db_path
        self._ensure_db_exists()
        self._create_tables()

    def _ensure_db_exists(self):
        """Ensure database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _create_tables(self):
        """Create users, favourites, and bookmarks tables if they don't exist"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    auth0_sub TEXT UNIQUE NOT NULL,
                    email TEXT,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favourites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    recipe_id INTEGER NOT NULL,
                    recipe_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, recipe_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    recipe_id INTEGER NOT NULL,
                    recipe_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    UNIQUE(user_id, recipe_id)
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

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

            # Check if user exists
            cursor.execute(
                "SELECT * FROM users WHERE auth0_sub = ?", (auth0_sub,)
            )
            existing = cursor.fetchone()

            if existing:
                # Update last_login and any changed fields
                cursor.execute(
                    """
                    UPDATE users
                    SET last_login = ?,
                        email = COALESCE(?, email),
                        username = COALESCE(?, username)
                    WHERE auth0_sub = ?
                    """,
                    (datetime.utcnow().isoformat(), email, username, auth0_sub),
                )
                conn.commit()
            else:
                # Create new user
                cursor.execute(
                    """
                    INSERT INTO users (auth0_sub, email, username, created_at, last_login)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        auth0_sub,
                        email,
                        username,
                        datetime.utcnow().isoformat(),
                        datetime.utcnow().isoformat(),
                    ),
                )
                conn.commit()

            # Return the user
            return self.get_user_by_sub(auth0_sub)
        finally:
            conn.close()

    def get_user_by_sub(self, auth0_sub: str) -> Optional[Dict[str, Any]]:
        """Get user by Auth0 subject ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE auth0_sub = ?", (auth0_sub,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by internal ID"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
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
            cursor.execute(
                """
                INSERT OR IGNORE INTO favourites (user_id, recipe_id, recipe_name, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, recipe_id, recipe_name, datetime.utcnow().isoformat()),
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
                "DELETE FROM favourites WHERE user_id = ? AND recipe_id = ?",
                (user_id, recipe_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_favourites(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all favourited recipes for a user"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT recipe_id, recipe_name, created_at
                FROM favourites
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def is_favourite(self, user_id: int, recipe_id: int) -> bool:
        """Check if a recipe is in user's favourites"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM favourites WHERE user_id = ? AND recipe_id = ?",
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
            cursor.execute(
                """
                INSERT OR IGNORE INTO bookmarks (user_id, recipe_id, recipe_name, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, recipe_id, recipe_name, datetime.utcnow().isoformat()),
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
                "DELETE FROM bookmarks WHERE user_id = ? AND recipe_id = ?",
                (user_id, recipe_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_bookmarks(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all bookmarked recipes for a user"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT recipe_id, recipe_name, created_at
                FROM bookmarks
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def is_bookmark(self, user_id: int, recipe_id: int) -> bool:
        """Check if a recipe is in user's bookmarks"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM bookmarks WHERE user_id = ? AND recipe_id = ?",
                (user_id, recipe_id),
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()


# Singleton instance
_user_db_instance: Optional[UserDatabase] = None


def get_user_database(db_path: str = "data/users.db") -> UserDatabase:
    """Get or create user database instance"""
    global _user_db_instance
    if _user_db_instance is None:
        _user_db_instance = UserDatabase(db_path)
    return _user_db_instance
