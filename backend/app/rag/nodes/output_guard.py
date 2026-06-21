"""Output guard node - runs post-generation safety checks."""

from app.rag.state import RAGState
from app.guardrails.pii import PIIDetector


async def output_guard_node(state: RAGState) -> dict:
    """Run output guardrails on generated response."""
    response = state.get("generated_response", "")
    flags = list(state.get("guardrail_flags", []))

    pii = PIIDetector()
    pii_result = pii.scan(response)

    blocked = False
    block_reason = None

    # Redact PII from output
    redacted_response = response
    if pii_result.get("contains_pii"):
        redacted_response = pii.redact(response)
        flags.append("output_pii_redacted")

    return {
        "generated_response": redacted_response,
        "output_guard_result": {
            "blocked": blocked,
            "pii_detected": pii_result.get("contains_pii", False),
            "redacted": redacted_response != response,
        },
        "blocked": blocked,
        "block_reason": block_reason,
        "guardrail_flags": flags,
    }
