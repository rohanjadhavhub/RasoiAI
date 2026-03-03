"""
Vision AI Service - Ingredient Recognition using Gemini
"""
import json
from typing import List, Dict, Any
from google import genai
from google.genai import types

from app.core.config import get_settings
from app.schemas import IdentifiedIngredient

settings = get_settings()

# Configure Gemini client
client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None


VISION_PROMPT = """You are an expert at identifying Indian cooking ingredients from photos.

Analyze these images and identify all visible ingredients used in Indian cooking.

For each ingredient, provide:
1. name: Common name in English (e.g., "potato", not "aloo")
2. alternate_names: Array of regional variations ["aloo", "batata"]
3. category: One of [vegetable, protein, spice, grain, dairy, fruit, herb, other]
4. confidence: Float 0.0-1.0 (how certain you are)
5. quantity_estimate: Approximate quantity if visible (e.g., "4-5 medium pieces")
6. notes: Any relevant observations

Special instructions:
- For packaged items, use OCR to read labels
- If uncertain, mark confidence < 0.7 and add note
- Handle multiple items of same ingredient (e.g., "3 onions")
- Recognize both fresh and packaged ingredients
- Focus on ingredients used in Indian cooking

Output as JSON with this exact structure:
{
  "identified_ingredients": [
    {
      "name": "potato",
      "alternate_names": ["aloo", "batata"],
      "category": "vegetable",
      "confidence": 0.95,
      "quantity_estimate": "4-5 medium pieces",
      "notes": "Clear view, good lighting"
    }
  ],
  "packaged_items": [
    {
      "name": "Garam Masala",
      "alternate_names": [],
      "category": "spice",
      "confidence": 0.88,
      "quantity_estimate": "1 packet",
      "notes": "Label partially visible"
    }
  ],
  "uncertain_items": [
    {
      "name": "coriander leaves",
      "alternate_names": ["dhania", "cilantro"],
      "category": "herb",
      "confidence": 0.55,
      "quantity_estimate": null,
      "notes": "Too far from camera, could be curry leaves"
    }
  ]
}

IMPORTANT: Return ONLY valid JSON, no additional text or markdown formatting."""


async def analyze_ingredients_from_images(image_data_list: List[bytes]) -> Dict[str, Any]:
    """
    Analyze images using Gemini Vision to identify ingredients
    
    Args:
        image_data_list: List of image bytes
        
    Returns:
        Dict with identified_ingredients, packaged_items, uncertain_items
    """
    if not settings.gemini_api_key:
        # Return mock data if no API key
        return _get_mock_ingredients()
    
    try:
        # Prepare image parts
        image_parts = []
        for img_data in image_data_list:
            image_parts.append(
                types.Part.from_bytes(data=img_data, mime_type="image/jpeg")
            )
        
        # Build content with images and prompt
        content = image_parts + [VISION_PROMPT]
        
        # Generate response
        response = client.models.generate_content(
            model=settings.gemini_vision_model,
            contents=content
        )
        response_text = response.text.strip()
        
        # Clean up response - remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
        
        # Parse JSON response
        result = json.loads(response_text)
        
        # Convert to IdentifiedIngredient models
        identified = [
            IdentifiedIngredient(**ing) 
            for ing in result.get("identified_ingredients", [])
        ]
        packaged = [
            IdentifiedIngredient(**ing) 
            for ing in result.get("packaged_items", [])
        ]
        uncertain = [
            IdentifiedIngredient(**ing) 
            for ing in result.get("uncertain_items", [])
        ]
        
        return {
            "identified_ingredients": identified,
            "packaged_items": packaged,
            "uncertain_items": uncertain
        }
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Vision AI response: {str(e)}")
    except Exception as e:
        raise Exception(f"Vision AI error: {str(e)}")


def _get_mock_ingredients() -> Dict[str, Any]:
    """Return mock ingredients for testing without API key"""
    return {
        "identified_ingredients": [
            IdentifiedIngredient(
                name="potato",
                alternate_names=["aloo", "batata"],
                category="vegetable",
                confidence=0.95,
                quantity_estimate="4-5 medium pieces",
                notes="Mock data - no API key configured"
            ),
            IdentifiedIngredient(
                name="onion",
                alternate_names=["pyaz", "kanda"],
                category="vegetable",
                confidence=0.92,
                quantity_estimate="2-3 pieces",
                notes="Mock data"
            ),
            IdentifiedIngredient(
                name="tomato",
                alternate_names=["tamatar"],
                category="vegetable",
                confidence=0.90,
                quantity_estimate="3 pieces",
                notes="Mock data"
            )
        ],
        "packaged_items": [],
        "uncertain_items": []
    }
