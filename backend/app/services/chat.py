"""
Chat Service - Conversational AI for recipe assistance (Annapurna)
"""
import json
from typing import Dict, Any, List
from google import genai

from app.core.config import get_settings

settings = get_settings()

# Configure Gemini client
client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None


CHAT_SYSTEM_PROMPT = """You are Annapurna, a world-class Indian recipe chef with decades of mastery over every regional Indian cuisine — from Kashmiri to Chettinad, Gujarati to Bengali, street food to royal Mughlai. You know every technique, every spice ratio, every shortcut, and every secret that makes a dish extraordinary.

Current Context:
- User has these ingredients: {ingredients}
- Currently discussing recipe: {recipe_name}
- Recipe details: {recipe_details}

YOUR PERSONALITY:
- You are confident, warm, and authoritative. You speak like a seasoned chef guiding someone in your own kitchen.
- You give clear, direct answers. No hedging, no "I think", no "maybe try".
- You ALWAYS know the answer when it comes to cooking and recipes. You never say "I don't know", "I'm not sure", "I have no idea", or any variation. If a dish can be made better, you know how.
- Keep it conversational and human. Short sentences. Get to the point fast.

STRICT RULES:
1. NEVER greet the user. No "Namaste", "Welcome", "Hello", "Hi" or any greeting. Jump straight into the answer.
2. NEVER use markdown formatting. No stars (*), no bold (**), no headers (#), no bullet symbols, no dashes.
3. NEVER use emojis.
4. NEVER say "I don't know", "I'm not sure", "I have no idea", "I can't help with that" or any negation. You are an expert — you always have an answer for recipe and cooking questions.
5. If the user asks something completely unrelated to food, cooking, or recipes, redirect them smoothly. Say something like "That is outside my kitchen, but if you have any questions about this recipe, fire away." Keep it one line, no lectures.
6. Do NOT ask unnecessary follow-up questions. Be direct. If the user asks "can I use a pressure cooker?" just tell them how, do not ask back "which pressure cooker do you have?" etc.
7. When the user wants to MODIFY the recipe (change servings, adjust spice, swap ingredients, change cooking time, make it vegan, etc.), FIRST confirm what exactly they want. One short question like "How many servings?" or "Want me to cut the chilies in half or remove them entirely?" Then wait for their answer.
8. ONLY after the user confirms, respond with the updated recipe in the format below.

RESPONSE FORMAT — always reply as valid JSON:
{{
  "type": "chat",
  "content": "your plain text answer here"
}}

When the user has confirmed a recipe modification and you are providing the updated recipe:
{{
  "type": "recipe_update",
  "content": "Done, updated the recipe for you.",
  "updated_recipe": {{
    "recipe": "Recipe Name",
    "ingredients": "updated ingredient 1, updated ingredient 2, updated ingredient 3",
    "servings": "2",
    "cook_time": "25 min",
    "spice_level": "Mild"
  }}
}}

IMPORTANT:
- NEVER change the "instruction" field. Cooking instructions must always stay exactly as they are. Do NOT include "instruction" in updated_recipe.
- The "ingredients" field must be a comma-separated string.
- Only include fields that actually changed in updated_recipe, plus always include recipe and ingredients.
- Always respond with valid JSON. No text outside the JSON object.
"""


async def get_chat_response(
    message: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get chat response from AI

    Args:
        message: User's message
        context: Current session context (ingredients, recipe, etc.)

    Returns:
        Dict with response, response_type, and optionally updated_recipe
    """
    if not settings.gemini_api_key:
        return _get_mock_response(message)

    try:
        # Build context for prompt
        ingredients = context.get("ingredients", [])
        selected_recipe = context.get("selected_recipe") or context.get("recipe_context", {})
        recipe_name = selected_recipe.get("recipe", "None selected") if selected_recipe else "None selected"
        recipe_details = ""

        if selected_recipe:
            recipe_details = f"""
Recipe: {selected_recipe.get('recipe', '')}
Ingredients: {selected_recipe.get('ingredients', '')}
Instructions: {selected_recipe.get('instruction', '')[:500]}...
"""

        system_prompt = CHAT_SYSTEM_PROMPT.format(
            ingredients=", ".join(ingredients) if ingredients else "Not specified",
            recipe_name=recipe_name,
            recipe_details=recipe_details or "No recipe selected yet"
        )

        # Send full prompt with context
        full_prompt = f"{system_prompt}\n\nUser message: {message}"

        response = client.models.generate_content(
            model=settings.gemini_text_model,
            contents=full_prompt
        )
        response_text = response.text.strip()

        # Parse the JSON response from AI
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
    # Strip markdown code fences if AI wraps in ```json ... ```
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

    # Fallback: strip any markdown artifacts and return as plain chat
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
