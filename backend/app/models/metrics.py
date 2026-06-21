"""Metrics and evaluation models."""

from datetime import datetime
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field


class RequestMetrics(Document):
    """Per-request metrics for monitoring."""

    request_id: str
    user_id: str
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    endpoint: str
    method: str
    status_code: int
    latency_ms: int
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    estimated_cost_usd: Optional[float] = None
    guardrail_triggered: bool = False
    guardrail_type: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "request_metrics"


class GuardrailEvent(Document):
    """Guardrail trigger events for audit."""

    request_id: str
    user_id: str
    guardrail_type: str  # injection, jailbreak, pii, scope
    action: str  # blocked, redacted, flagged, allowed
    input_text: Optional[str] = None
    output_text: Optional[str] = None
    confidence: Optional[float] = None
    details: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "guardrail_events"


class EvalRun(Document):
    """Evaluation run metadata."""

    run_name: str
    dataset_name: str
    total_questions: int
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    triggered_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "eval_runs"


class EvalResult(Document):
    """Individual evaluation results."""

    run_id: Indexed(str)
    question: str
    ground_truth: str
    generated_answer: str
    contexts: list[str] = Field(default_factory=list)
    faithfulness: Optional[float] = None
    answer_relevancy: Optional[float] = None
    context_precision: Optional[float] = None
    context_recall: Optional[float] = None
    role_compliant: Optional[bool] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "eval_results"
