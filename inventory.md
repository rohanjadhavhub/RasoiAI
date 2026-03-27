You are a senior full-stack developer working on **RasoiAI**, a smart kitchen assistant.
The `remoteScan` feature is already complete and working. It captures a photo via RPi camera,
saves it to `captures/latest.jpg`, and passes it to `vision.py` which returns a list of
identified ingredients using Gemini Vision.

## What you must build now — Inventory + Expiry System

---

### 1. DATABASE — Inventory Table

Using **SQLite + SQLAlchemy** (async, with `aiosqlite`), create an `inventory` table:
```sql
inventory (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id      TEXT    NOT NULL,
  ingredient   TEXT    NOT NULL,          -- normalized lowercase, e.g. "tomato"
  first_seen   DATETIME NOT NULL,         -- UTC timestamp of FIRST detection ever
  last_seen    DATETIME NOT NULL,         -- UTC timestamp of most recent scan
  expiry_date  DATETIME NOT NULL,         -- first_seen + shelf_life_days
  is_expired   BOOLEAN  NOT NULL DEFAULT 0,
  scan_count   INTEGER  NOT NULL DEFAULT 1
)
```

Rules:
- Unique constraint on `(user_id, ingredient, DATE(first_seen))` — one row per ingredient per day per user
- On re-scan of the same ingredient same day: UPDATE `last_seen`, `scan_count` only — NEVER touch `first_seen` or `expiry_date`
- On re-scan of same ingredient on a NEW day: INSERT a fresh row (new first_seen, new expiry)
- `is_expired` is a computed flag: set to 1 when `NOW() > expiry_date` (update on every read)

---

### 2. EXPIRY HARDCODED REFERENCE SHEET

Create `expiry_config.py` as the single source of truth. Include AT LEAST these items:
```python
SHELF_LIFE_DAYS: dict[str, int] = {
    # Vegetables
    "tomato": 3,
    "potato": 14,
    "onion": 21,
    "garlic": 30,
    "spinach": 3,
    "carrot": 14,
    "capsicum": 5,
    "broccoli": 4,
    "cauliflower": 5,
    "cucumber": 5,
    "ginger": 14,
    "coriander": 3,
    "green chili": 5,
    "cabbage": 7,
    "beetroot": 10,
    "peas": 3,
    "corn": 2,
    "eggplant": 4,
    # Fruits
    "banana": 3,
    "apple": 14,
    "lemon": 14,
    "mango": 4,
    "papaya": 3,
    "orange": 10,
    "grape": 5,
    "watermelon": 5,
    # Dairy
    "milk": 3,
    "paneer": 4,
    "curd": 3,
    "butter": 30,
    "cheese": 14,
    "egg": 21,
    # Proteins
    "chicken": 2,
    "fish": 1,
    "mutton": 2,
    # Staples / Pantry
    "bread": 4,
    "rice": 180,
    "lentils": 180,
    "flour": 90,
    # Default fallback
    "__default__": 5,
}
```

Add a helper:
```python
def get_shelf_life(ingredient: str) -> int:
    key = ingredient.strip().lower()
    return SHELF_LIFE_DAYS.get(key, SHELF_LIFE_DAYS["__default__"])
```

---

### 3. BACKEND — New API Endpoints

Add to the existing FastAPI app under prefix `/api/inventory`:

**`POST /api/inventory/update`**
- Body: `{ user_id: str, ingredients: list[str] }`
- For each ingredient: apply the upsert logic above using `expiry_config.get_shelf_life()`
- Returns: full current inventory for that user (list of inventory rows, with `is_expired` refreshed)

**`GET /api/inventory/{user_id}`**
- Returns all inventory rows for the user, sorted by `expiry_date ASC`
- Refreshes `is_expired` on each row before returning
- Groups response into two lists: `{ "fresh": [...], "expired": [...] }`

**`DELETE /api/inventory/{user_id}/{ingredient_id}`**
- Hard deletes a row (user manually removes an item)

Wire the scan flow: after `vision.py` returns detected ingredients, automatically call the
inventory update logic so `/api/camera/scan` response includes the updated inventory.

---

### 4. INTEGRATION — Update the Scan Endpoint

Modify `POST /api/camera/scan` to:
1. Capture image (existing)
2. Pass to `vision.py` → get `detected: list[str]`
3. Call inventory upsert for each detected ingredient
4. Return combined response:
```json
{
  "success": true,
  "image_path": "captures/latest.jpg",
  "detected_ingredients": ["tomato", "onion", "ginger"],
  "inventory": {
    "fresh": [ ...rows... ],
    "expired": [ ...rows... ]
  }
}
```

---

### 5. FRONTEND — New Inventory Page

After a successful scan response, navigate to (or render) an **Inventory Page**.
Build it as a single clean HTML page or React component (`inventory.jsx`).

Requirements:

**Header section:**
- Title: "Kitchen Inventory"
- Subtitle: last scan timestamp + count of items detected this scan (highlighted in a badge)

**Detected This Scan strip:**
- Horizontal pill-row of the ingredients just detected, each with its expiry countdown
  e.g. `🍅 Tomato · expires in 3d`

**Inventory Table — two sections:**

FRESH (green header):
| Ingredient | First Seen | Expires On | Days Left | Scans |
|---|---|---|---|---|
| Tomato | Today 10:32am | Dec 15 | 3 days | 2 |

EXPIRED (red header, muted rows):
| Ingredient | Expired On | Days Overdue | Action |
|---|---|---|---|
| Spinach | Dec 10 | 2 days ago | [Remove] |

**Design rules:**
- Use a warm, food-friendly color palette — saffron/turmeric yellows, fresh greens, clay reds
- "Days Left" column: green if >3 days, amber if 1–3 days, red if expired
- Each row has a subtle progress bar showing time remaining vs total shelf life
- "Remove" button on expired rows calls `DELETE /api/inventory/{user_id}/{id}`
- Empty state: if no inventory yet, show "No items scanned yet. Tap Scan to begin."
- Responsive, mobile-first (RPi is accessed from phones in the kitchen)

---

### 6. FILE STRUCTURE
work in exixting backend and frontend folders

---

### Technical constraints
- Python 3.11+, FastAPI, SQLAlchemy 2.x async, aiosqlite
- Use `pathlib`, type hints, and Pydantic v2 response models throughout
- All datetimes stored and compared in UTC (`datetime.utcnow()`)
- Ingredient names normalized to lowercase + stripped before any DB operation
- All files modular and clean — no logic in `__init__.py`
- The expiry reference sheet (`expiry_config.py`) must be the ONLY place shelf life is defined