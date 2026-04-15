# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RasoiAI is an AI-powered Indian recipe recommendation system. Users upload photos of ingredients, Gemini Vision identifies them, and the system recommends matching recipes from a PostgreSQL database of ~6500 Indian recipes. Includes a LangGraph-powered chatbot ("Annapurna") with persistent conversation memory.

## Architecture

Three independent components in a single repo (not a monorepo — no workspace tooling):

- **`backend/`** — Python FastAPI API server (port 8000)
- **`frontend/`** — React 19 + Vite 7 SPA (port 5173)
- **`rasoi_camera/`** — Standalone FastAPI app for Raspberry Pi camera-based ingredient scanning (port 8001)

### Backend structure (`backend/app/`)

- `core/config.py` — Pydantic Settings, reads from `backend/.env`. Access via `get_settings()` (LRU-cached singleton).
- `routes/` — FastAPI routers, all mounted under `/api` prefix in `main.py`. Auth routes under `/api/auth`.
- `services/` — Business logic:
  - `vision.py` — Gemini Vision ingredient recognition (uses `google-genai` SDK directly, not LangChain)
  - `sql_generator.py` — Gemini generates PostgreSQL queries to search recipes by ingredients. Falls back to basic LIKE queries without API key.
  - `chat_graph.py` — LangGraph `StateGraph` with three nodes: `chat_node` → `summarize` → `extract_preferences`. Uses `AsyncPostgresSaver` checkpointer for cross-session memory. Checkpointer lifecycle managed via FastAPI startup/shutdown events.
  - `gap_analysis.py` — Scores recipe readiness based on available vs required ingredients
- `db/` — Direct `psycopg2` database access (no ORM). `recipe_db.py` for recipes, `user_db.py` for users/favourites/bookmarks/preferences. Access via `get_database()` / `get_user_database()`.
- `schemas/` — Pydantic v2 request/response models

### Frontend structure (`frontend/src/`)

- `main.jsx` — Entry point. Wraps app in `Auth0Provider` + `BrowserRouter`.
- `App.jsx` — Route definitions and header/nav. All routes are flat (no nesting).
- `pages/` — One JSX + one CSS file per page. Each page is self-contained.
- `services/api.js` — All API calls to the backend. Uses raw `fetch()`, no axios. Authenticated requests go through `authFetch()` helper which adds Bearer token.
- Styling is vanilla CSS (no Tailwind, no CSS-in-JS).

### RPi Camera (`rasoi_camera/`)

Runs independently on a Raspberry Pi. The frontend communicates with it via SSH tunnel (`localhost:8001`). Flow: capture image → Gemini Vision analysis → POST ingredients to main backend's `/api/remote-ingredients`.

## Development Commands

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # Dev server at localhost:5173
npm run build        # Production build to dist/
npm run lint         # ESLint
npm run preview      # Preview production build
```

### Database
```bash
cd backend
python init_database.py   # Seed recipes from indian_recipe_cleaned.csv into PostgreSQL
```

## Environment Variables

**`backend/.env`**: `GEMINI_API_KEY`, `DATABASE_URL` (Neon PostgreSQL), `AUTH0_DOMAIN`, `AUTH0_API_AUDIENCE`

**`frontend/.env`**: `VITE_AUTH0_DOMAIN`, `VITE_AUTH0_CLIENT_ID`, `VITE_AUTH0_AUDIENCE`

**`rasoi_camera/.env`**: `GEMINI_API_KEY`, `MAIN_APP_URL`

## Key Patterns

- The Gemini SDK is used in two ways: `google-genai` directly for vision/SQL generation, and `langchain-google-genai` (`ChatGoogleGenerativeAI`) for the LangGraph chatbot.
- Auth0 JWT verification happens in `backend/app/services/auth.py`. Tokens use RS256.
- The chat system uses LangGraph's message summarization to keep context windows small — conversations longer than 4 messages get summarized and older messages are deleted from state.
- Preference extraction runs automatically after each chat message by checking for keyword triggers before calling the LLM (saves tokens).
- The frontend API base URL is hardcoded in `services/api.js` (`http://localhost:8000/api`).
- No test framework is set up — testing is done via Swagger UI at `/docs`.

## Deployment

Deployed on Render (see `render.yaml`). Only the backend is configured for deployment — the frontend build would need to be served separately or added to the config.
