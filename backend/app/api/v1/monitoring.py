"""Monitoring API routes."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from beanie.operators import And, GTE

from app.models.user import User
from app.models.metrics import RequestMetrics, GuardrailEvent
from app.schemas import MonitoringSummary, CostSummary, ErrorSummary, GuardrailSummary
from app.api.deps import get_current_user
from app.core.rbac import MANAGEMENT_ROLES
from app.core.exceptions import AuthorizationError

router = APIRouter()


def require_management(user: User = Depends(get_current_user)) -> User:
    """Require executive or admin role for monitoring access."""
    if user.role.value not in MANAGEMENT_ROLES:
        raise AuthorizationError("Management access required for monitoring")
    return user


@router.get("/summary", response_model=MonitoringSummary)
async def get_monitoring_summary(
    days: int = 7,
    user: User = Depends(require_management),
):
    """Get monitoring summary for the specified period."""
    since = datetime.utcnow() - timedelta(days=days)

    metrics = await RequestMetrics.find(
        RequestMetrics.created_at >= since
    ).to_list()

    total_requests = len(metrics)
    avg_latency = sum(m.latency_ms for m in metrics) / max(total_requests, 1)
    total_tokens = sum(m.total_tokens or 0 for m in metrics)
    total_cost = sum(m.estimated_cost_usd or 0 for m in metrics)
    guardrail_triggers = sum(1 for m in metrics if m.guardrail_triggered)
    error_count = sum(1 for m in metrics if m.status_code >= 400)

    return MonitoringSummary(
        total_requests=total_requests,
        avg_latency_ms=round(avg_latency, 2),
        total_tokens=total_tokens,
        total_cost_usd=round(total_cost, 6),
        guardrail_triggers=guardrail_triggers,
        error_count=error_count,
    )


@router.get("/costs", response_model=CostSummary)
async def get_cost_summary(
    days: int = 30,
    user: User = Depends(require_management),
):
    """Get cost breakdown by role and model."""
    since = datetime.utcnow() - timedelta(days=days)
    metrics = await RequestMetrics.find(
        RequestMetrics.created_at >= since
    ).to_list()

    total_cost = sum(m.estimated_cost_usd or 0 for m in metrics)

    cost_by_role: dict[str, float] = {}
    for m in metrics:
        role = m.user_role or "unknown"
        cost_by_role[role] = cost_by_role.get(role, 0) + (m.estimated_cost_usd or 0)

    return CostSummary(
        total_cost_usd=round(total_cost, 6),
        cost_by_role={k: round(v, 6) for k, v in cost_by_role.items()},
        cost_by_model={},
    )


@router.get("/errors", response_model=ErrorSummary)
async def get_error_summary(
    days: int = 7,
    limit: int = 50,
    user: User = Depends(require_management),
):
    """Get recent error summary."""
    since = datetime.utcnow() - timedelta(days=days)
    errors = await RequestMetrics.find(
        And(
            RequestMetrics.created_at >= since,
            RequestMetrics.status_code >= 400,
        )
    ).sort("-created_at").limit(limit).to_list()

    return ErrorSummary(
        total_errors=len(errors),
        recent_errors=[
            {
                "request_id": e.request_id,
                "endpoint": e.endpoint,
                "status_code": e.status_code,
                "error": e.error_message,
                "created_at": e.created_at.isoformat(),
            }
            for e in errors
        ],
    )


@router.get("/guardrails", response_model=GuardrailSummary)
async def get_guardrail_summary(
    days: int = 7,
    user: User = Depends(require_management),
):
    """Get guardrail trigger summary."""
    since = datetime.utcnow() - timedelta(days=days)
    events = await GuardrailEvent.find(
        GuardrailEvent.created_at >= since
    ).to_list()

    by_type: dict[str, int] = {}
    for e in events:
        by_type[e.guardrail_type] = by_type.get(e.guardrail_type, 0) + 1

    return GuardrailSummary(
        total_triggers=len(events),
        by_type=by_type,
    )


@router.get("/requests")
async def list_requests(
    days: int = 1,
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(require_management),
):
    """List recent request metrics."""
    since = datetime.utcnow() - timedelta(days=days)
    metrics = await RequestMetrics.find(
        RequestMetrics.created_at >= since
    ).sort("-created_at").skip(skip).limit(limit).to_list()

    return [
        {
            "request_id": m.request_id,
            "user_email": m.user_email,
            "user_role": m.user_role,
            "endpoint": m.endpoint,
            "status_code": m.status_code,
            "latency_ms": m.latency_ms,
            "total_tokens": m.total_tokens,
            "estimated_cost_usd": m.estimated_cost_usd,
            "guardrail_triggered": m.guardrail_triggered,
            "created_at": m.created_at.isoformat(),
        }
        for m in metrics
    ]
