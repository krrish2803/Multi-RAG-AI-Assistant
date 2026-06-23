"""LangGraph RAG pipeline orchestration."""

import time
from typing import Optional

from app.config import Settings
from app.rag.state import RAGState
from app.rag.nodes.input_guard import input_guard_node
from app.rag.nodes.retrieval import retrieval_node
from app.rag.nodes.generation import generation_node
from app.rag.nodes.output_guard import output_guard_node
from app.rag.nodes.fallback import fallback_node


class RAGGraph:
    """RAG pipeline using a graph-based approach (inspired by LangGraph).
    
    Flow: input_guard -> [safe] -> retrieval -> generation -> output_guard -> END
                      -> [blocked] -> fallback -> END
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    async def run(
        self,
        user_query: str,
        user_role: str,
        user_departments: list[str],
        conversation_history: list[dict],
        request_id: str,
        document_ids: Optional[list[str]] = None,
    ) -> dict:
        """Execute the RAG pipeline."""
        start_time = time.perf_counter()

        # Initialize state
        state: RAGState = {
            "user_query": user_query,
            "user_role": user_role,
            "user_departments": user_departments or [],
            "conversation_history": conversation_history or [],
            "request_id": request_id,
            "document_ids": document_ids,
            "guardrail_result": None,
            "retrieved_documents": None,
            "generated_response": None,
            "output_guard_result": None,
            "token_usage": None,
            "latency_ms": None,
            "error": None,
            "blocked": False,
            "block_reason": None,
            "sources": None,
            "guardrail_flags": [],
        }

        try:
            # Step 1: Input Guard
            guard_result = await input_guard_node(state)
            state.update(guard_result)

            if state.get("blocked"):
                # Route to fallback
                fallback_result = await fallback_node(state)
                state.update(fallback_result)
                return self._build_result(state, start_time)

            # Step 2: Retrieval with RBAC
            retrieval_result = await retrieval_node(state, self.settings)
            state.update(retrieval_result)

            # Step 3: Generation
            generation_result = await generation_node(state, self.settings)
            state.update(generation_result)

            # Step 4: Output Guard
            output_result = await output_guard_node(state)
            state.update(output_result)

            if state.get("blocked"):
                fallback_result = await fallback_node(state)
                state.update(fallback_result)

        except Exception as e:
            state["error"] = str(e)
            state["generated_response"] = (
                "I apologize, but an error occurred while processing your request. "
                "Please try again later."
            )
            state["blocked"] = True
            state["block_reason"] = f"System error: {str(e)[:100]}"

        return self._build_result(state, start_time)

    def _build_result(self, state: RAGState, start_time: float) -> dict:
        """Build the final result from pipeline state."""
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        return {
            "response": state.get("generated_response", "No response generated."),
            "sources": state.get("sources") or [],
            "blocked": state.get("blocked", False),
            "block_reason": state.get("block_reason"),
            "prompt_tokens": state.get("prompt_tokens", 0),
            "completion_tokens": state.get("completion_tokens", 0),
            "total_tokens": state.get("total_tokens", 0),
            "estimated_cost": state.get("estimated_cost", 0.0),
            "latency_ms": latency_ms,
            "guardrail_flags": state.get("guardrail_flags", []),
            "request_id": state["request_id"],
        }
