"""Input guard node - runs pre-retrieval safety checks."""

import asyncio
from app.rag.state import RAGState
from app.guardrails.injection import InjectionDetector
from app.guardrails.jailbreak import JailbreakDetector
from app.guardrails.pii import PIIDetector
from app.guardrails.scope import ScopeDetector


async def input_guard_node(state: RAGState) -> dict:
    """Run input guardrails before retrieval."""
    query = state["user_query"]
    flags = []

    # Run all detectors
    injection = InjectionDetector()
    jailbreak = JailbreakDetector()
    pii = PIIDetector()
    scope = ScopeDetector()

    injection_result = injection.check(query)
    jailbreak_result = jailbreak.check(query)
    pii_result = pii.scan(query)
    scope_result = scope.check(query)

    blocked = False
    block_reason = None

    if injection_result.get("blocked"):
        blocked = True
        block_reason = "Potential prompt injection detected"
        flags.append("injection")

    if jailbreak_result.get("blocked"):
        blocked = True
        block_reason = "Potential jailbreak attempt detected"
        flags.append("jailbreak")

    if pii_result.get("contains_pii"):
        flags.append("pii_detected")
        # Don't block, just flag

    if scope_result.get("blocked"):
        blocked = True
        block_reason = "Question is outside the scope of this assistant"
        flags.append("out_of_scope")

    return {
        "guardrail_result": {
            "blocked": blocked,
            "reason": block_reason,
            "details": {
                "injection": injection_result,
                "jailbreak": jailbreak_result,
                "pii": pii_result,
                "scope": scope_result,
            },
        },
        "blocked": blocked,
        "block_reason": block_reason,
        "guardrail_flags": flags,
    }
