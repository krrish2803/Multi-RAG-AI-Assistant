"""RAG pipeline state definition."""

from typing import TypedDict, Optional


class RAGState(TypedDict):
    """State schema for the LangGraph RAG pipeline."""

    # Inputs
    user_query: str
    user_role: str
    user_departments: list[str]
    conversation_history: list[dict]
    request_id: str

    # Pipeline data
    guardrail_result: Optional[dict]
    retrieved_documents: Optional[list[dict]]
    generated_response: Optional[str]
    output_guard_result: Optional[dict]

    # Metadata
    token_usage: Optional[dict]
    latency_ms: Optional[int]
    error: Optional[str]
    blocked: bool
    block_reason: Optional[str]
    sources: Optional[list[dict]]
    guardrail_flags: Optional[list[str]]
