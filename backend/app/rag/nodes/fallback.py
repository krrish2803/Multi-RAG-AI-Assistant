"""Fallback node - handles blocked or error cases."""

from app.rag.state import RAGState
from app.rag.prompts import REFUSAL_PROMPT


async def fallback_node(state: RAGState) -> dict:
    """Generate a refusal or error response."""
    reason = state.get("block_reason", "The request could not be processed.")

    response = REFUSAL_PROMPT.format(reason=reason)

    return {
        "generated_response": response,
        "blocked": True,
        "block_reason": reason,
        "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "estimated_cost": 0.0,
        "sources": [],
    }
