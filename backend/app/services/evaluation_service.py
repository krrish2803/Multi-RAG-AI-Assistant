"""Evaluation service - Ragas integration for RAG quality assessment."""

import json
import os
from datetime import datetime
from typing import Optional

from app.config import Settings
from app.models.metrics import EvalRun, EvalResult


class EvaluationService:
    """Service for running RAG evaluation using Ragas."""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def run_evaluation(self, run_id: str, dataset_name: str = "default") -> dict:
        """Run evaluation on a test dataset."""
        # Load test dataset
        dataset_path = f"/app/data/evaluation/{dataset_name}_dataset.json"
        if not os.path.exists(dataset_path):
            dataset_path = f"data/evaluation/{dataset_name}_dataset.json"

        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Evaluation dataset not found: {dataset_path}")

        with open(dataset_path, "r") as f:
            dataset = json.load(f)

        eval_run = await EvalRun.get(run_id)
        if eval_run:
            eval_run.total_questions = len(dataset)
            await eval_run.save()

        results = []
        for item in dataset:
            # For each question, we'd run the RAG pipeline and compare
            # For now, store the dataset as-is for manual evaluation
            result = EvalResult(
                run_id=run_id,
                question=item.get("question", ""),
                ground_truth=item.get("ground_truth", ""),
                generated_answer=item.get("expected_answer", "Pending evaluation"),
                contexts=item.get("contexts", []),
                faithfulness=None,
                answer_relevancy=None,
                context_precision=None,
                context_recall=None,
            )
            await result.insert()
            results.append(result)

        return {"total": len(results), "run_id": run_id}
