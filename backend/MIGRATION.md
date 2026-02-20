# RasoiAI Database Migration Run-Book

## Prerequisites

Set `DATABASE_URL` in `backend/.env`:

```
DATABASE_URL=postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/dbname?sslmode=require
```

## Setup Steps

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Load recipes from CSV into Neon

```bash
python init_database.py
```

### 3. (Optional) Migrate existing SQLite data

```bash
python scripts/migrate_data.py --dry-run   # validate first
python scripts/migrate_data.py             # run migration
```

### 4. Start the app

```bash
uvicorn app.main:app --reload
```

### 5. Verify

```bash
curl http://localhost:8000/db-test
curl http://localhost:8000/api/recipes?limit=3
```
