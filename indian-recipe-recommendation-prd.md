# Product Requirements Document (PRD)
## Indian Recipe Recommendation - Agentic Workflow

---

**Document Version:** 1.0  
**Last Updated:** February 9, 2026  
**Status:** Draft  
**Owner:** Product Team

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Product Vision](#product-vision)
4. [User Personas](#user-personas)
5. [Core Features](#core-features)
6. [System Architecture](#system-architecture)
7. [Workflow Details](#workflow-details)
8. [Database Design](#database-design)
9. [AI/ML Components](#aiml-components)
10. [User Experience Flow](#user-experience-flow)
11. [Technical Requirements](#technical-requirements)
12. [Success Metrics](#success-metrics)
13. [Future Enhancements](#future-enhancements)
14. [Risks & Mitigation](#risks--mitigation)

---

## Executive Summary

### Product Overview
An intelligent recipe recommendation system that analyzes photos of available ingredients and suggests authentic Indian recipes users can make immediately. The system uses computer vision, AI-powered SQL query generation, and conversational AI to provide personalized cooking suggestions.

### Key Value Proposition
- **Zero Food Waste:** Use what you already have
- **Instant Recommendations:** Get recipes in <5 seconds
- **Indian Cooking Optimized:** Understands regional variations and common pantry assumptions
- **Intelligent Matching:** Strict on main ingredients, flexible on spices
- **Conversational Support:** Ask questions, get modifications, find alternatives

### Target Market
- Indian households looking to reduce food waste
- Home cooks seeking recipe inspiration from available ingredients
- Users wanting to explore regional Indian cuisine
- Beginner cooks needing step-by-step guidance

---

## Problem Statement

### Current Challenges
1. **Decision Fatigue:** Users don't know what to cook with available ingredients
2. **Food Waste:** Ingredients expire before being used
3. **Recipe Mismatch:** Most recipe apps assume you'll shop for ingredients first
4. **Indian Cooking Gap:** Generic recipe apps don't understand Indian pantry assumptions (spices, aromatics)
5. **Scattered Information:** Users search multiple sources, get overwhelmed

### User Pain Points
- "I have random vegetables but don't know what to make"
- "Recipe needs 15 ingredients, I only have 8"
- "Don't know if I can substitute ingredients"
- "Recipe is too complicated for my skill level"
- "Unsure about cooking time with available equipment"

---

## Product Vision

### Vision Statement
*"Make cooking delightful by helping users discover what they can create with what they already have, eliminating the gap between inspiration and action."*

### Mission
Leverage AI to bridge the gap between available ingredients and delicious Indian meals, making home cooking accessible, waste-free, and enjoyable.

### Success Criteria
- Users cook more frequently at home
- Reduced ingredient waste
- Increased confidence in Indian cooking
- High recipe completion rate (>70%)

---

## User Personas

### Primary Persona: "Busy Priya"
- **Age:** 28-35
- **Occupation:** Working professional
- **Location:** Urban India (Mumbai, Bangalore, Delhi)
- **Cooking Skill:** Intermediate
- **Pain Points:**
  - Limited time for meal planning
  - Hates food waste
  - Wants variety without extensive shopping
- **Goals:**
  - Quick dinner ideas (<45 min)
  - Use groceries before they expire
  - Impress family with new recipes

### Secondary Persona: "Learning Rahul"
- **Age:** 22-28
- **Occupation:** Student/Young professional
- **Location:** Staying away from home
- **Cooking Skill:** Beginner
- **Pain Points:**
  - Misses home-cooked food
  - Limited cooking knowledge
  - Budget constraints
- **Goals:**
  - Learn basic Indian cooking
  - Make simple, tasty meals
  - Avoid ordering food daily

### Tertiary Persona: "Experimental Anjali"
- **Age:** 35-50
- **Occupation:** Homemaker/Part-time professional
- **Location:** Tier 1/2 cities
- **Cooking Skill:** Advanced
- **Pain Points:**
  - Wants to try new regional cuisines
  - Family gets bored of same dishes
  - Looking for creative uses of ingredients
- **Goals:**
  - Explore regional Indian recipes
  - Fusion cooking experiments
  - Seasonal ingredient utilization

---

## Core Features

### Feature 1: Photo-Based Ingredient Recognition
**Priority:** P0 (Must Have)

**Description:**  
Users upload 2-3 photos of available ingredients. Computer vision AI identifies ingredients with confidence scores.

**User Story:**  
*"As a user, I want to quickly show what ingredients I have so that I don't have to manually type them out."*

**Acceptance Criteria:**
- ✅ Accepts 2-3 images (JPG, PNG, HEIC)
- ✅ Identifies common Indian vegetables (potato, onion, tomato, cauliflower, etc.)
- ✅ Recognizes proteins (chicken, paneer, eggs, dal varieties)
- ✅ Handles packaged items with OCR (spice labels, dal packets)
- ✅ Provides confidence scores for uncertain items
- ✅ Allows user to confirm/correct identifications
- ✅ Processes images in <3 seconds

**Technical Notes:**
- Use GPT-4 Vision or similar multimodal LLM
- Handle poor lighting/blurry images gracefully
- Support regional ingredient variations

---

### Feature 2: Intelligent Recipe Matching
**Priority:** P0 (Must Have)

**Description:**  
AI generates SQL queries to match user's ingredients with recipes from SQLite database. Implements strict matching for main ingredients, assumes common spices are available.

**User Story:**  
*"As a user, I want recipe suggestions that I can actually make with what I have, not recipes requiring extensive shopping."*

**Acceptance Criteria:**
- ✅ Matches recipes based on main ingredients (strict)
- ✅ Assumes common Indian spices available (turmeric, cumin, coriander, red chili, mustard seeds)
- ✅ Assumes basic aromatics available (onion, tomato, ginger, garlic)
- ✅ Returns 3 recommendation tiers:
  - **Ready to Cook:** 0 missing items
  - **Almost There:** 1-2 common items needed
  - **Worth Shopping For:** 3+ items needed
- ✅ Considers user preferences (cuisine, time, dietary)
- ✅ Handles regional name variations (aloo/potato, karela/bitter gourd)
- ✅ Query execution time <500ms

**Matching Logic:**
```
Priority 1: Main ingredients (vegetables, proteins) - STRICT
Priority 2: Special ingredients (kasuri methi, coconut) - FLAG as optional
Priority 3: Common spices & aromatics - ASSUME available
```

---

### Feature 3: User Preference Collection
**Priority:** P0 (Must Have)

**Description:**  
Interactive questions to understand user's cooking context and preferences before recipe matching.

**User Story:**  
*"As a user, I want the system to consider my dietary restrictions and time constraints so I get relevant recommendations."*

**Acceptance Criteria:**
- ✅ Collects preferences via conversational interface:
  - Cuisine preference (North/South/East/West Indian, Any)
  - Cooking time (<20 min, <45 min, <90 min, No limit)
  - Meal type (Breakfast, Lunch, Dinner, Snack)
  - Dietary restrictions (Veg, Non-veg, Vegan, Jain, No onion-garlic)
  - Spice level (Mild, Medium, Spicy)
  - Skill level (Beginner, Intermediate, Advanced)
- ✅ Remembers preferences for future sessions
- ✅ Allows users to skip/modify preferences
- ✅ Quick selection UI (not lengthy forms)

---

### Feature 4: Gap Analysis & Substitutions
**Priority:** P0 (Must Have)

**Description:**  
After recipe matching, system identifies missing ingredients and suggests substitutions where applicable.

**User Story:**  
*"As a user, I want to know exactly what I'm missing and if I can substitute anything so I can decide whether to cook or shop."*

**Acceptance Criteria:**
- ✅ Categorizes missing ingredients:
  - **Critical:** Main vegetables/proteins (deal-breakers)
  - **Nice-to-have:** Special ingredients (optional)
  - **Assumed:** Common pantry items (not shown to user)
- ✅ Suggests substitutions for regional ingredients
  - Example: Kashmiri red chili → Paprika + Cayenne
  - Example: Coconut milk → Cashew paste + water
  - Example: Curry leaves → Can skip (adjust aromatics)
- ✅ Estimates "effort score" for acquiring missing items
- ✅ Shows impact of skipping optional ingredients

---

### Feature 5: Step-by-Step Recipe Instructions
**Priority:** P0 (Must Have)

**Description:**  
Display complete recipe with highlighted available ingredients and clear cooking steps.

**User Story:**  
*"As a user, I want clear, numbered instructions so I can follow along easily while cooking."*

**Acceptance Criteria:**
- ✅ Shows full ingredient list with checkmarks for available items
- ✅ Numbered, sequential cooking steps
- ✅ Estimated time per step (where applicable)
- ✅ Cooking tips and pro suggestions
- ✅ Visual formatting for readability
- ✅ Servings information (adjustable in future)

---

### Feature 6: Conversational AI Assistant
**Priority:** P1 (Should Have)

**Description:**  
Chat interface for users to ask questions, request modifications, and get alternatives.

**User Story:**  
*"As a user, I want to ask questions about the recipe and get instant answers so I don't have to search elsewhere."*

**Acceptance Criteria:**
- ✅ Answer recipe-specific questions:
  - "Can I use pressure cooker instead?"
  - "How do I reduce spice level?"
  - "What if I don't have garam masala?"
- ✅ Suggest modifications:
  - "Make it vegan"
  - "Reduce cooking time"
  - "Add more protein"
- ✅ Find alternatives:
  - "I don't want bitter gourd, what else?"
  - "Show me breakfast options with same ingredients"
- ✅ Context-aware responses (remembers recipe being discussed)
- ✅ Regenerates SQL queries for alternative requests
- ✅ Natural language understanding

---

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│  User Interface │
│   (Web/Mobile)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Application Layer (Python/Node)   │
│  ┌──────────────────────────────┐  │
│  │  Orchestration Agent         │  │
│  └──────────────────────────────┘  │
└────────┬───────────────┬────────────┘
         │               │
         ▼               ▼
┌──────────────┐  ┌──────────────────┐
│  Vision AI   │  │  Language Model  │
│  (GPT-4V/    │  │  (GPT-4/Claude)  │
│   Claude)    │  │                  │
└──────────────┘  └─────────┬────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  SQL Generator   │
                  │  (AI-Powered)    │
                  └─────────┬────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  SQLite Database │
                  │  (recipes.db)    │
                  └──────────────────┘
```

### Component Breakdown

#### 1. Frontend Layer
- **Technology:** React/Next.js (Web) or React Native (Mobile)
- **Responsibilities:**
  - Image upload and preview
  - User preference collection
  - Recipe display
  - Chat interface

#### 2. Backend Layer
- **Technology:** Python (FastAPI) or Node.js (Express)
- **Responsibilities:**
  - API endpoints
  - Request orchestration
  - Session management
  - Error handling

#### 3. AI Layer
- **Vision Agent:**
  - Model:  Gemini Vision
  - Input: 2-3 images
  - Output: Structured JSON with identified ingredients
  
- **SQL Generation Agent:**
  - Model: gemini-2.5-flash
  - Input: User ingredients + preferences
  - Output: Optimized SQL query
  
- **Conversational Agent:**
  - Model: gemini-2.5-flash
  - Input: User question + recipe context
  - Output: Natural language response

#### 4. Database Layer
- **Technology:** SQLite (MVP)
- **Storage:** Recipe data with search indexes
- **Size:** ~3-5 MB for 500 recipes

---

## Workflow Details

### End-to-End Workflow

```
Step 1: Image Upload
    ↓
Step 2: Ingredient Recognition
    ↓
Step 3: User Preference Collection
    ↓
Step 4: SQL Query Generation
    ↓
Step 5: Recipe Retrieval
    ↓
Step 6: Gap Analysis
    ↓
Step 7: Recipe Presentation
    ↓
Step 8: Conversational Support (ongoing)
```

### Detailed Workflow Steps

#### **Step 1: Image Upload**
**User Action:** Takes/uploads 2-3 photos of ingredients

**System Action:**
- Validates image format (JPG, PNG, HEIC)
- Compresses images if >5MB
- Stores temporarily for processing
- Shows upload progress

**Output:** Uploaded images ready for processing

**Error Handling:**
- Invalid format → Show error message
- Too large → Auto-compress
- Upload failure → Retry option

---

#### **Step 2: Ingredient Recognition**
**User Action:** Waits for analysis

**System Action:**
```python
# Vision AI Processing
images = [image1, image2, image3]
prompt = """
Identify all Indian cooking ingredients visible in these images.
For each ingredient, provide:
- name (common English/Hindi name)
- category (vegetable/protein/spice/grain)
- confidence_score (0-1)
- quantity_estimate (if visible)

Output as JSON.
"""

response = vision_ai.analyze(images, prompt)

# Sample Output
{
  "identified_ingredients": [
    {
      "name": "potato",
      "alternate_names": ["aloo", "batata"],
      "category": "vegetable",
      "confidence": 0.95,
      "quantity": "4-5 medium pieces"
    },
    {
      "name": "cauliflower",
      "alternate_names": ["gobi", "phool gobi"],
      "category": "vegetable",
      "confidence": 0.92,
      "quantity": "1 small head"
    },
    {
      "name": "uncertain_item",
      "category": "unknown",
      "confidence": 0.45,
      "note": "unclear due to lighting"
    }
  ],
  "visible_packaged_items": [
    {
      "name": "Everest Garam Masala",
      "category": "spice",
      "confidence": 0.88
    }
  ]
}
```

**User Confirmation:**
- Shows identified ingredients
- Allows corrections/additions
- Asks clarifying questions for low-confidence items

**Output:** Confirmed ingredient list

---

#### **Step 3: User Preference Collection**
**User Action:** Answers quick preference questions
**System Action:**
- Presents interactive selection widgets
- Questions asked:
  1. **Cuisine preference?** [North Indian | South Indian | East Indian | West Indian | Any]
  2. **How much time do you have?** [<20 min | <45 min | <90 min | No limit]
  3. **What meal?** [Breakfast | Lunch | Dinner | Snack]
  4. **Dietary restrictions?** [Veg | Non-veg | Vegan | Jain | None]
  5. **Spice level?** [Mild | Medium | Spicy]

**Storage:**
- Saves to session context
- Optionally saves to user profile for future

**Output:** Preference object
```json
{
  "cuisine": "North Indian",
  "time_limit": 45,
  "meal_type": "Dinner",
  "dietary": "Vegetarian",
  "spice_level": "Medium",
  "skill_level": "Intermediate"
}
```

---

#### **Step 4: SQL Query Generation**
**User Action:** None (automated)

**System Action:**
```python
# AI generates SQL query dynamically
context = {
  "ingredients": ["potato", "cauliflower", "paneer"],
  "preferences": {
    "cuisine": "North Indian",
    "time_limit": 45,
    "dietary": "Vegetarian"
  }
}

prompt = f"""
Generate a SQLite query to find recipes matching:
- Main ingredients: {context['ingredients']}
- Cuisine: {context['preferences']['cuisine']}
- Max cooking time: {context['preferences']['time_limit']} minutes
- Dietary: {context['preferences']['dietary']}

Database schema:
- Table: recipes
- Columns: recipe (string), ingredients (string), instruction (string)

Rules:
1. Main ingredients MUST be present (strict matching)
2. Assume common spices available (don't filter for them)
3. Use LIKE for flexible matching
4. Calculate match score favoring more ingredient matches
5. Order by match score DESC
6. Return top 10 results
"""

generated_sql = llm.generate(prompt)

# Sample Generated SQL
query = """
SELECT 
  recipe,
  ingredients,
  instruction,
  (
    CASE WHEN LOWER(ingredients) LIKE '%potato%' OR LOWER(ingredients) LIKE '%aloo%' THEN 10 ELSE 0 END +
    CASE WHEN LOWER(ingredients) LIKE '%cauliflower%' OR LOWER(ingredients) LIKE '%gobi%' THEN 10 ELSE 0 END +
    CASE WHEN LOWER(ingredients) LIKE '%paneer%' THEN 10 ELSE 0 END
  ) as match_score
FROM recipes
WHERE 
  (
    (LOWER(ingredients) LIKE '%potato%' OR LOWER(ingredients) LIKE '%aloo%') OR
    (LOWER(ingredients) LIKE '%cauliflower%' OR LOWER(ingredients) LIKE '%gobi%') OR
    LOWER(ingredients) LIKE '%paneer%'
  )
  AND LOWER(recipe) LIKE '%north indian%'
  AND LOWER(ingredients) NOT LIKE '%chicken%'
  AND LOWER(ingredients) NOT LIKE '%mutton%'
  AND LENGTH(instruction) < 2000
ORDER BY match_score DESC
LIMIT 10;
"""
```

**Output:** Executable SQL query

---

#### **Step 5: Recipe Retrieval**
**User Action:** None (automated)

**System Action:**
```python
# Execute query against SQLite database
import sqlite3

conn = sqlite3.connect('recipes.db')
cursor = conn.cursor()

results = cursor.execute(generated_sql).fetchall()
conn.close()

# Sample Results
[
  {
    "recipe": "Aloo Gobi",
    "ingredients": "3 potatoes, 1 cauliflower, onion, tomato, turmeric, cumin...",
    "instruction": "Heat oil, add cumin seeds...",
    "match_score": 20
  },
  {
    "recipe": "Aloo Paneer Curry",
    "ingredients": "2 potatoes, 200g paneer, onion, tomato, cream...",
    "instruction": "Cut paneer into cubes...",
    "match_score": 20
  },
  {
    "recipe": "Gobi Paratha",
    "ingredients": "1 cauliflower, wheat flour, spices...",
    "instruction": "Grate cauliflower, mix with spices...",
    "match_score": 10
  }
]
```

**Output:** List of matching recipes

---

#### **Step 6: Gap Analysis**
**User Action:** None (automated)

**System Action:**
```python
def analyze_recipe_gaps(recipe_ingredients, user_ingredients):
    """
    Parse recipe ingredients and categorize based on availability
    """
    # Parse ingredient string
    recipe_items = parse_ingredients(recipe_ingredients)
    # Example: ["potato", "cauliflower", "onion", "tomato", "turmeric", "cumin", "garam masala"]
    
    # Categorize
    assumed_available = [
        "salt", "oil", "ghee", "water",
        "turmeric", "cumin", "coriander powder", "red chili powder",
        "mustard seeds", "garam masala",
        "onion", "tomato", "ginger", "garlic", "green chili"
    ]
    
    have = []
    missing_critical = []
    missing_optional = []
    
    for item in recipe_items:
        if item in user_ingredients:
            have.append(item)
        elif item in assumed_available:
            # Don't show to user
            continue
        else:
            # Check if critical or optional
            if is_main_ingredient(item):
                missing_critical.append(item)
            else:
                missing_optional.append(item)
    
    return {
        "have": have,
        "missing_critical": missing_critical,
        "missing_optional": missing_optional,
        "readiness": "READY" if len(missing_critical) == 0 else "NEED_SHOPPING"
    }

# Apply to all recipes
analyzed_recipes = []
for recipe in results:
    gap_analysis = analyze_recipe_gaps(recipe['ingredients'], user_ingredients)
    analyzed_recipes.append({
        **recipe,
        **gap_analysis
    })

# Sort by readiness
analyzed_recipes.sort(key=lambda x: (
    0 if x['readiness'] == 'READY' else 1,
    len(x['missing_critical']),
    -x['match_score']
))
```

**Output:** Recipes with gap analysis

---

#### **Step 7: Recipe Presentation**
**User Action:** Reviews recommendations

**System Action:**
- Groups recipes into tiers:
  - **🎯 Ready to Cook** (0 missing critical items)
  - **🛒 Almost There** (1-2 missing items)
  - **🛍️ Worth Shopping For** (3+ missing items)

**Display Format:**
```
🎯 READY TO COOK

1. Aloo Gobi
   ✅ You have: Potato, Cauliflower
   ✅ Assumed: Onion, tomato, cumin, turmeric
   ⚠️ Optional: Garam masala (enhances flavor)
   ⏱️ Time: 30 min | 🌶️ Spice: Medium | 👨‍🍳 Easy
   [View Recipe] [Ask Questions]

2. Aloo Paneer Curry
   ✅ You have: Potato, Paneer
   ✅ Assumed: Basic spices
   ⚠️ Optional: Cream (makes it rich)
   ⏱️ Time: 35 min | 🌶️ Spice: Medium | 👨‍🍳 Medium
   [View Recipe] [Ask Questions]

---

🛒 ALMOST THERE

3. Gobi Paratha
   ✅ You have: Cauliflower
   ❌ Need: Wheat flour (atta) - likely already in pantry
   ⏱️ Time: 40 min | 🌶️ Spice: Mild | 👨‍🍳 Medium
   [View Recipe]
```

**Output:** User-friendly recipe recommendations

---

#### **Step 8: Conversational Support**
**User Action:** Clicks "View Recipe" or asks questions

**System Action (Recipe View):**
```
📝 ALOO GOBI RECIPE

Ingredients:
✅ 3 medium potatoes (you have)
✅ 1 small cauliflower (you have)
✅ 1 onion, chopped (assumed available)
✅ 2 tomatoes, chopped (assumed available)
✅ Spices: turmeric, cumin, coriander (assumed available)
⚠️ 1 tsp garam masala (optional - adds aroma)

Instructions:
1️⃣ Prep (5 min)
   - Cut potatoes and cauliflower into florets
   - Soak in salted water to reduce bitterness
   
2️⃣ Tempering (2 min)
   - Heat 2 tbsp oil in kadai
   - Add 1 tsp cumin seeds, let splutter
   
3️⃣ Cooking (20 min)
   - Add onions, cook till golden
   - Add tomatoes, cook till soft
   - Add turmeric, coriander powder, salt
   - Add vegetables, mix well
   - Cover and cook on medium heat
   
4️⃣ Finishing (3 min)
   - Check if vegetables are tender
   - Add garam masala
   - Garnish with coriander leaves

💡 Pro Tips:
- Don't add water - vegetables release moisture
- Stir occasionally to prevent sticking
- For softer texture, pressure cook for 1 whistle

⏱️ Total Time: 30 minutes
🍽️ Serves: 4 people

[Start Cooking Mode] [Modify Recipe] [Find Alternatives]
```

**System Action (Chat Interface):**

**User:** "Can I make this in a pressure cooker?"

**AI Response:**
```
Yes! Pressure cooker method for Aloo Gobi:

1. Do the tempering same way (cumin in oil)
2. Add onions, tomatoes, and spices
3. Add vegetables + 1/4 cup water
4. Pressure cook for 1 whistle
5. Release pressure naturally (5 min)

⏱️ Saves 10 minutes! Total time: ~20 min

Note: Vegetables may be slightly softer than kadai method.
```

---

**User:** "I don't have cauliflower anymore"

**AI Response:**
```
No problem! Here's what you can make with just potatoes:

🎯 Ready to Cook:
1. Jeera Aloo (Cumin Potatoes) - 15 min
2. Aloo Bhaji (Spiced Potato Stir-fry) - 20 min
3. Batata Vada (Potato Fritters) - 30 min

Or if you have paneer:
4. Aloo Paneer Curry - 35 min

Which one interests you?
```

---

**User:** "Make it less spicy"

**AI Response:**
```
To make Aloo Gobi mild:

🌶️ Reduce red chili powder: 1 tsp → 1/4 tsp
🌶️ Skip green chilies entirely
🥛 Add 2-3 tbsp yogurt while cooking (cools heat + adds tang)
🍅 Use more tomatoes (natural sweetness balances)

Everything else stays the same! Your family will love it 😊

Want me to show the updated ingredient list?
```

**Output:** Context-aware conversational support

---

## Database Design

### SQLite Schema

#### **Table: recipes**
```sql
CREATE TABLE recipes (
    recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe TEXT NOT NULL,              -- Recipe name
    ingredients TEXT NOT NULL,          -- Comma-separated ingredient list
    instruction TEXT NOT NULL,          -- Cooking instructions
    
    
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster search
CREATE INDEX idx_ingredients ON recipes(ingredients);
CREATE INDEX idx_recipe_name ON recipes(recipe);

-- Full-text search index (for advanced search)
CREATE VIRTUAL TABLE recipes_fts USING fts5(
    recipe, 
    ingredients, 
    content=recipe
);
```

### Sample Data

```sql
INSERT INTO recipes (recipe, ingredients, instruction, cuisine_type, meal_type, cooking_time, difficulty, spice_level, dietary_type, tags) VALUES

('Aloo Gobi', 
 '3 potatoes, 1 cauliflower, 1 onion - chopped, 2 tomatoes - chopped, 1 tsp turmeric, 1 tsp cumin, 1 tsp coriander powder, 1 tsp red chili, 1 tsp garam masala, 2 tbsp oil, salt to taste',
 'Heat oil, add cumin seeds. Add onions, cook golden. Add tomatoes and spices. Add vegetables, cover and cook 20 min.',
 'North Indian',
 'Lunch,Dinner',
 30,
 'Easy',
 'Medium',
 'Vegetarian',
 'comfort-food,everyday,potato,cauliflower'),

('Masala Karela Recipe',
 '6 Karela (Bitter Gourd/ Pavakkai) - deseeded, Salt - to taste, 1 Onion - sliced, 1 tsp turmeric, 1 tsp cumin, oil',
 'To begin making the Masala Karela Recipe, de-seed the karela and slice. Do not remove the skin. Heat oil, add cumin, then onions. Add karela, spices and cook covered till tender.',
 'North Indian',
 'Lunch,Dinner',
 25,
 'Easy',
 'Medium',
 'Vegetarian',
 'bitter-gourd,karela,healthy'),

('Spicy Tomato Rice (Recipe)',
 '2 cups rice - cooked, 3 tomatoes, 3 teaspoons BC Belle Bhat powder, salt to taste, 1 onion, curry leaves, mustard seeds, oil',
 'To make tomato puliogere, first cut the tomatoes. Now put in a mixer grinder and make a puree. Heat oil, add mustard seeds and curry leaves. Add onions, cook. Add tomato puree and BC Belle powder. Mix with cooked rice.',
 'South Indian',
 'Lunch',
 20,
 'Easy',
 'Spicy',
 'Vegetarian',
 'quick,rice,tomato,south-indian');
```

### Database Operations

#### **Initialization Script**
```python
# init_database.py
import sqlite3
import pandas as pd

def initialize_database():
    """Create and populate SQLite database from CSV"""
    
    # Load recipe data
    df = pd.read_csv('train_recipes.csv')
    
    # Create database connection
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instruction TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert data
    df.to_sql('recipes', conn, if_exists='replace', index=False)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ingredients ON recipes(ingredients)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_recipe ON recipes(recipe)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized with {len(df)} recipes")

if __name__ == "__main__":
    initialize_database()
```

#### **Query Helper Functions**
```python
# database.py
import sqlite3
from typing import List, Dict, Any

class RecipeDatabase:
    def __init__(self, db_path='recipes.db'):
        self.db_path = db_path
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        results = cursor.execute(query).fetchall()
        conn.close()
        
        # Convert to list of dicts
        return [dict(row) for row in results]
    
    def search_by_ingredients(self, ingredients: List[str], limit: int = 10) -> List[Dict]:
        """Search recipes by ingredients"""
        # Build LIKE conditions
        conditions = []
        for ing in ingredients:
            conditions.append(f"LOWER(ingredients) LIKE '%{ing.lower()}%'")
        
        where_clause = " OR ".join(conditions)
        
        query = f"""
        SELECT recipe, ingredients, instruction
        FROM recipes
        WHERE {where_clause}
        LIMIT {limit}
        """
        
        return self.execute_query(query)
    
    def get_recipe_by_name(self, recipe_name: str) -> Dict:
        """Get specific recipe by name"""
        query = f"""
        SELECT * FROM recipes
        WHERE LOWER(recipe) = LOWER('{recipe_name}')
        LIMIT 1
        """
        
        results = self.execute_query(query)
        return results[0] if results else None
```

---

## AI/ML Components

### Component 1: Vision AI (Ingredient Recognition)

**Model:** GPT-4 Vision / Claude 3.5 Sonnet / Gemini Pro Vision

**Input:**
- 2-3 images (JPEG/PNG)
- Max resolution: 2048x2048
- Max file size: 5MB per image

**Prompt Template:**
```
You are an expert at identifying Indian cooking ingredients from photos.

Analyze these images and identify all visible ingredients used in Indian cooking.

For each ingredient, provide:
1. name: Common name in English (e.g., "potato", not "aloo")
2. alternate_names: Array of regional variations ["aloo", "batata"]
3. category: One of [vegetable, protein, spice, grain, dairy, other]
4. confidence: Float 0.0-1.0
5. quantity_estimate: Approximate quantity if visible (e.g., "4-5 medium pieces")
6. notes: Any relevant observations

Special instructions:
- For packaged items, use OCR to read labels
- If uncertain, mark confidence < 0.7 and add note
- Handle multiple items of same ingredient (e.g., "3 onions")
- Recognize both fresh and packaged ingredients

Output as JSON with this structure:
{
  "identified_ingredients": [...],
  "packaged_items": [...],
  "uncertain_items": [...]
}
```

**Output Format:**
```json
{
  "identified_ingredients": [
    {
      "name": "potato",
      "alternate_names": ["aloo", "batata"],
      "category": "vegetable",
      "confidence": 0.95,
      "quantity_estimate": "4-5 medium pieces",
      "notes": "Clear view, good lighting"
    }
  ],
  "packaged_items": [
    {
      "name": "Everest Garam Masala",
      "category": "spice",
      "confidence": 0.88,
      "notes": "Label partially visible"
    }
  ],
  "uncertain_items": [
    {
      "possible_names": ["coriander leaves", "curry leaves"],
      "category": "herb",
      "confidence": 0.55,
      "notes": "Too far from camera, need clarification"
    }
  ]
}
```

**Error Handling:**
- Blurry images → Request clarification
- No ingredients visible → Ask user to retake
- Multiple items unclear → Ask specific questions

---

### Component 2: SQL Query Generator

**Model:** gemini-2.5-flash

**Input:**
- User ingredients list
- User preferences object
- Database schema

**Prompt Template:**
```
You are a SQL expert specializing in recipe search queries.

Generate an optimized SQLite query to find matching recipes based on:

User's Ingredients: {ingredients}
Preferences: {preferences}

Database Schema:
Table: recipes
Columns: recipe (TEXT), ingredients (TEXT), instruction (TEXT)

Query Requirements:
1. Main ingredients MUST be present (use OR for alternate names)
   - Example: "potato" OR "aloo" OR "batata"
2. Assume common Indian spices/aromatics are available (don't filter):
   - Spices: turmeric, cumin, coriander powder, red chili, mustard seeds, garam masala
   - Aromatics: onion, tomato, ginger, garlic, green chili
   - Basics: salt, oil, ghee
3. Exclude recipes with ingredients user definitely doesn't have:
   - If user has only veg ingredients, exclude chicken/mutton/fish
4. Calculate match_score favoring recipes with more ingredient matches
5. Consider cooking time if specified: LENGTH(instruction) as proxy (<800 chars ≈ quick)
6. Order by match_score DESC
7. LIMIT 10 results
8. Use LOWER() for case-insensitive matching

Generate ONLY the SQL query, no explanations.
```

**Sample Input:**
```python
ingredients = ["potato", "cauliflower", "paneer"]
preferences = {
    "cuisine": "North Indian",
    "time_limit": 45,
    "dietary": "Vegetarian"
}
```

**Sample Output:**
```sql
SELECT 
  recipe,
  ingredients,
  instruction,
  (
    CASE WHEN LOWER(ingredients) LIKE '%potato%' OR LOWER(ingredients) LIKE '%aloo%' THEN 10 ELSE 0 END +
    CASE WHEN LOWER(ingredients) LIKE '%cauliflower%' OR LOWER(ingredients) LIKE '%gobi%' THEN 10 ELSE 0 END +
    CASE WHEN LOWER(ingredients) LIKE '%paneer%' THEN 10 ELSE 0 END
  ) as match_score
FROM recipes
WHERE 
  (
    (LOWER(ingredients) LIKE '%potato%' OR LOWER(ingredients) LIKE '%aloo%') OR
    (LOWER(ingredients) LIKE '%cauliflower%' OR LOWER(ingredients) LIKE '%gobi%') OR
    LOWER(ingredients) LIKE '%paneer%'
  )
  AND (LOWER(recipe) LIKE '%north indian%' OR LOWER(ingredients) LIKE '%north%')
  AND LOWER(ingredients) NOT LIKE '%chicken%'
  AND LOWER(ingredients) NOT LIKE '%mutton%'
  AND LENGTH(instruction) < 2000
ORDER BY match_score DESC, LENGTH(instruction) ASC
LIMIT 10;
```

---

### Component 3: Conversational AI

**Model:** GPT-4 / Claude 3.5 Sonnet

**Context Management:**
```python
conversation_context = {
    "user_ingredients": ["potato", "cauliflower"],
    "selected_recipe": {
        "name": "Aloo Gobi",
        "ingredients": "...",
        "instruction": "..."
    },
    "preferences": {...},
    "conversation_history": [...]
}
```

**System Prompt:**
```
You are a helpful Indian cooking assistant. You help users cook recipes based on their available ingredients.

Current Context:
- User has: {user_ingredients}
- Currently discussing: {recipe_name}
- Recipe details: {recipe_data}

Your capabilities:
1. Answer questions about the recipe
2. Suggest modifications (reduce spice, change cooking method, etc.)
3. Provide substitutions for missing ingredients
4. Find alternative recipes if user changes mind
5. Explain cooking techniques

Guidelines:
- Be concise and practical
- Use emojis sparingly for clarity
- When suggesting alternatives, regenerate SQL query
- Always consider Indian cooking context
- If user wants different recipe, use their ingredients to search again
- Maintain friendly, encouraging tone

Respond naturally to user questions.
```

**Sample Interactions:**

**User:** "Can I skip garam masala?"

**Response:**
```
Yes, you can skip garam masala! The dish will still taste good.

To compensate:
• Add a pinch more cumin (adds warmth)
• Use a bay leaf while cooking (adds aroma)

Or make quick garam masala substitute:
• 1/2 tsp cumin powder
• 1/4 tsp coriander powder  
• Pinch of cinnamon

The recipe will work fine without it too! 👍
```

---

## User Experience Flow

### Flow 1: First-Time User (Complete Journey)

```
1. Landing Page
   ↓
   [Get Started] button
   ↓
2. Upload Instructions
   "Take 2-3 photos of your ingredients"
   [Upload Photos] or [Take Photo]
   ↓
3. Image Analysis
   Loading... "Analyzing your ingredients"
   ↓
4. Confirmation Screen
   "Is this correct?"
   ✅ Potato (4-5 pieces)
   ✅ Cauliflower (1 head)
   ❓ Is this coriander or curry leaves?
   [Confirm] [Edit] [Add More]
   ↓
5. Quick Preferences
   "Help us personalize"
   - Cuisine? [North/South/East/West/Any]
   - Time available? [<20/<45/<90/No limit]
   - Meal type? [Breakfast/Lunch/Dinner/Snack]
   [Skip for now] [Continue]
   ↓
6. Processing
   Loading... "Finding perfect recipes"
   ↓
7. Results Page
   
   🎯 READY TO COOK (2)
   [Aloo Gobi] [Aloo Paratha]
   
   🛒 ALMOST THERE (1)
   [Gobi Pakora] → Need: Chickpea flour
   
   🛍️ WORTH SHOPPING (1)
   [Aloo Tikki Chaat] → Need: 3 items
   
   ↓
8. Recipe Detail
   [User clicks "Aloo Gobi"]
   
   Full recipe display
   [Start Cooking] [Ask Question] [Find Alternative]
   ↓
9. Cooking Mode (Optional)
   Step-by-step with timers
   ↓
10. Feedback
    "How did it turn out?"
    ⭐⭐⭐⭐⭐
    [Share] [Save Recipe]
```

---

### Flow 2: Returning User (Quick Path)

```
1. Home Screen
   "Welcome back! Last cooked: Aloo Gobi"
   [Cook Again] [Find New Recipe]
   ↓
2. Quick Upload
   [Camera icon] - Tap to scan ingredients
   ↓
3. Auto-apply Saved Preferences
   Using: North Indian, <45 min, Dinner, Veg
   [Change Preferences]
   ↓
4. Instant Results
   (Skip preference questions)
   ↓
5. Recipe Selection
```

---

### Flow 3: Conversational Modification

```
User viewing "Aloo Gobi" recipe
↓
Types: "Can I use pressure cooker?"
↓
AI: "Yes! Here's how..."
↓
User: "Make it less spicy"
↓
AI: "Reduce red chili from 1 tsp to 1/4 tsp..."
↓
User: "Show updated ingredient list"
↓
AI: [Displays modified recipe]
↓
User: "Perfect! Let's cook this"
↓
[Start Cooking Mode]
```

---

## Technical Requirements

### Frontend Requirements

**Web Application:**
- **Framework:** React 18+ 
- **Styling:** Tailwind CSS
- **State Management:** React Context / Zustand
- **Image Handling:** react-dropzone for uploads
- **UI Components:** shadcn/ui or Material-UI



**Key Features:**
- Responsive design (mobile-first)
- Image preview before upload
- Loading states and progress indicators
- Error handling with user-friendly messages
- Accessibility (WCAG 2.1 AA)

---

### Backend Requirements

**Technology Stack:**
- **Language:** Python 3.10+
- **Framework:** FastAPI (async support)
- **Database:** SQLite 3.35+ (with FTS5 support)
- **AI/ML:** langchain
- **Image Processing:** Pillow (PIL)

**API Endpoints:**

```python
# API Structure

POST /api/upload-images
- Input: multipart/form-data with 2-3 images
- Output: {session_id, uploaded_count}

POST /api/analyze-ingredients
- Input: {session_id}
- Output: {identified_ingredients, uncertain_items}

POST /api/confirm-ingredients
- Input: {session_id, confirmed_ingredients, user_preferences}
- Output: {confirmation_status}

POST /api/get-recommendations
- Input: {session_id}
- Output: {ready_recipes, almost_recipes, shopping_recipes}

GET /api/recipe/{recipe_id}
- Output: {recipe_details, full_instructions}

POST /api/chat
- Input: {session_id, user_message, context}
- Output: {ai_response, updated_context}

POST /api/generate-sql
- Input: {ingredients, preferences}
- Output: {generated_query, execution_plan}

GET /api/execute-query
- Input: {query}
- Output: {results}
```

**Performance Targets:**
- Image upload: <2s
- Ingredient analysis: <3s
- SQL query generation: <1s
- Database query execution: <500ms
- Chat response: <2s
- Total time (upload → recommendations): <8s

---

### AI/ML Requirements

**Models:**

| Component | Model Options | Latency Target |
|-----------|---------------|----------------|
| Vision AI |gemini-2.5-flash | <3s |
| SQL Generation |gemini-2.5-flash | <1s |
| Conversational |gemini-2.5-flash | <2s |

**API Rate Limits:**
- Vision API: 50 requests/min
- Text API: 500 requests/min
- Implement queuing for burst traffic

**Cost Optimization:**
- Cache common ingredient recognitions
- Reuse SQL queries for similar ingredient sets
- Implement response caching for FAQs

---

### Database Requirements

**SQLite Configuration:**
```python
# Database settings
DATABASE_CONFIG = {
    'database': 'recipes.db',
    'timeout': 10,
    'check_same_thread': False,
    'isolation_level': None,  # Autocommit mode
}

# Optimization
PRAGMA settings:
- journal_mode = WAL  # Write-Ahead Logging
- synchronous = NORMAL
- cache_size = -64000  # 64MB cache
- temp_store = MEMORY
```

**Backup Strategy:**
- Daily automated backups
- Backup rotation (keep last 7 days)
- Export to JSON weekly

**Data Volume Estimates:**
- MVP: 500 recipes (~3-5 MB)
- Year 1: 2,000 recipes (~15-20 MB)
- Year 2: 5,000 recipes (~40-50 MB)

---



### Security Requirements

**Data Protection:**
- HTTPS only (TLS 1.3)
- Image sanitization (check file headers)
- SQL injection prevention (parameterized queries)
- Rate limiting per IP
- CORS configuration

**Privacy:**
- Images deleted after 24 hours
- No PII collection required
- Anonymous usage analytics
- GDPR/privacy policy compliance


## Success Metrics

### Primary Metrics

**User Engagement:**
- **DAU/MAU ratio:** Target >20%
- **Session duration:** Target >5 minutes
- **Recipes viewed per session:** Target 3+
- **Return rate:** Target >40% within 7 days

**Product Success:**
- **Recipe selection rate:** >60% (users pick at least 1 recipe)
- **Cooking completion:** >50% (users start cooking mode)
- **Satisfaction score:** >4.2/5 average rating

**Technical Performance:**
- **Ingredient recognition accuracy:** >85%
- **Recipe match relevance:** >80% user satisfaction
- **System uptime:** >99.5%
- **API response time:** <3s for 95th percentile

---

### Secondary Metrics

**User Behavior:**
- Photos uploaded per session
- Preference questions answered
- Chat interactions per recipe
- Recipe modifications requested
- Alternative recipes explored

**Business Metrics:**
- User acquisition cost (CAC)
- Customer lifetime value (LTV)
- Organic vs paid user ratio
- Referral rate

-

## Future Enhancements

### Phase 2 Features (3-6 months)

**1. Cooking Mode Enhancements**
- Voice commands while cooking
- Step-by-step timers
- Video tutorials integration
- Hands-free navigation

**2. Social Features**
- Share recipes with friends
- Family recipe collaboration
- Community ratings and reviews
- Photo sharing of cooked dishes

**3. Smart Pantry**
- Save regular pantry items
- Ingredient expiry tracking
- Shopping list generation
- Pantry-based auto-suggestions

**4. Personalization**
- AI learns user taste preferences
- Seasonal ingredient suggestions
- Regional cuisine deep-dives
- Skill level progression tracking

---

### Phase 3 Features (6-12 months)

**1. Meal Planning**
- Weekly meal planner
- Batch cooking suggestions
- Leftover management
- Nutritional planning

**2. Recipe Contributions**
- User-submitted recipes
- Family recipe preservation
- Community curation
- Recipe variations tracking

**3. E-commerce Integration**
- Ingredient delivery (Zepto, Blinkit, Swiggy Instamart)
- Price comparison
- Bulk buying suggestions
- Farmer's market locator

**4. Advanced AI**
- Image-based recipe generation (photo → recipe)
- Dietary restriction auto-detection
- Allergen warnings
- Nutritional analysis

---

### Long-term Vision (12+ months)

**1. Multi-language Support**
- Hindi, Tamil, Telugu, Bengali, Marathi
- Regional recipe names
- Voice input in native languages

**2. Hardware Integration**
- Smart kitchen appliance integration
- IoT-enabled cooking guidance
- Recipe → appliance automation

**3. Video Content**
- Live cooking classes
- Celebrity chef collaborations
- Regional cooking shows
- Technique masterclasses

**4. Global Expansion**
- Adapt for other cuisines
- Diaspora-focused features
- Cultural cooking education

---

## Risks & Mitigation

### Technical Risks

**Risk 1: Ingredient Recognition Accuracy**
- **Impact:** High (Core feature)
- **Probability:** Medium
- **Mitigation:**
  - Multi-model ensemble (GPT-4V + Claude)
  - User confirmation step
  - Continuous model fine-tuning
  - Fallback to manual entry

**Risk 2: Database Scalability**
- **Impact:** Medium
- **Probability:** Low (with SQLite)
- **Mitigation:**
  - Monitor query performance
  - Implement caching layer
  - Have PostgreSQL migration plan ready
  - Regular performance testing

**Risk 3: API Cost Overruns**
- **Impact:** High (Business viability)
- **Probability:** Medium
- **Mitigation:**
  - Response caching (80% hit rate target)
  - Rate limiting per user
  - Fallback to cheaper models for simple queries
  - Cost monitoring alerts

---

### Product Risks

**Risk 1: Low User Engagement**
- **Impact:** High
- **Probability:** Medium
- **Mitigation:**
  - Quick time-to-value (<2 min first recipe)
  - Gamification (cooking streaks)
  - Push notifications for expiring ingredients
  - Social sharing features

**Risk 2: Recipe Quality/Diversity**
- **Impact:** Medium
- **Probability:** Low
- **Mitigation:**
  - Curate from trusted sources
  - Community testing before launch
  - Regional recipe expert review
  - Regular content updates

**Risk 3: User Privacy Concerns**
- **Impact:** High
- **Probability:** Low
- **Mitigation:**
  - Clear privacy policy
  - Auto-delete images after 24h
  - No personal data requirements
  - Transparent data usage

---

### Business Risks

**Risk 1: Competition**
- **Impact:** Medium
- **Probability:** High
- **Mitigation:**
  - Focus on Indian cuisine depth
  - Superior AI matching algorithm
  - Community building
  - Rapid feature iteration

**Risk 2: Monetization Challenges**
- **Impact:** High
- **Probability:** Medium
- **Mitigation:**
  - Freemium model planning
  - B2B partnerships (grocery delivery)
  - Sponsored recipes (ethical brands)
  - Premium features (meal planning)

---

## Appendices

### Appendix A: Assumed Available Ingredients

These ingredients are assumed to be in most Indian households and are NOT checked during matching:

**Spices:**
- Turmeric powder (haldi)
- Cumin seeds & powder (jeera)
- Coriander powder (dhania)
- Red chili powder (lal mirch)
- Mustard seeds (rai/sarson)
- Garam masala
- Black pepper
- Cinnamon (dalchini)
- Cloves (laung)
- Cardamom (elaichi)

**Aromatics:**
- Onions
- Tomatoes
- Ginger
- Garlic
- Green chilies
- Curry leaves (South India)

**Basics:**
- Salt
- Cooking oil
- Ghee
- Water
- Sugar

---

### Appendix B: Regional Name Mapping

| English | Hindi | Tamil | Telugu | Bengali | Marathi |
|---------|-------|-------|--------|---------|---------|
| Potato | Aloo | Urulaikizhangu | Bangaladumpa | Aloo | Batata |
| Cauliflower | Gobi | Cauliflower | Cauliflower | Phulkopi | Phulgobhi |
| Bitter Gourd | Karela | Pavakkai | Kakarakaya | Korola | Karle |
| Eggplant | Baingan | Kathirikai | Vankaya | Begun | Vangi |
| Okra | Bhindi | Vendakkai | Bendakaya | Dharosh | Bhendi |
| Spinach | Palak | Keerai | Bachhali | Palong shak | Palak |

---

### Appendix C: Development Roadmap

**MVP (Month 1-2):**
- ✅ Core workflow implementation
- ✅ SQLite database setup
- ✅ Basic UI (web)
- ✅ Vision AI integration
- ✅ SQL query generation
- ✅ 100-200 recipes

**Beta (Month 3):**
- ✅ User testing (50 users)
- ✅ Bug fixes and optimizations
- ✅ Recipe expansion (500 recipes)
- ✅ Analytics integration
- ✅ Conversational AI polish

**Launch (Month 4):**
- ✅ Public release
- ✅ Marketing campaign
- ✅ App store submission (mobile)
- ✅ Press outreach
- ✅ Community building

**Post-Launch (Month 5-6):**
- ✅ Feature iterations based on feedback
- ✅ Performance optimizations
- ✅ Recipe database expansion (1000+)
- ✅ Phase 2 feature planning

---

### Appendix D: Glossary

**Agentic Workflow:** AI system where multiple specialized agents collaborate to complete complex tasks

**Gap Analysis:** Process of identifying missing ingredients required for a recipe

**Main Ingredients:** Primary vegetables, proteins, or grains that define a dish (e.g., potato in Aloo Gobi)

**Match Score:** Numerical value indicating how well a recipe matches available ingredients

**RAG (Retrieval Augmented Generation):** AI technique combining database retrieval with language model generation

**SQLite:** Lightweight, serverless database engine (file-based)

**Text-to-SQL:** AI capability to convert natural language to SQL queries

**Vision AI:** Machine learning model that analyzes and understands images

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Feb 9, 2026 | Product Team | Initial draft |

---

**END OF DOCUMENT**
