from datetime import date, timedelta
from statistics import median
from typing import Any

import httpx

from app.config import load_runtime_config
from app.repositories.store import get_store
from app.schemas.predictions import (
    DurationFeedbackExportResponse,
    DurationPredictionResponse,
    PredictionAccuracyDay,
    PredictionAccuracyResponse,
)
from app.schemas.tasks import TaskRead
from app.services import analytics as analytics_service
from app.services import tasks as task_service

ML_TIMEOUT_SECONDS = 8.0
FALLBACK_MODEL_NAME = "estimate-fallback"
FALLBACK_MODEL_VERSION = "0.1.0"

CALIBRATION_MIN_SAMPLES = 3
CALIBRATION_WINDOW = 20
CALIBRATION_FLOOR = 0.5
CALIBRATION_CEILING = 2.0
PREDICTION_MAX_MINUTES = 480


def get_duration_predictions(user_id: int, target_date: date) -> DurationPredictionResponse:
    tasks = task_service.list_tasks(user_id=user_id, target_date=target_date)
    return predict_for_tasks(user_id=user_id, target_date=target_date, tasks=tasks)


def export_duration_feedback(user_id: int, target_date: date) -> DurationFeedbackExportResponse:
    tasks = task_service.list_tasks(user_id=user_id, target_date=target_date)
    analytics = analytics_service.get_daily_analytics(user_id=user_id, target_date=target_date)
    actual_minutes_by_task = {summary.task_id: summary.actual_minutes for summary in analytics.task_summaries}
    rows = [["category", "estimated_minutes", "priority", "difficulty", "requires_focus", "actual_minutes"]]
    for task in tasks:
        actual_minutes = actual_minutes_by_task.get(task.id, 0)
        if task.status != "completed" or actual_minutes <= 0:
            continue
        rows.append(
            [
                task.category,
                str(task.estimated_minutes),
                str(task.priority),
                str(task.difficulty),
                "true" if task.requires_focus else "false",
                str(actual_minutes),
            ],
        )

    content = "\n".join(",".join(csv_escape(value) for value in row) for row in rows) + "\n"
    return DurationFeedbackExportResponse(
        filename=f"duration-feedback-{target_date.isoformat()}.csv",
        content_type="text/csv",
        row_count=max(0, len(rows) - 1),
        content=content,
    )


def log_served_predictions(
    user_id: int,
    target_date: date,
    tasks: list[TaskRead],
    prediction_response: DurationPredictionResponse,
) -> int:
    """Persist the predictions a generated plan was built on, for later accuracy pairing."""
    estimated_by_task = {task.id: task.estimated_minutes for task in tasks}
    entries = [
        {
            "user_id": user_id,
            "task_id": prediction.task_id,
            "target_date": target_date,
            "model_name": prediction.model_name,
            "model_version": prediction_response.model_version,
            "predicted_minutes": prediction.predicted_minutes,
            "raw_predicted_minutes": prediction.raw_predicted_minutes or prediction.predicted_minutes,
            "estimated_minutes": estimated_by_task.get(prediction.task_id, prediction.predicted_minutes),
        }
        for prediction in prediction_response.predictions
        if prediction.task_id in estimated_by_task
    ]
    if not entries:
        return 0
    return len(get_store().create_prediction_logs(entries))


def record_prediction_actual(user_id: int, task_id: int, actual_minutes: int) -> int:
    if actual_minutes <= 0:
        return 0
    return get_store().record_prediction_actual(user_id=user_id, task_id=task_id, actual_minutes=actual_minutes)


def get_prediction_accuracy(user_id: int, days: int = 90) -> PredictionAccuracyResponse:
    since_date = date.today() - timedelta(days=days)
    logs = get_store().list_prediction_logs(user_id=user_id, since_date=since_date)
    paired_logs = [log for log in logs if log["actual_minutes"] is not None]

    daily: list[PredictionAccuracyDay] = []
    for day in sorted({log["target_date"] for log in paired_logs}):
        day_logs = [log for log in paired_logs if log["target_date"] == day]
        daily.append(
            PredictionAccuracyDay(
                target_date=day,
                paired_count=len(day_logs),
                model_mae=mean_absolute_error(day_logs, "predicted_minutes"),
                estimate_mae=mean_absolute_error(day_logs, "estimated_minutes"),
            )
        )

    model_mae = mean_absolute_error(paired_logs, "predicted_minutes") if paired_logs else None
    estimate_mae = mean_absolute_error(paired_logs, "estimated_minutes") if paired_logs else None
    improvement_ratio = (
        round(1 - (model_mae / estimate_mae), 4) if model_mae is not None and estimate_mae else None
    )

    return PredictionAccuracyResponse(
        user_id=user_id,
        window_days=days,
        logged_count=len(logs),
        paired_count=len(paired_logs),
        model_mae=model_mae,
        estimate_mae=estimate_mae,
        improvement_ratio=improvement_ratio,
        daily=daily,
    )


def mean_absolute_error(logs: list[dict[str, Any]], prediction_field: str) -> float:
    if not logs:
        return 0.0
    total_error = sum(abs(log[prediction_field] - log["actual_minutes"]) for log in logs)
    return round(total_error / len(logs), 2)


def predict_for_tasks(
    user_id: int,
    target_date: date,
    tasks: list[TaskRead],
) -> DurationPredictionResponse:
    ml_payload = build_ml_payload(user_id=user_id, target_date=target_date, tasks=tasks)
    ml_url = load_runtime_config().ml_service_url

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
    calibration_factor, calibration_samples = get_user_calibration(user_id)
    predictions = [
        {
            **prediction,
            "raw_predicted_minutes": prediction["predicted_minutes"],
            "predicted_minutes": calibrate_minutes(prediction["predicted_minutes"], calibration_factor),
        }
        for prediction in payload["predictions"]
    ]
    return DurationPredictionResponse(
        user_id=user_id,
        target_date=target_date,
        model_name=payload["model_name"],
        model_version=payload["model_version"],
        predictions=predictions,
        calibration_factor=calibration_factor,
        calibration_samples=calibration_samples,
    )


def get_user_calibration(user_id: int) -> tuple[float | None, int]:
    """Median actual/predicted ratio over the user's recent paired predictions.

    The ratio uses the raw model output rather than the served (already
    calibrated) value, so the factor cannot feed back on itself. Returns
    (None, samples) until enough pairs exist; the factor is clamped so a few
    unusual tasks cannot swing predictions wildly.
    """
    logs = get_store().list_prediction_logs(user_id=user_id)
    ratios = [
        log["actual_minutes"] / log["raw_predicted_minutes"]
        for log in logs
        if log["actual_minutes"] and (log.get("raw_predicted_minutes") or 0) > 0
    ][-CALIBRATION_WINDOW:]

    if len(ratios) < CALIBRATION_MIN_SAMPLES:
        return None, len(ratios)

    factor = min(CALIBRATION_CEILING, max(CALIBRATION_FLOOR, median(ratios)))
    return round(factor, 3), len(ratios)


def calibrate_minutes(predicted_minutes: int, calibration_factor: float | None) -> int:
    if calibration_factor is None:
        return predicted_minutes
    return min(PREDICTION_MAX_MINUTES, max(1, round(predicted_minutes * calibration_factor)))


def csv_escape(value: str) -> str:
    if any(character in value for character in [",", "\"", "\n", "\r"]):
        return '"' + value.replace('"', '""') + '"'
    return value


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
