# RasoiAI Backend

Indian Recipe Recommendation System - Backend API

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Initialize Database

```bash
python init_database.py
```

## Run Server

```bash
uvicorn app.main:app --reload
```

API will be available at http://localhost:8000
