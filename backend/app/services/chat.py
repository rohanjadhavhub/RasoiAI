"""
Chat Service - Conversational AI for recipe assistance (Annapurna)

Authenticated users → LangGraph workflow with persistent memory.
Unauthenticated   → stateless Gemini call (no memory).
"""
import json
from typing import Dict, Any, Optional
from google import genai

from app.core.config import get_settings

settings = get_settings()

# Configure Gemini client (used only for unauthenticated fallback)
client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None


# ── System Prompt (lean, shared with chat_graph.py) ──────────

CHAT_SYSTEM_PROMPT = """You are Annapurna, an expert Indian chef across all regional cuisines.

CONTEXT:
User profile: {user_preferences}
Ingredients: {ingredients} | Recipe: {recipe_name} | Details: {recipe_details}

STYLE: Confident, warm, direct. Short sentences. No hedging.

RULES:
- No greetings, no markdown, no emojis
- Always have a cooking answer. Never say "I don't know"
- Off-topic: "That's outside my kitchen — ask me about this recipe."
- No unnecessary follow-up questions. Answer directly.
- Modifications: ask ONE clarifying question first, wait, then return updated recipe JSON.

OUTPUT: Always return valid JSON only. Nothing outside it.

Chat reply:
{{"type":"chat","content":"plain text answer"}}

After user confirms a modification:
{{"type":"recipe_update","content":"Done, updated the recipe for you.","updated_recipe":{{"recipe":"Name","ingredients":"item1, item2","servings":"2","cook_time":"25 min","spice_level":"Mild"}}}}

JSON RULES:
- Never include or change "instruction" field
- "ingredients" = comma-separated string
- Only include changed fields + always include "recipe" and "ingredients"
"""


async def get_chat_response(
    message: str,
    context: Dict[str, Any],
    user_id: Optional[str] = None,
    internal_user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get chat response from AI.

    Args:
        message: User's message
        context: Current session context (ingredients, recipe, etc.)
        user_id: auth0_sub (if authenticated) — enables memory
        internal_user_id: DB users.id (if authenticated)

    Returns:
        Dict with response, response_type, and optionally updated_recipe
    """
    if not settings.gemini_api_key:
        return _get_mock_response(message)

    # ── Authenticated path: LangGraph with memory ────────────
    if user_id and internal_user_id:
        try:
            from app.services.chat_graph import invoke_chat_graph
            return await invoke_chat_graph(user_id, internal_user_id, message, context)
        except Exception as e:
            print(f"[LangGraph Error] {type(e).__name__}: {e}")
            # Fall through to stateless path as safety net

    # ── Unauthenticated / fallback: stateless Gemini call ────
    try:
        ingredients = context.get("ingredients", [])
        selected_recipe = context.get("selected_recipe") or context.get("recipe_context", {})
        recipe_name = selected_recipe.get("recipe", "None selected") if selected_recipe else "None selected"
        recipe_details = ""

        if selected_recipe:
            recipe_details = (
                f"Recipe: {selected_recipe.get('recipe', '')}. "
                f"Ingredients: {selected_recipe.get('ingredients', '')}. "
                f"Instructions: {str(selected_recipe.get('instruction', ''))[:300]}..."
            )

        system_prompt = CHAT_SYSTEM_PROMPT.format(
            user_preferences="Not logged in.",
            ingredients=", ".join(ingredients) if ingredients else "Not specified",
            recipe_name=recipe_name,
            recipe_details=recipe_details or "No recipe selected yet",
        )

        full_prompt = f"{system_prompt}\n\nUser message: {message}"

        response = client.models.generate_content(
            model=settings.gemini_text_model,
            contents=full_prompt,
        )
        response_text = response.text.strip()

        parsed = _parse_ai_response(response_text)

        result = {
            "response": parsed.get("content", response_text),
            "response_type": parsed.get("type", "chat"),
        }

        if parsed.get("type") == "recipe_update" and parsed.get("updated_recipe"):
            result["updated_recipe"] = parsed["updated_recipe"]

        return result

    except Exception as e:
        print(f"[Annapurna Chat Error] {type(e).__name__}: {e}")
        return {
            "response": "Something went wrong on my end. Ask me again.",
            "response_type": "chat",
        }


def _parse_ai_response(text: str) -> Dict[str, Any]:
    """Parse JSON response from AI, with fallback for non-JSON responses"""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict) and "type" in parsed:
            return parsed
    except json.JSONDecodeError:
        pass

    clean_text = _clean_response_text(text)
    return {"type": "chat", "content": clean_text}


def _clean_response_text(text: str) -> str:
    """Remove markdown formatting, emojis, and unwanted patterns from response text"""
    import re
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'^#{1,4}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\-•\*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]', '', text)
    text = re.sub(r'^(Namaste!?\s*|Welcome!?\s*|Hello!?\s*|Hi there!?\s*)', '', text, flags=re.IGNORECASE)
    return text.strip()


def _get_mock_response(message: str) -> Dict[str, Any]:
    """Mock response when no API key is configured"""
    message_lower = message.lower()

    if "pressure cooker" in message_lower:
        response = ("Do the tempering step in the cooker itself, add everything in, "
                     "splash 1/4 cup water, and give it 1-2 whistles. Natural release. "
                     "Saves you 10-15 minutes and the flavours meld beautifully.")

    elif "spicy" in message_lower or "spice" in message_lower:
        response = ("Halve the red chili powder and deseed the green chilies. "
                     "Stir in 2 tablespoons of yogurt towards the end — it rounds "
                     "out the heat without killing the flavour. Want me to update the recipe?")

    elif "substitute" in message_lower or "replace" in message_lower:
        response = ("Ghee swaps with butter or neutral oil. Coconut milk can be replaced "
                     "with cashew paste thinned with water. Ginger-garlic paste — just use "
                     "fresh minced, same quantity. Which ingredient do you need swapped?")

    elif "serving" in message_lower or "people" in message_lower:
        response = "How many servings do you need? I will scale everything for you."

    else:
        response = ("Ask me anything about this recipe — cooking tips, ingredient swaps, "
                     "serving adjustments, or technique. I am all yours.")

    return {
        "response": response,
        "response_type": "chat",
    }
