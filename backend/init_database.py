"""
Database initialization script for RasoiAI — PostgreSQL (Neon) only
Loads recipes from the real CSV dataset into Neon PostgreSQL.
Requires DATABASE_URL in .env
"""
import os
import csv
import psycopg2
from pathlib import Path
from dotenv import load_dotenv


def _get_csv_path() -> Path:
    """Locate the recipe CSV file."""
    candidates = [
        Path("../indian_recipe_cleaned.csv"),
        Path("indian_recipe_cleaned.csv"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "CSV file not found. Ensure indian_recipe_cleaned.csv is in the project root."
    )


def initialize_database():
    """Initialize the PostgreSQL database with real recipe data from CSV."""
    load_dotenv()
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL is not set. Please set it in .env")
        return

    csv_path = _get_csv_path()

    print(f"📂 CSV: {csv_path.absolute()}")
    print(f"📁 Target: PostgreSQL (Neon)")

    conn = psycopg2.connect(database_url, connect_timeout=10)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS recipes CASCADE")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id SERIAL PRIMARY KEY,
            recipe TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instruction TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()

    # Load CSV
    recipe_count = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            recipe_name = row.get("recipe", "").strip()
            ingredients = row.get("ingredients", "").strip()
            instruction = row.get("instruction", "").strip()

            if not recipe_name or not ingredients:
                continue

            cursor.execute(
                "INSERT INTO recipes (recipe, ingredients, instruction) VALUES (%s, %s, %s)",
                (recipe_name, ingredients, instruction),
            )
            recipe_count += 1

            if recipe_count % 1000 == 0:
                print(f"  📝 Loaded {recipe_count} recipes...")

    conn.commit()

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_recipe_name ON recipes(recipe)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ingredients ON recipes(ingredients)")
    conn.commit()
    conn.close()

    print(f"\n✅ Database initialized successfully!")
    print(f"📊 Total recipes loaded: {recipe_count}")


if __name__ == "__main__":
    initialize_database()
