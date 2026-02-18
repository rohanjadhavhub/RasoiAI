"""
User History Routes - Favourites & Bookmarks (authenticated)
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException

from app.services.auth import get_current_user
from app.user_database import get_user_database
from app.models import RecipeActionRequest, SavedRecipeResponse

router = APIRouter()


def _resolve_user_id(claims: Dict[str, Any]) -> int:
    """
    Resolve internal user_id from Auth0 claims.
    Auto-creates the user row if it doesn't exist yet (same as /me endpoint).
    """
    db = get_user_database()
    auth0_sub = claims.get("sub", "")
    email = claims.get("email") or claims.get("nickname")
    username = claims.get("nickname") or claims.get("name") or email

    # Upsert: creates on first call, updates last_login on subsequent calls
    user = db.upsert_user(auth0_sub=auth0_sub, email=email, username=username)
    return user["id"]


# ─── Favourites ──────────────────────────────────────────────


@router.post("/favourites", status_code=201)
async def add_favourite(
    body: RecipeActionRequest,
    claims: Dict[str, Any] = Depends(get_current_user),
):
    """Add a recipe to the authenticated user's favourites"""
    user_id = _resolve_user_id(claims)
    db = get_user_database()
    added = db.add_favourite(user_id, body.recipe_id, body.recipe_name)
    return {"added": added, "recipe_id": body.recipe_id}


@router.delete("/favourites/{recipe_id}")
async def remove_favourite(
    recipe_id: int,
    claims: Dict[str, Any] = Depends(get_current_user),
):
    """Remove a recipe from the authenticated user's favourites"""
    user_id = _resolve_user_id(claims)
    db = get_user_database()
    removed = db.remove_favourite(user_id, recipe_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favourite not found")
    return {"removed": True, "recipe_id": recipe_id}


@router.get("/favourites", response_model=List[SavedRecipeResponse])
async def list_favourites(
    claims: Dict[str, Any] = Depends(get_current_user),
):
    """List all favourited recipes for the authenticated user"""
    user_id = _resolve_user_id(claims)
    db = get_user_database()
    return db.get_favourites(user_id)


@router.get("/favourites/{recipe_id}/status")
async def favourite_status(
    recipe_id: int,
    claims: Dict[str, Any] = Depends(get_current_user),
):
    """Check if a recipe is in the authenticated user's favourites"""
    user_id = _resolve_user_id(claims)
    db = get_user_database()
    return {"is_favourite": db.is_favourite(user_id, recipe_id)}


# ─── Bookmarks ───────────────────────────────────────────────


@router.post("/bookmarks", status_code=201)
async def add_bookmark(
    body: RecipeActionRequest,
    claims: Dict[str, Any] = Depends(get_current_user),
):
    """Add a recipe to the authenticated user's bookmarks"""
    user_id = _resolve_user_id(claims)
    db = get_user_database()
    added = db.add_bookmark(user_id, body.recipe_id, body.recipe_name)
    return {"added": added, "recipe_id": body.recipe_id}


@router.delete("/bookmarks/{recipe_id}")
async def remove_bookmark(
    recipe_id: int,
    claims: Dict[str, Any] = Depends(get_current_user),
):
    """Remove a recipe from the authenticated user's bookmarks"""
    user_id = _resolve_user_id(claims)
    db = get_user_database()
    removed = db.remove_bookmark(user_id, recipe_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return {"removed": True, "recipe_id": recipe_id}


@router.get("/bookmarks", response_model=List[SavedRecipeResponse])
async def list_bookmarks(
    claims: Dict[str, Any] = Depends(get_current_user),
):
    """List all bookmarked recipes for the authenticated user"""
    user_id = _resolve_user_id(claims)
    db = get_user_database()
    return db.get_bookmarks(user_id)


@router.get("/bookmarks/{recipe_id}/status")
async def bookmark_status(
    recipe_id: int,
    claims: Dict[str, Any] = Depends(get_current_user),
):
    """Check if a recipe is in the authenticated user's bookmarks"""
    user_id = _resolve_user_id(claims)
    db = get_user_database()
    return {"is_bookmark": db.is_bookmark(user_id, recipe_id)}
