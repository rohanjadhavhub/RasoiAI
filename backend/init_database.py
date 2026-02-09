"""
Database initialization script for RasoiAI
Loads recipes from the real CSV dataset
"""
import sqlite3
import csv
from pathlib import Path


def initialize_database():
    """Initialize the SQLite database with real recipe data from CSV"""
    
    # Database path
    db_path = Path("data/recipes.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # CSV path
    csv_path = Path("../indian_recipe_cleaned.csv")
    
    if not csv_path.exists():
        # Try alternate path
        csv_path = Path("indian_recipe_cleaned.csv")
        if not csv_path.exists():
            csv_path = Path("../indian_recipe_cleaned.csv")
    
    print(f"📂 Looking for CSV at: {csv_path.absolute()}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Drop existing table and recreate
    cursor.execute("DROP TABLE IF EXISTS recipes")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instruction TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Load recipes from CSV
    recipe_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                recipe_name = row.get('recipe', '').strip()
                ingredients = row.get('ingredients', '').strip()
                instruction = row.get('instruction', '').strip()
                
                # Skip empty rows
                if not recipe_name or not ingredients:
                    continue
                
                cursor.execute(
                    "INSERT INTO recipes (recipe, ingredients, instruction) VALUES (?, ?, ?)",
                    (recipe_name, ingredients, instruction)
                )
                recipe_count += 1
                
                # Progress indicator
                if recipe_count % 1000 == 0:
                    print(f"  📝 Loaded {recipe_count} recipes...")
        
        conn.commit()
        
    except FileNotFoundError:
        print(f"❌ CSV file not found at {csv_path}")
        print("   Please ensure indian_recipe_cleaned.csv is in the project root")
        return
    
    # Create indexes for faster searching
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_recipe_name ON recipes(recipe)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ingredients ON recipes(ingredients)")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database initialized successfully!")
    print(f"📊 Total recipes loaded: {recipe_count}")
    print(f"📁 Database location: {db_path.absolute()}")


if __name__ == "__main__":
    initialize_database()
