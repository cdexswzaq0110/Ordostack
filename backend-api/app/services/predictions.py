import os
from datetime import date
from typing import Any

import httpx

from app.schemas.predictions import DurationPredictionResponse
from app.schemas.tasks import TaskRead
from app.services import analytics as analytics_service
from app.services import tasks as task_service

DEFAULT_ML_SERVICE_URL = "http://ml-service:8200"
ML_TIMEOUT_SECONDS = 8.0
FALLBACK_MODEL_NAME = "estimate-fallback"
FALLBACK_MODEL_VERSION = "0.1.0"


def get_duration_predictions(user_id: int, target_date: date) -> DurationPredictionResponse:
    tasks = task_service.list_tasks(user_id=user_id, target_date=target_date)
    return predict_for_tasks(user_id=user_id, target_date=target_date, tasks=tasks)


def predict_for_tasks(
    user_id: int,
    target_date: date,
    tasks: list[TaskRead],
) -> DurationPredictionResponse:
    ml_payload = build_ml_payload(user_id=user_id, target_date=target_date, tasks=tasks)
    ml_url = os.getenv("ML_SERVICE_URL", DEFAULT_ML_SERVICE_URL).rstrip("/")

    try:
        response = httpx.post(
            f"{ml_url}/duration/predict",
            json=ml_payload,
            timeout=ML_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.RequestError:
        return build_fallback_predictions(user_id=user_id, target_date=target_date, tasks=tasks)
    except httpx.HTTPStatusError:
        return build_fallback_predictions(user_id=user_id, target_date=target_date, tasks=tasks)

    payload = response.json()
    return DurationPredictionResponse(
        user_id=user_id,
        target_date=target_date,
        model_name=payload["model_name"],
        model_version=payload["model_version"],
        predictions=payload["predictions"],
    )


def build_ml_payload(user_id: int, target_date: date, tasks: list[TaskRead]) -> dict[str, Any]:
    analytics = analytics_service.get_daily_analytics(user_id=user_id, target_date=target_date)
    actual_minutes_by_task = {summary.task_id: summary.actual_minutes for summary in analytics.task_summaries}

    return {
        "user_id": user_id,
        "tasks": [
            {
                "task_id": task.id,
                "title": task.title,
                "category": task.category,
                "estimated_minutes": task.estimated_minutes,
                "priority": task.priority,
                "difficulty": task.difficulty,
                "requires_focus": task.requires_focus,
                "actual_minutes": actual_minutes_by_task.get(task.id, 0),
            }
            for task in tasks
        ],
    }


def build_fallback_predictions(
    user_id: int,
    target_date: date,
    tasks: list[TaskRead],
) -> DurationPredictionResponse:
    return DurationPredictionResponse(
        user_id=user_id,
        target_date=target_date,
        model_name=FALLBACK_MODEL_NAME,
        model_version=FALLBACK_MODEL_VERSION,
        predictions=[
            {
                "task_id": task.id,
                "predicted_minutes": task.estimated_minutes,
                "confidence": 0.2,
                "model_name": FALLBACK_MODEL_NAME,
                "reason": "ml-service unavailable",
            }
            for task in tasks
        ],
    )
