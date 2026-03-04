"""
LangGraph Chat Workflow — Annapurna chatbot with persistent memory.

Uses StateGraph + AsyncPostgresSaver to checkpoint conversation state
in PostgreSQL (Neon) so authenticated users get cross-session memory.
Stores conversation summaries (not full history) to save tokens.
"""
import json
from typing import TypedDict, Dict, Any, List, Optional, Annotated

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, RemoveMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from app.core.config import get_settings
from app.db.user_db import get_user_database


# ── System Prompt (lean, ~300 tokens) ────────────────────────

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

# ── Preference extraction prompt ─────────────────────────────

PREFERENCE_EXTRACT_PROMPT = """Extract cooking preferences from this user message.
Return ONLY a JSON object. Use empty string for fields not mentioned.
{{"preferred_spice_level":"","dietary_restrictions":"","favorite_cuisines":"","disliked_ingredients":"","region":"","community":"","cooking_style":"","general_notes":""}}

User message: {message}"""

# ── Summarization prompt ─────────────────────────────────────

SUMMARIZE_PROMPT = """Summarize this conversation in 2-3 sentences. Focus on: what the user asked, what was recommended, any recipe modifications made, and user preferences revealed.

{conversation}"""


# ── Graph State ──────────────────────────────────────────────

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]  # conversation history
    context: Dict[str, Any]                  # recipe / ingredients
    user_id: Optional[str]                   # auth0_sub
    internal_user_id: Optional[int]          # DB user.id
    user_preferences: Dict[str, Any]         # from DB
    response: Dict[str, Any]                 # final output
    summary: str                             # running conversation summary


# ── Module-level pool (set by init_checkpointer) ────────────

_pool: Optional[AsyncConnectionPool] = None
_checkpointer: Optional[AsyncPostgresSaver] = None


async def init_checkpointer():
    """Create connection pool + checkpointer. Call on app startup."""
    global _pool, _checkpointer
    settings = get_settings()
    conninfo = settings.database_url

    # Create checkpoint tables using autocommit connection
    # (setup() uses CREATE INDEX CONCURRENTLY — can't run inside transaction)
    import psycopg
    async with await psycopg.AsyncConnection.connect(
        conninfo, autocommit=True
    ) as conn:
        checkpointer_setup = AsyncPostgresSaver(conn)
        await checkpointer_setup.setup()
    print("[LangGraph] Checkpoint tables created.")

    # Create pool for runtime
    _pool = AsyncConnectionPool(
        conninfo=conninfo,
        min_size=2,
        max_size=10,
        open=False,
    )
    await _pool.open()
    _checkpointer = AsyncPostgresSaver(_pool)
    print("[LangGraph] Checkpointer initialised, pool ready.")


async def close_checkpointer():
    """Close pool. Call on app shutdown."""
    global _pool
    if _pool:
        await _pool.close()
        print("[LangGraph] Connection pool closed.")


def get_checkpointer() -> AsyncPostgresSaver:
    if _checkpointer is None:
        raise RuntimeError("Checkpointer not initialised. Call init_checkpointer() first.")
    return _checkpointer


# ── Helper: build user-preference summary string ────────────

def _pref_summary(prefs: Optional[Dict[str, Any]]) -> str:
    if not prefs:
        return "New user, no known preferences."
    parts = []
    if prefs.get("region"):
        parts.append(f"From: {prefs['region']}")
    if prefs.get("community"):
        parts.append(f"Community: {prefs['community']}")
    if prefs.get("preferred_spice_level"):
        parts.append(f"Spice: {prefs['preferred_spice_level']}")
    if prefs.get("dietary_restrictions"):
        parts.append(f"Diet: {prefs['dietary_restrictions']}")
    if prefs.get("favorite_cuisines"):
        parts.append(f"Likes: {prefs['favorite_cuisines']}")
    if prefs.get("disliked_ingredients"):
        parts.append(f"Avoids: {prefs['disliked_ingredients']}")
    if prefs.get("cooking_style"):
        parts.append(f"Style: {prefs['cooking_style']}")
    if prefs.get("general_notes"):
        parts.append(f"Notes: {prefs['general_notes']}")
    return ". ".join(parts) if parts else "New user, no known preferences."


# ── Helper: parse JSON from AI response ─────────────────────

def _parse_json_response(text: str) -> Dict[str, Any]:
    """Parse JSON from model output, stripping markdown fences."""
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
    # Fallback
    import re
    clean_text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    clean_text = re.sub(r'^#{1,4}\s*', '', clean_text, flags=re.MULTILINE)
    clean_text = re.sub(r'^[\-•\*]\s+', '', clean_text, flags=re.MULTILINE)
    return {"type": "chat", "content": clean_text.strip()}


# ── Graph Nodes ──────────────────────────────────────────────

async def chat_node(state: ChatState) -> dict:
    """Call Gemini with the conversation summary + latest message."""
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_text_model,
        google_api_key=settings.gemini_api_key,
    )

    # Build context strings
    ctx = state.get("context", {})
    ingredients = ctx.get("ingredients", [])
    selected_recipe = ctx.get("selected_recipe") or ctx.get("recipe_context", {})
    recipe_name = selected_recipe.get("recipe", "None selected") if selected_recipe else "None selected"
    recipe_details = ""
    if selected_recipe:
        recipe_details = (
            f"Recipe: {selected_recipe.get('recipe', '')}. "
            f"Ingredients: {selected_recipe.get('ingredients', '')}. "
            f"Instructions: {str(selected_recipe.get('instruction', ''))[:300]}..."
        )

    system_prompt = CHAT_SYSTEM_PROMPT.format(
        user_preferences=_pref_summary(state.get("user_preferences")),
        ingredients=", ".join(ingredients) if ingredients else "Not specified",
        recipe_name=recipe_name,
        recipe_details=recipe_details or "No recipe selected yet",
    )

    # Build messages: system + optional summary context + conversation messages
    messages = [SystemMessage(content=system_prompt)]

    # Inject previous summary as context if it exists
    summary = state.get("summary", "")
    if summary:
        messages.append(SystemMessage(content=f"Previous conversation context: {summary}"))

    messages.extend(state["messages"])

    ai_msg = await llm.ainvoke(messages)
    parsed = _parse_json_response(ai_msg.content)

    result: Dict[str, Any] = {
        "response": parsed.get("content", ai_msg.content),
        "response_type": parsed.get("type", "chat"),
    }
    if parsed.get("type") == "recipe_update" and parsed.get("updated_recipe"):
        result["updated_recipe"] = parsed["updated_recipe"]

    return {
        "messages": [ai_msg],
        "response": result,
    }


async def summarize_node(state: ChatState) -> dict:
    """Summarize conversation when messages grow too long, then trim."""
    messages = state.get("messages", [])

    # Only summarize when we have more than 4 messages (2 exchanges)
    if len(messages) <= 4:
        return {}

    try:
        settings = get_settings()
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_text_model,
            google_api_key=settings.gemini_api_key,
        )

        # Build conversation text from all messages
        existing_summary = state.get("summary", "")
        conversation_parts = []
        if existing_summary:
            conversation_parts.append(f"Earlier context: {existing_summary}")
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "Annapurna"
            conversation_parts.append(f"{role}: {msg.content[:200]}")

        conversation_text = "\n".join(conversation_parts)

        resp = await llm.ainvoke([
            HumanMessage(content=SUMMARIZE_PROMPT.format(conversation=conversation_text))
        ])
        new_summary = resp.content.strip()

        # Keep only the last 2 messages (latest exchange), delete the rest
        delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]

        return {
            "summary": new_summary,
            "messages": delete_messages,
        }
    except Exception as e:
        print(f"[Summarize] Skipped: {e}")
        return {}


async def extract_preferences_node(state: ChatState) -> dict:
    """Extract user preferences (diet, region, community, etc.) from chat."""
    internal_user_id = state.get("internal_user_id")
    if not internal_user_id:
        return {}

    # Get the latest human message
    human_msgs = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    if not human_msgs:
        return {}
    latest_msg = human_msgs[-1].content

    # Quick keyword check before calling the LLM (save tokens)
    pref_keywords = [
        "spicy", "spice", "mild", "hot", "vegan", "vegetarian", "non-veg",
        "no onion", "no garlic", "jain", "gluten", "dairy", "allergy",
        "south indian", "north indian", "bengali", "gujarati", "punjabi",
        "maharashtrian", "marathi", "rajasthani", "kerala", "tamil",
        "brahmin", "muslim", "christian", "sikh",
        "don't eat", "avoid", "hate", "love", "prefer", "favourite", "favorite",
        "quick", "traditional", "one-pot", "healthy", "low oil", "diabetic",
        "family", "kids", "from", "i am", "i'm",
    ]
    if not any(kw in latest_msg.lower() for kw in pref_keywords):
        return {}

    try:
        settings = get_settings()
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_text_model,
            google_api_key=settings.gemini_api_key,
        )
        extract_msg = HumanMessage(
            content=PREFERENCE_EXTRACT_PROMPT.format(message=latest_msg)
        )
        resp = await llm.ainvoke([extract_msg])

        # Parse — strip markdown fences if present
        resp_text = resp.content.strip()
        if resp_text.startswith("```"):
            lines = resp_text.split("\n")[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            resp_text = "\n".join(lines).strip()

        prefs = json.loads(resp_text)

        # Only upsert if at least one field has data
        if any(v for v in prefs.values() if v):
            db = get_user_database()
            db.upsert_preferences(internal_user_id, prefs)
            return {"user_preferences": prefs}
    except Exception as e:
        print(f"[Preferences Extraction] Skipped: {e}")

    return {}


# ── Build Graph ──────────────────────────────────────────────

def build_chat_graph() -> StateGraph:
    """Create the LangGraph chat workflow."""
    graph = StateGraph(ChatState)
    graph.add_node("chat_node", chat_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("extract_preferences", extract_preferences_node)
    graph.add_edge(START, "chat_node")
    graph.add_edge("chat_node", "summarize")
    graph.add_edge("summarize", "extract_preferences")
    graph.add_edge("extract_preferences", END)
    return graph


# Compile once (checkpointer attached at invocation time)
_compiled_graph = None


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_chat_graph().compile(checkpointer=get_checkpointer())
    return _compiled_graph


# ── Public API ───────────────────────────────────────────────

async def invoke_chat_graph(
    user_id: str,
    internal_user_id: int,
    message: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Invoke the LangGraph chat workflow with memory.

    Args:
        user_id: auth0_sub — used as thread_id for checkpointing
        internal_user_id: DB users.id — for preference storage
        message: user's message text
        context: recipe / ingredients context dict

    Returns:
        Dict with response, response_type, and optionally updated_recipe
    """
    db = get_user_database()
    prefs = db.get_preferences(internal_user_id) or {}

    config = {"configurable": {"thread_id": user_id}}
    input_state = {
        "messages": [HumanMessage(content=message)],
        "context": context,
        "user_id": user_id,
        "internal_user_id": internal_user_id,
        "user_preferences": prefs,
        "response": {},
        "summary": "",
    }

    graph = _get_graph()
    result = await graph.ainvoke(input_state, config=config)
    return result.get("response", {"response": "Something went wrong.", "response_type": "chat"})
