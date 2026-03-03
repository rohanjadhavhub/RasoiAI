"""
Auth Routes - User authentication via Auth0
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends

from app.services.auth import get_current_user
from app.db import get_user_database

router = APIRouter()


@router.get("/me")
async def get_me(claims: Dict[str, Any] = Depends(get_current_user)):
    """
    Get or create user profile from Auth0 token.
    On first call, auto-creates user row from token claims.
    """
    db = get_user_database()

    # Extract user info from Auth0 claims
    auth0_sub = claims.get("sub", "")
    email = claims.get("email") or claims.get(
        f"https://{claims.get('iss', '').replace('https://', '')}/email"
    )
    username = claims.get("nickname") or claims.get("name") or email

    # Upsert user (create on first login, update last_login on subsequent)
    user = db.upsert_user(
        auth0_sub=auth0_sub,
        email=email,
        username=username,
    )

    return {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "created_at": user["created_at"],
        "last_login": user["last_login"],
    }
