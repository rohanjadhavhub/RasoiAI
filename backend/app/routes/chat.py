"""
Chat Routes - Conversational AI for recipe assistance
"""
from fastapi import APIRouter, HTTPException

from app.models import ChatRequest, ChatResponse
from app.services.chat import get_chat_response

router = APIRouter()

# Reference to sessions from images module
from app.routes.images import sessions


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with AI about recipes
    """
    # Get session context if available
    context = {}
    if request.session_id in sessions:
        session = sessions[request.session_id]
        context = {
            "ingredients": session.get("ingredients", []),
            "preferences": session.get("preferences"),
            "selected_recipe": session.get("selected_recipe")
        }
    
    # Add any recipe context from request
    if request.recipe_context:
        context["recipe_context"] = request.recipe_context
    
    try:
        response = await get_chat_response(request.message, context)
        return ChatResponse(
            response=response["response"],
            suggestions=response.get("suggestions", [])
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
    
    from app.database import get_database
    db = get_database()
    recipe = db.get_recipe_by_id(recipe_id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    sessions[session_id]["selected_recipe"] = recipe
    
    return {
        "status": "selected",
        "recipe": recipe["recipe"]
    }
