"""
Data Migration Script: SQLite → PostgreSQL (Neon)

Migrates all data from local SQLite databases to a remote Neon PostgreSQL instance.
Tables are migrated in dependency order (parents before children).

Usage:
    python scripts/migrate_data.py              # run migration
    python scripts/migrate_data.py --dry-run    # validate without writing
"""
import sys
import os
import sqlite3
import argparse
from pathlib import Path


def get_pg_connection():
    """Get PostgreSQL connection."""
    import psycopg2
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable is not set.")
        sys.exit(1)
    return psycopg2.connect(database_url, connect_timeout=10)


def migrate_recipes(dry_run: bool = False):
    """Migrate the recipes table from SQLite → PostgreSQL."""
    sqlite_path = Path("data/recipes.db")
    if not sqlite_path.exists():
        print("⚠️  data/recipes.db not found — skipping recipes migration")
        return

    src = sqlite3.connect(str(sqlite_path))
    src.row_factory = sqlite3.Row
    cursor_src = src.cursor()

    # Count rows
    cursor_src.execute("SELECT COUNT(*) FROM recipes")
    total = cursor_src.fetchone()[0]

    if dry_run:
        print(f"🔍 recipes: {total} rows would be migrated")
        src.close()
        return

    # Fetch all rows
    cursor_src.execute("""
        SELECT rowid as id, recipe, ingredients, instruction
        FROM recipes
        ORDER BY rowid
    """)
    rows = cursor_src.fetchall()
    src.close()

    # Insert into PostgreSQL
    dst = get_pg_connection()
    cursor_dst = dst.cursor()

    # Ensure table exists
    cursor_dst.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id SERIAL PRIMARY KEY,
            recipe TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instruction TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    dst.commit()

    migrated = 0
    for row in rows:
        try:
            cursor_dst.execute(
                """
                INSERT INTO recipes (id, recipe, ingredients, instruction)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (row["id"], row["recipe"], row["ingredients"], row["instruction"]),
            )
            if cursor_dst.rowcount > 0:
                migrated += 1
        except Exception as e:
            print(f"  ⚠️  Row id={row['id']}: {e}")
            dst.rollback()
            continue

    # Reset sequence to max id
    cursor_dst.execute("SELECT MAX(id) FROM recipes")
    max_id = cursor_dst.fetchone()[0]
    if max_id:
        cursor_dst.execute(f"SELECT setval('recipes_id_seq', {max_id})")

    dst.commit()
    cursor_dst.execute("CREATE INDEX IF NOT EXISTS idx_recipe_name ON recipes(recipe)")
    cursor_dst.execute("CREATE INDEX IF NOT EXISTS idx_ingredients ON recipes(ingredients)")
    dst.commit()
    dst.close()

    print(f"✓ recipes: {migrated} rows migrated (of {total} total)")


def migrate_users(dry_run: bool = False):
    """Migrate users, favourites, and bookmarks from SQLite → PostgreSQL."""
    sqlite_path = Path("data/users.db")
    if not sqlite_path.exists():
        print("⚠️  data/users.db not found — skipping user data migration")
        return

    src = sqlite3.connect(str(sqlite_path))
    src.row_factory = sqlite3.Row

    tables = [
        ("users", ["id", "auth0_sub", "email", "username", "created_at", "last_login"]),
        ("favourites", ["id", "user_id", "recipe_id", "recipe_name", "created_at"]),
        ("bookmarks", ["id", "user_id", "recipe_id", "recipe_name", "created_at"]),
    ]

    # Dry run — just count
    if dry_run:
        for table_name, _ in tables:
            try:
                cursor = src.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                total = cursor.fetchone()[0]
                print(f"🔍 {table_name}: {total} rows would be migrated")
            except sqlite3.OperationalError:
                print(f"⚠️  {table_name}: table does not exist in SQLite")
        src.close()
        return

    dst = get_pg_connection()
    cursor_dst = dst.cursor()

    # Ensure tables exist (DDL)
    cursor_dst.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            auth0_sub TEXT UNIQUE NOT NULL,
            email TEXT,
            username TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            last_login TIMESTAMP DEFAULT NOW()
        )
    """)
    cursor_dst.execute("""
        CREATE TABLE IF NOT EXISTS favourites (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            recipe_id INTEGER NOT NULL,
            recipe_name TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, recipe_id)
        )
    """)
    cursor_dst.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            recipe_id INTEGER NOT NULL,
            recipe_name TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, recipe_id)
        )
    """)
    dst.commit()

    # Migrate each table in order
    for table_name, columns in tables:
        try:
            cursor_src = src.cursor()
            cursor_src.execute(f"SELECT * FROM {table_name} ORDER BY id")
            rows = cursor_src.fetchall()
        except sqlite3.OperationalError:
            print(f"⚠️  {table_name}: table does not exist in SQLite — skipped")
            continue

        migrated = 0
        placeholders = ", ".join(["%s"] * len(columns))
        col_list = ", ".join(columns)

        for row in rows:
            values = tuple(row[col] for col in columns)
            try:
                cursor_dst.execute(
                    f"""
                    INSERT INTO {table_name} ({col_list})
                    VALUES ({placeholders})
                    ON CONFLICT (id) DO NOTHING
                    """,
                    values,
                )
                if cursor_dst.rowcount > 0:
                    migrated += 1
            except Exception as e:
                print(f"  ⚠️  {table_name} id={row['id']}: {e}")
                dst.rollback()
                continue

        dst.commit()

        # Reset sequence
        cursor_dst.execute(f"SELECT MAX(id) FROM {table_name}")
        max_id = cursor_dst.fetchone()[0]
        if max_id:
            cursor_dst.execute(f"SELECT setval('{table_name}_id_seq', {max_id})")
            dst.commit()

        print(f"✓ {table_name}: {migrated} rows migrated (of {len(rows)} total)")

    src.close()
    dst.close()


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite data → PostgreSQL (Neon)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate without writing to PostgreSQL",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("RasoiAI Data Migration: SQLite → PostgreSQL")
    print("=" * 50)

    if args.dry_run:
        print("MODE: DRY RUN (no data will be written)\n")
    else:
        print("MODE: LIVE MIGRATION\n")

    migrate_recipes(dry_run=args.dry_run)
    migrate_users(dry_run=args.dry_run)

    print("\n" + "=" * 50)
    if args.dry_run:
        print("Dry run complete. No data was written.")
    else:
        print("Migration complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
