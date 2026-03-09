"""
Forwarder — Send extracted ingredients to the main RasoiAI backend.

Uses httpx to POST ingredient names to ``/api/remote-ingredients`` on the
main app, which runs them through ``sql_generator.py`` for recipe lookup.
"""
import os
from typing import Any, Dict, List, Optional

import httpx

# ── Configuration ─────────────────────────────────────────────
MAIN_APP_URL = os.getenv("MAIN_APP_URL", "http://localhost:8000")
_ENDPOINT = "/api/remote-ingredients"
_TIMEOUT = 30  # seconds


async def forward_ingredients(
    ingredients: List[str],
    preferences: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    POST extracted ingredients to the main RasoiAI backend.

    Args:
        ingredients:  List of ingredient names (e.g. ["potato", "onion"]).
        preferences:  Optional user preferences dict.

    Returns:
        Recipe recommendations from the main app.

    Raises:
        httpx.HTTPStatusError: If the main app returns an error status.
        httpx.ConnectError:    If the main app is unreachable.
    """
    url = f"{MAIN_APP_URL}{_ENDPOINT}"

    payload: Dict[str, Any] = {"ingredients": ingredients}
    if preferences:
        payload["preferences"] = preferences

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
