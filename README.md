# 🍛 RasoiAI — Intelligent Indian Recipe Recommendation System

**RasoiAI** is an AI-powered recipe recommendation platform that identifies ingredients from photos and suggests Indian recipes you can cook with what you have. It features **Annapurna**, a conversational AI chef persona built with LangGraph, who helps you explore, modify, and master Indian recipes across all regional cuisines.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **📸 Ingredient Recognition** | Upload photos of your ingredients — Gemini Vision AI identifies them with confidence scores, alternate regional names, and quantity estimates |
| **🔍 Smart Recipe Search** | AI-generated SQL queries match your ingredients against a database of Indian recipes, scoring each recipe by ingredient overlap |
| **🧑‍🍳 Annapurna Chatbot** | A LangGraph-powered conversational chef with persistent memory. Ask about recipes, request modifications, and get personalized cooking advice |
| **📊 Gap Analysis** | See which ingredients you have, what's missing, and your "readiness" to cook each recipe — with awareness of common Indian pantry staples |
| **🔐 Auth0 Authentication** | Secure login with user profiles, recipe favourites, and bookmarks |
| **🧠 Preference Learning** | The chatbot automatically extracts your dietary preferences, regional tastes, and cooking style from conversations and personalizes future recommendations |

---

## 🏗️ Architecture

```
RasoiAI/
├── backend/                    # FastAPI (Python)
│   ├── app/
│   │   ├── core/               # Config & settings (Pydantic)
│   │   ├── db/                 # Database layer (PostgreSQL/Neon)
│   │   │   ├── recipe_db.py    # Recipe CRUD operations
│   │   │   └── user_db.py      # Users, favourites, bookmarks, preferences
│   │   ├── routes/             # API endpoints
│   │   │   ├── auth.py         # Auth0 JWT verification
│   │   │   ├── chat.py         # Chat with Annapurna
│   │   │   ├── images.py       # Image upload & analysis
│   │   │   ├── recipes.py      # Recipe search & recommendations
│   │   │   └── user_history.py # Favourites & bookmarks
│   │   ├── schemas/            # Pydantic request/response models
│   │   └── services/           # Business logic
│   │       ├── chat_graph.py   # LangGraph stateful chat workflow
│   │       ├── vision.py       # Gemini Vision ingredient recognition
│   │       ├── sql_generator.py# AI-powered SQL query generation
│   │       └── gap_analysis.py # Ingredient gap & readiness scoring
│   ├── init_database.py        # DB seeder script (CSV → PostgreSQL)
│   └── requirements.txt
│
├── frontend/                   # React + Vite
│   └── src/
│       ├── pages/
│       │   ├── LandingPage     # Home / hero
│       │   ├── UploadPage      # Image upload & ingredient detection
│       │   ├── IngredientsPage # Review & confirm detected ingredients
│       │   ├── RecipesPage     # Browse AI-recommended recipes
│       │   ├── RecipeDetailPage# Full recipe + Annapurna chatbot
│       │   ├── ProfilePage     # User profile, favourites, bookmarks
│       │   └── LoginPage       # Auth0 login
│       └── services/
│           └── api.js          # API client
│
└── indian_recipe_cleaned.csv   # Recipe dataset (~6500+ recipes)
```

---

## 🔧 Tech Stack

### Backend
- **Framework:** FastAPI + Uvicorn
- **AI/LLM:** Google Gemini (`google-genai`) — Vision & Text models (`gemini-2.5-flash`)
- **Chat Orchestration:** LangGraph with `AsyncPostgresSaver` checkpointer for persistent conversation memory
- **Database:** PostgreSQL via [Neon](https://neon.tech) (serverless Postgres)
- **Auth:** Auth0 (RS256 JWT verification via `PyJWT`)
- **Validation:** Pydantic v2 + Pydantic Settings

### Frontend
- **Framework:** React 19 + Vite 7
- **Auth:** `@auth0/auth0-react`
- **Routing:** React Router DOM v7
- **Styling:** Vanilla CSS

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL** — a [Neon](https://neon.tech) account (free tier) is recommended
- **Google Gemini API Key** — get one at [Google AI Studio](https://aistudio.google.com/apikey)
- **Auth0 Account** — create a free tenant at [auth0.com](https://auth0.com)

### 1. Clone the Repository

```bash
git clone https://github.com/rohanjadhavhub/RasoiAI.git
cd RasoiAI
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Fill in your credentials in `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/dbname?sslmode=require
AUTH0_DOMAIN=your_auth0_domain
AUTH0_API_AUDIENCE=your_api_audience
```

### 3. Initialize the Database

Seed the recipe database from the CSV dataset:

```bash
python init_database.py
```

This loads ~6500+ Indian recipes into your PostgreSQL database.

### 4. Start the Backend

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `/docs`.

### 5. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Fill in your Auth0 credentials in `frontend/.env`:

```env
VITE_AUTH0_DOMAIN=your_auth0_domain
VITE_AUTH0_CLIENT_ID=your_auth0_client_id
VITE_AUTH0_AUDIENCE=your_api_audience
```

### 6. Start the Frontend

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## 🔄 Application Workflow

```mermaid
flowchart LR
    A[📸 Upload Photos] --> B[🔍 Gemini Vision<br/>Identifies Ingredients]
    B --> C[✅ Review & Confirm<br/>Ingredients]
    C --> D[🤖 AI SQL Generator<br/>Queries Recipe DB]
    D --> E[📊 Gap Analysis<br/>Scores Readiness]
    E --> F[🍽️ Browse Recipes<br/>with Match Scores]
    F --> G[🧑‍🍳 Chat with Annapurna<br/>Ask Questions & Modify]
```

1. **Upload** — Snap photos of your available ingredients (up to 3 images, supports JPG/PNG/HEIC/WebP)
2. **Detect** — Gemini Vision identifies ingredients with confidence scores and regional alternate names
3. **Confirm** — Review the detected ingredients, remove false positives, add anything missed
4. **Search** — An AI-generated SQL query finds the best-matching recipes from the database, ranked by ingredient overlap
5. **Analyze** — Each recipe shows a gap analysis: what you have, what's missing (critical vs. optional), and a readiness label (`READY` / `ALMOST_THERE` / `NEED_SHOPPING`)
6. **Cook & Chat** — Open a recipe to view full details. Chat with **Annapurna** to ask questions, get substitution tips, or modify the recipe. She remembers your preferences across sessions

---

## 🎯 Use Cases

- **"What can I cook tonight?"** — Upload photos of what's in your fridge and get instant recipe ideas ranked by ingredient match
- **"I'm new to Indian cooking"** — Browse recipes and ask Annapurna to explain techniques, suggest simpler alternatives, or adjust spice levels
- **"I have dietary restrictions"** — Tell Annapurna you're vegan, Jain, gluten-free, etc. She'll remember and personalize all future recommendations
- **"Can I modify this recipe?"** — Ask Annapurna to swap ingredients, adjust servings, or make it kid-friendly — she returns an updated recipe
- **"Save for later"** — Bookmark recipes to revisit and favourite the ones you loved

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload-images` | Upload ingredient photos |
| `POST` | `/api/analyze-ingredients` | Run Gemini Vision on uploaded images |
| `POST` | `/api/confirm-ingredients` | Confirm ingredients + preferences |
| `POST` | `/api/get-recommendations` | Get AI-ranked recipe recommendations |
| `GET`  | `/api/recipe/{id}` | Get full recipe details |
| `GET`  | `/api/recipes/search` | Search recipes by ingredient list |
| `POST` | `/api/chat` | Chat with Annapurna (supports auth token for memory) |
| `GET`  | `/api/auth/me` | Get/create user profile |
| `POST` | `/api/favourites` | Add a favourite |
| `DELETE` | `/api/favourites/{id}` | Remove a favourite |
| `GET`  | `/api/favourites` | List user's favourites |
| `POST` | `/api/bookmarks` | Add a bookmark |
| `DELETE` | `/api/bookmarks/{id}` | Remove a bookmark |
| `GET`  | `/api/bookmarks` | List user's bookmarks |
| `GET`  | `/health` | Health check |

Full interactive documentation available at `/docs` (Swagger UI) and `/redoc`.

---

## 🧪 Development

### Running Backend Tests

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` to test endpoints interactively.

### Building Frontend for Production

```bash
cd frontend
npm run build       # Output in dist/
npm run preview     # Preview the production build
```

### Linting

```bash
cd frontend
npm run lint
```

---

## 📚 Dataset

The project uses a cleaned dataset of **~6500+ Indian recipes** (`indian_recipe_cleaned.csv`) covering dishes from across India, with fields:

| Column | Description |
|--------|-------------|
| `recipe` | Recipe name |
| `ingredients` | Comma-separated ingredient list |
| `instruction` | Step-by-step cooking instructions |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source. See the repository for license details.
