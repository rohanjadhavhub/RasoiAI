You are working inside an existing, production-ready SaaS codebase with:

Frontend: React
Backend: FastAPI
ORM: SQLAlchemy (sync)
Current DB: SQLite (local file)
Target DB: Neon PostgreSQL (serverless, requires SSL)

Before making any changes, read the existing files — especially database.py, models.py, and any existing alembic/ directory. Do not assume structure; infer it from the code.

OBJECTIVE
Migrate the database layer from SQLite → Neon PostgreSQL with zero breaking changes to business logic, models, or API contracts.

HARD CONSTRAINTS

Do not modify model field names, relationships, or API behavior
Do not drop or manually recreate schema — use Alembic exclusively
Do not hardcode credentials anywhere — all secrets via environment variables
Do not explain concepts — write and modify files directly
All changes must be backward-compatible: SQLite still works locally if DATABASE_URL is absent


TASKS — execute in order
1. Audit existing database.py
Read the file first. Then refactor the engine/session setup to:

Use DATABASE_URL env var if present → PostgreSQL via psycopg2
Fall back to SQLite if absent
Apply these engine kwargs conditionally:

python# PostgreSQL
create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args={"sslmode": "require", "connect_timeout": 10}
)

# SQLite fallback
create_engine(
    "sqlite:///./app.db",
    connect_args={"check_same_thread": False}
)
2. Audit models for SQLite-specific patterns
Scan all SQLAlchemy models and fix any of the following for PostgreSQL compatibility:

autoincrement=True on non-integer PKs → remove or replace
DateTime defaults using datetime.now (not datetime.utcnow) → wrap in func.now() or use server_default
JSON columns → ensure using sqlalchemy.JSON (not String)
Boolean columns → ensure not stored as integers
Any PRAGMA or SQLite-specific raw SQL → remove

Report each change made with a one-line comment in the code.
3. Set up Alembic (if not already initialized)

Run alembic init alembic only if no alembic/ directory exists
Update alembic/env.py to:

Import Base from your models
Set target_metadata = Base.metadata
Read DATABASE_URL from environment (same logic as database.py)


Update alembic.ini to remove hardcoded sqlalchemy.url (move to env.py)

4. Generate and validate migration
Run:
bashalembic revision --autogenerate -m "migrate_sqlite_to_postgres"
alembic upgrade head
```
If there are errors, fix them before proceeding. Do not use `--sql` mode.

**5. Write a data migration script: `scripts/migrate_data.py`**
This script must:
- Connect to SQLite source and Neon PostgreSQL target simultaneously
- Migrate tables in dependency order (parents before children, respecting FK constraints)
- Preserve all primary keys and foreign key relationships
- Use `INSERT ... ON CONFLICT DO NOTHING` to be safe on reruns
- Print progress per table: `✓ users: 142 rows migrated`
- Accept `--dry-run` flag to validate without writing

**6. Update `requirements.txt`**
Add only what is missing:
```
psycopg2-binary>=2.9.9
alembic>=1.13.0
Do not add duplicates. Do not change existing pinned versions unless there's a conflict.
7. Produce a MIGRATION.md run-book (brief, commands only):
markdown## Local Dev
DATABASE_URL not set → SQLite used automatically

## Production Migration Steps
1. Set DATABASE_URL in environment
2. alembic upgrade head
3. python scripts/migrate_data.py --dry-run
4. python scripts/migrate_data.py
5. Verify row counts match
```

---

**OUTPUT FORMAT**

For each file modified or created, output it in full using this format:
```
### FILE: path/to/file.py
```python
# full file contents
```
Do not truncate files. Do not use placeholder comments like # ... rest of file unchanged.