"""
Chat Routes - Conversational AI for recipe assistance
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Header

from app.schemas import ChatRequest, ChatResponse
from app.services.chat import get_chat_response

router = APIRouter()

# Reference to sessions from images module
from app.routes.images import sessions


async def _extract_user_id(authorization: Optional[str]) -> tuple:
    """
    Extract auth0_sub and internal user_id from Bearer token.
    Returns (auth0_sub, internal_user_id) or (None, None) if unauthenticated.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None, None
    token = authorization.split(" ", 1)[1]
    try:
        from app.services.auth import verify_token
        payload = await verify_token(token)
        auth0_sub = payload.get("sub")
        if not auth0_sub:
            return None, None
        from app.db import get_user_database
        db = get_user_database()
        user = db.get_user_by_sub(auth0_sub)
        if user:
            return auth0_sub, user["id"]
        return None, None
    except Exception:
        return None, None


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    authorization: Optional[str] = Header(None),
):
    """
    Chat with AI about recipes.
    Optionally pass Authorization header for persistent memory.
    """
    # Get session context
    context = {}
    if request.session_id in sessions:
        session = sessions[request.session_id]
        context = {
            "ingredients": session.get("ingredients", []),
            "preferences": session.get("preferences"),
            "selected_recipe": session.get("selected_recipe"),
        }

    # Add any recipe context from request
    if request.recipe_context:
        context["recipe_context"] = request.recipe_context

    # Extract user identity from token (if provided)
    auth0_sub, internal_user_id = await _extract_user_id(authorization)

    try:
        response = await get_chat_response(
            request.message,
            context,
            user_id=auth0_sub,
            internal_user_id=internal_user_id,
        )
        return ChatResponse(
            response=response["response"],
            suggestions=response.get("suggestions", []),
            response_type=response.get("response_type", "chat"),
            updated_recipe=response.get("updated_recipe"),
            thread_id=auth0_sub,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/chat/select-recipe")
async def select_recipe(session_id: str, recipe_id: int):
    """
    Select a recipe for context in chat
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    from app.db import get_database
    db = get_database()
    recipe = db.get_recipe_by_id(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    sessions[session_id]["selected_recipe"] = recipe

    return {
        "status": "selected",
        "recipe": recipe["recipe"],
    }
