"""
Chat Service - Conversational AI for recipe assistance
"""
import json
from typing import Dict, Any, List
import google.generativeai as genai

from app.config import get_settings

settings = get_settings()

# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


CHAT_SYSTEM_PROMPT = """You are a helpful Indian cooking assistant named RasoiAI. You help users cook authentic Indian recipes based on their available ingredients.

Current Context:
- User has these ingredients: {ingredients}
- Currently discussing recipe: {recipe_name}
- Recipe details: {recipe_details}

Your capabilities:
1. Answer questions about the recipe (cooking time, techniques, tips)
2. Suggest modifications (reduce spice, change cooking method, make vegan)
3. Provide substitutions for missing ingredients
4. Recommend alternative recipes if user changes mind
5. Explain Indian cooking techniques and spice usage

Guidelines:
- Be concise and practical
- Use emojis sparingly for clarity (🌶️ for spice, ⏱️ for time, 💡 for tips)
- Always consider Indian cooking context
- Maintain friendly, encouraging tone
- If asked about something outside cooking, politely redirect

Format responses with clear structure using bullet points or numbered lists when appropriate.
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
        Dict with response and suggestions
    """
    if not settings.gemini_api_key:
        return _get_mock_response(message)
    
    try:
        model = genai.GenerativeModel(settings.gemini_text_model)
        
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
        
        # Create chat
        chat = model.start_chat(history=[])
        
        # Send system context first
        full_prompt = f"{system_prompt}\n\nUser question: {message}"
        
        response = chat.send_message(full_prompt)
        response_text = response.text.strip()
        
        # Generate suggestions based on context
        suggestions = _generate_suggestions(message, context)
        
        return {
            "response": response_text,
            "suggestions": suggestions
        }
        
    except Exception as e:
        return {
            "response": f"I apologize, but I encountered an error. Please try again. (Error: {str(e)[:50]})",
            "suggestions": ["Try a simpler question", "Ask about substitutions", "Request cooking tips"]
        }


def _get_mock_response(message: str) -> Dict[str, Any]:
    """Mock response when no API key is configured"""
    message_lower = message.lower()
    
    if "pressure cooker" in message_lower:
        response = """Yes, you can use a pressure cooker! Here's how:

1. Do the tempering (tadka) step normally in the pressure cooker
2. Add all vegetables and spices
3. Add a splash of water (1/4 cup)
4. Close lid and cook for 1-2 whistles
5. Let pressure release naturally

⏱️ This saves 10-15 minutes of cooking time!

💡 Tip: Vegetables will be slightly softer than kadai method."""
    
    elif "spicy" in message_lower or "spice" in message_lower:
        response = """To reduce spice level:

🌶️ **Reduce these:**
- Red chili powder: Use half the amount
- Green chilies: Skip entirely or remove seeds

🥛 **Add these to cool down:**
- 2-3 tbsp yogurt while cooking
- A pinch of sugar
- More tomatoes (natural sweetness)

💡 Tip: You can always add spice later, but can't remove it!"""
    
    elif "substitute" in message_lower or "replace" in message_lower:
        response = """Common Indian cooking substitutions:

🧈 **Ghee →** Butter or oil
🥥 **Coconut milk →** Cashew paste + water
🌿 **Kasuri methi →** Skip it (reduces flavor slightly)
🍅 **Fresh tomato →** Tomato puree or canned tomatoes
🧄 **Ginger-garlic paste →** Fresh minced (1:1 ratio)

What specific ingredient do you need to substitute?"""
    
    else:
        response = """I'm here to help with your Indian cooking! I can assist with:

• 🍳 Recipe modifications
• 🌶️ Adjusting spice levels
• 🔄 Ingredient substitutions
• ⏱️ Cooking time adjustments
• 💡 Pro cooking tips

What would you like to know about your recipe?"""
    
    return {
        "response": response,
        "suggestions": [
            "Can I use pressure cooker?",
            "How to make it less spicy?",
            "What can I substitute?"
        ]
    }


def _generate_suggestions(message: str, context: Dict[str, Any]) -> List[str]:
    """Generate contextual suggestions"""
    suggestions = []
    
    if context.get("selected_recipe"):
        suggestions = [
            "How long will this take?",
            "Can I make it less spicy?",
            "What can I serve with this?"
        ]
    else:
        suggestions = [
            "Show me vegetarian options",
            "What's quick to make?",
            "Suggest something with potatoes"
        ]
    
    return suggestions[:3]
