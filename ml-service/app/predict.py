import json
from functools import lru_cache
from typing import Any

from app.features import category_multiplier
from app.model_registry import active_model_path
from app.schemas import DurationPrediction, DurationTaskInput

HEURISTIC_MODEL_NAME = "heuristic-duration"
HEURISTIC_MODEL_VERSION = "0.1.0"

# Confidence floors when no learned error profile exists: heuristic predictions
# and artifacts trained before error profiles were recorded.
HEURISTIC_BASE_CONFIDENCE = 0.45
ARTIFACT_BASE_CONFIDENCE = 0.6
EXECUTION_SIGNAL_BONUS = 0.1
CONFIDENCE_FLOOR = 0.2
CONFIDENCE_CEILING = 0.95


def predict_duration(task: DurationTaskInput) -> DurationPrediction:
    model = load_duration_model()
    predicted_minutes = calculate_predicted_minutes(task, model)
    model_name, _, _ = get_active_model_metadata(model)

    if model is not None:
        reason = "trained local artifact blended with execution logs" if task.actual_minutes > 0 else "trained local artifact"
    else:
        reason = "blended with execution logs" if task.actual_minutes > 0 else "feature baseline"

    return DurationPrediction(
        task_id=task.task_id,
        predicted_minutes=predicted_minutes,
        confidence=calculate_confidence(task, model),
        model_name=model_name,
        reason=reason,
    )


def calculate_confidence(task: DurationTaskInput, model: dict[str, Any] | None) -> float:
    """Derive confidence from the model's learned error profile for the task's category.

    A category whose historical error is small relative to the estimate scores
    high; unknown categories fall back to the global error, and artifacts
    without an error profile fall back to a documented base value.
    """
    if model is None:
        confidence = HEURISTIC_BASE_CONFIDENCE
    else:
        category_mae = model.get("category_mae", {}).get(task.category, model.get("global_mae"))
        if isinstance(category_mae, (int, float)):
            confidence = 1 - (float(category_mae) / max(task.estimated_minutes, 1))
        else:
            confidence = ARTIFACT_BASE_CONFIDENCE

    if task.actual_minutes > 0:
        confidence += EXECUTION_SIGNAL_BONUS

    return round(min(CONFIDENCE_CEILING, max(CONFIDENCE_FLOOR, confidence)), 2)


def calculate_predicted_minutes(task: DurationTaskInput, model: dict[str, Any] | None = None) -> int:
    if model is not None:
        baseline_prediction = calculate_artifact_prediction(task, model)
    else:
        baseline_prediction = calculate_heuristic_prediction(task)

    if task.actual_minutes > 0:
        blend_weight = 0.45 if model is not None else 0.35
        baseline_prediction = (baseline_prediction * (1 - blend_weight)) + (task.actual_minutes * blend_weight)

    return clamp_minutes(round(baseline_prediction))


def calculate_heuristic_prediction(task: DurationTaskInput) -> float:
    difficulty_factor = 1 + ((task.difficulty - 3) * 0.08)
    focus_factor = 1.06 if task.requires_focus else 1.0
    priority_factor = 1 + max(0, task.priority - 3) * 0.02
    baseline_prediction = task.estimated_minutes * category_multiplier(task.category)
    baseline_prediction *= difficulty_factor * focus_factor * priority_factor
    return baseline_prediction


def calculate_artifact_prediction(task: DurationTaskInput, model: dict[str, Any]) -> float:
    category_multipliers = model.get("category_multipliers", {})
    global_multiplier = float(model.get("global_multiplier", 1.0))
    learned_category_multiplier = float(category_multipliers.get(task.category, global_multiplier))
    difficulty_weight = float(model.get("difficulty_weight", 0.04))
    priority_weight = float(model.get("priority_weight", 0.015))
    focus_multiplier = float(model.get("focus_multiplier", 1.05))

    prediction = task.estimated_minutes * learned_category_multiplier
    prediction *= 1 + ((task.difficulty - 3) * difficulty_weight)
    prediction *= 1 + max(0, task.priority - 3) * priority_weight
    if task.requires_focus:
        prediction *= focus_multiplier

    return prediction


def clamp_minutes(value: int) -> int:
    return min(480, max(1, value))


@lru_cache(maxsize=1)
def load_duration_model() -> dict[str, Any] | None:
    model_path = active_model_path()
    if not model_path.exists():
        return None

    with model_path.open("r", encoding="utf-8") as model_file:
        model = json.load(model_file)

    if "model_name" not in model or "model_version" not in model:
        return None

    return model


def get_active_model_metadata(model: dict[str, Any] | None = None) -> tuple[str, str, str]:
    active_model = load_duration_model() if model is None else model
    if active_model is None:
        return HEURISTIC_MODEL_NAME, HEURISTIC_MODEL_VERSION, "heuristic"

    return (
        str(active_model["model_name"]),
        str(active_model["model_version"]),
        str(active_model.get("source", "local-artifact")),
    )


def reset_model_cache() -> None:
    load_duration_model.cache_clear()
