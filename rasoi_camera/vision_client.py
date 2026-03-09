"""
Vision Client — Local Gemini Vision analysis for ingredient extraction.

Mirrors the prompt and logic from the main app's ``vision.py`` but runs
standalone on the Raspberry Pi without Pydantic or the full backend stack.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from google import genai
from google.genai import types

# ── Gemini Configuration ──────────────────────────────────────
_API_KEY = os.getenv("GEMINI_API_KEY", "")
_MODEL = os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=_API_KEY) if _API_KEY else None


# ── Vision Prompt (identical to main app's vision.py) ─────────
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


def analyze_image(image_path: Path) -> Dict[str, Any]:
    """
    Analyse a captured image using Gemini Vision.

    Args:
        image_path: Absolute path to the JPEG file.

    Returns:
        Dict with keys ``identified_ingredients``, ``packaged_items``,
        ``uncertain_items`` — each a list of dicts.

    Raises:
        RuntimeError: If the API key is missing or analysis fails.
    """
    if not _API_KEY or client is None:
        raise RuntimeError(
            "GEMINI_API_KEY not set. Add it to your .env file."
        )

    image_bytes = image_path.read_bytes()

    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    content = [image_part, VISION_PROMPT]

    try:
        response = client.models.generate_content(
            model=_MODEL,
            contents=content,
        )
        response_text = response.text.strip()

        # Strip markdown code fences if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        result: Dict[str, Any] = json.loads(response_text)

        return {
            "identified_ingredients": result.get("identified_ingredients", []),
            "packaged_items": result.get("packaged_items", []),
            "uncertain_items": result.get("uncertain_items", []),
        }

    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse Gemini response: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Vision analysis error: {exc}") from exc


def extract_ingredient_names(analysis: Dict[str, Any]) -> List[str]:
    """
    Flatten an analysis result into a simple list of ingredient names.

    Includes identified + packaged items with confidence >= 0.5.
    Uncertain items are excluded by default.

    Args:
        analysis: Dict returned by ``analyze_image()``.

    Returns:
        Deduplicated list of lowercase ingredient names.
    """
    names: set[str] = set()

    for item in analysis.get("identified_ingredients", []):
        if item.get("confidence", 0) >= 0.5:
            names.add(item["name"].lower())

    for item in analysis.get("packaged_items", []):
        if item.get("confidence", 0) >= 0.5:
            names.add(item["name"].lower())

    return sorted(names)
