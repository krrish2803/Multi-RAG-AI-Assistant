"""Evaluation API routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, BackgroundTasks

from app.config import Settings, get_settings
from app.models.user import User
from app.models.metrics import EvalRun, EvalResult
from app.schemas import EvalRunRequest, EvalRunResponse, EvalResultResponse
from app.api.deps import get_current_user
from app.core.rbac import MANAGEMENT_ROLES
from app.core.exceptions import AuthorizationError
from app.services.evaluation_service import EvaluationService

router = APIRouter()


def require_eval_access(user: User = Depends(get_current_user)) -> User:
    """Require admin or engineering role for evaluation access."""
    allowed = ["admin", "engineering", "executive"]
    if user.role.value not in allowed:
        raise AuthorizationError("Evaluation access restricted")
    return user


@router.post("/run", response_model=EvalRunResponse)
async def trigger_evaluation(
    request: EvalRunRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_eval_access),
    settings: Settings = Depends(get_settings),
):
    """Trigger a new evaluation run."""
    eval_run = EvalRun(
        run_name=request.run_name or f"eval-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        dataset_name=request.dataset_name,
        total_questions=0,
        status="pending",
        triggered_by=user.email,
    )
    await eval_run.insert()

    # Run evaluation in background
    background_tasks.add_task(run_evaluation_task, str(eval_run.id), request.dataset_name, settings)

    return EvalRunResponse(
        id=str(eval_run.id),
        run_name=eval_run.run_name,
        dataset_name=eval_run.dataset_name,
        total_questions=eval_run.total_questions,
        status=eval_run.status,
        created_at=eval_run.created_at,
    )


async def run_evaluation_task(run_id: str, dataset_name: str, settings: Settings):
    """Background task to run evaluation."""
    try:
        eval_run = await EvalRun.get(run_id)
        if eval_run:
            eval_run.status = "running"
            eval_run.started_at = datetime.utcnow()
            await eval_run.save()

        service = EvaluationService(settings)
        await service.run_evaluation(run_id, dataset_name)

        eval_run = await EvalRun.get(run_id)
        if eval_run:
            eval_run.status = "completed"
            eval_run.completed_at = datetime.utcnow()
            await eval_run.save()

    except Exception as e:
        eval_run = await EvalRun.get(run_id)
        if eval_run:
            eval_run.status = "failed"
            await eval_run.save()


@router.get("/runs", response_model=list[EvalRunResponse])
async def list_eval_runs(
    limit: int = 20,
    user: User = Depends(require_eval_access),
):
    """List all evaluation runs."""
    runs = await EvalRun.find().sort("-created_at").limit(limit).to_list()

    return [
        EvalRunResponse(
            id=str(r.id),
            run_name=r.run_name,
            dataset_name=r.dataset_name,
            total_questions=r.total_questions,
            status=r.status,
            started_at=r.started_at,
            completed_at=r.completed_at,
            created_at=r.created_at,
        )
        for r in runs
    ]


@router.get("/results/{run_id}", response_model=list[EvalResultResponse])
async def get_eval_results(
    run_id: str,
    user: User = Depends(require_eval_access),
):
    """Get results for a specific evaluation run."""
    results = await EvalResult.find(EvalResult.run_id == run_id).to_list()

    return [
        EvalResultResponse(
            id=str(r.id),
            run_id=r.run_id,
            question=r.question,
            ground_truth=r.ground_truth,
            generated_answer=r.generated_answer,
            faithfulness=r.faithfulness,
            answer_relevancy=r.answer_relevancy,
            context_precision=r.context_precision,
            context_recall=r.context_recall,
        )
        for r in results
    ]
