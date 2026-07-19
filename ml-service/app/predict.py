import json
from functools import lru_cache
from typing import Any

from app.data_contract import (
    PREDICTION_MAX_MINUTES,
    PREDICTION_MIN_MINUTES,
    SCHEMA_VERSION,
    linear_contributions,
    linear_predict,
    normalize_category,
)
from app.features import category_multiplier
from app.model_registry import active_model_path
from app.schemas import DurationPrediction, DurationTaskInput, PredictionFactor

HEURISTIC_MODEL_NAME = "heuristic-duration"
HEURISTIC_MODEL_VERSION = "0.1.0"

# Confidence floors when no learned error profile exists: heuristic predictions
# and artifacts trained before error profiles were recorded.
HEURISTIC_BASE_CONFIDENCE = 0.45
ARTIFACT_BASE_CONFIDENCE = 0.6
EXECUTION_SIGNAL_BONUS = 0.1
CONFIDENCE_FLOOR = 0.2
CONFIDENCE_CEILING = 0.95

# Reliability labels derived from the historical error band relative to the
# prediction. These are honest descriptors of past error, not probabilities.
RELIABILITY_MIN_SAMPLES = 3
RELIABILITY_HIGH_RATIO = 0.15
RELIABILITY_MEDIUM_RATIO = 0.35

# An estimate wildly outside the training range means the model is
# extrapolating; the flag warns downstream consumers.
OOD_RANGE_FACTOR = 2.0

# Only artifacts whose schema shares our major version are servable.
SUPPORTED_SCHEMA_MAJOR = SCHEMA_VERSION.split(".")[0]

LINEAR_ARTIFACT_KEYS = ("categories", "scaler_mean", "scaler_scale", "coefficients", "intercept", "feature_names")


def predict_duration(task: DurationTaskInput) -> DurationPrediction:
    model = load_duration_model()
    predicted_minutes = calculate_predicted_minutes(task, model)
    model_name, model_version, _ = get_active_model_metadata(model)

    if model is not None:
        reason = "trained local artifact blended with execution logs" if task.actual_minutes > 0 else "trained local artifact"
    else:
        reason = "blended with execution logs" if task.actual_minutes > 0 else "feature baseline"

    error_band, sample_count = get_error_profile(task, model)
    lower_bound, upper_bound = calculate_bounds(predicted_minutes, error_band)

    return DurationPrediction(
        task_id=task.task_id,
        predicted_minutes=predicted_minutes,
        confidence=calculate_confidence(task, model),
        model_name=model_name,
        reason=reason,
        model_version=model_version,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        reliability=calculate_reliability(predicted_minutes, error_band, sample_count, model),
        sample_count=sample_count,
        fallback=model is None,
        out_of_distribution=is_out_of_distribution(task, model),
        factors=calculate_factors(task, model),
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


def get_error_profile(task: DurationTaskInput, model: dict[str, Any] | None) -> tuple[float | None, int | None]:
    """(historical error band in minutes, category sample count) for the task.

    Both are None when the active model has no learned error profile — the
    caller then reports insufficient data instead of inventing an interval.
    """
    if model is None:
        return None, 0

    category = normalize_category(task.category)
    category_mae = model.get("category_mae", {}).get(category, model.get("global_mae"))
    band = float(category_mae) if isinstance(category_mae, (int, float)) else None

    sample_counts = model.get("category_sample_counts")
    if isinstance(sample_counts, dict):
        sample_count = int(sample_counts.get(category, 0))
    else:
        sample_count = None
    return band, sample_count


def calculate_bounds(predicted_minutes: int, error_band: float | None) -> tuple[int | None, int | None]:
    if error_band is None:
        return None, None
    lower = max(PREDICTION_MIN_MINUTES, round(predicted_minutes - error_band))
    upper = min(PREDICTION_MAX_MINUTES, round(predicted_minutes + error_band))
    return lower, upper


def calculate_reliability(
    predicted_minutes: int,
    error_band: float | None,
    sample_count: int | None,
    model: dict[str, Any] | None,
) -> str:
    if model is None or error_band is None:
        return "insufficient-data"
    if sample_count is not None and sample_count < RELIABILITY_MIN_SAMPLES:
        return "insufficient-data"

    ratio = error_band / max(predicted_minutes, 1)
    if ratio <= RELIABILITY_HIGH_RATIO:
        return "high"
    if ratio <= RELIABILITY_MEDIUM_RATIO:
        return "medium"
    return "low"


def is_out_of_distribution(task: DurationTaskInput, model: dict[str, Any] | None) -> bool:
    if model is None:
        return False

    category = normalize_category(task.category)
    known_categories = model.get("categories") or list(model.get("category_multipliers", {}))
    if known_categories and category not in known_categories:
        return True

    estimate_range = model.get("estimated_minutes_range")
    if isinstance(estimate_range, list) and len(estimate_range) == 2:
        low, high = estimate_range
        if task.estimated_minutes > high * OOD_RANGE_FACTOR or task.estimated_minutes < low / OOD_RANGE_FACTOR:
            return True
    return False


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
    if model.get("model_type") == "linear-json":
        return linear_predict(task_features(task), model)
    return calculate_multiplier_prediction(task, model)


def calculate_multiplier_prediction(task: DurationTaskInput, model: dict[str, Any]) -> float:
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


def task_features(task: DurationTaskInput) -> dict[str, Any]:
    return {
        "category": task.category,
        "estimated_minutes": task.estimated_minutes,
        "priority": task.priority,
        "difficulty": task.difficulty,
        "requires_focus": task.requires_focus,
    }


def calculate_factors(task: DurationTaskInput, model: dict[str, Any] | None) -> list[PredictionFactor]:
    """Break the prediction into named contributions, largest impact first.

    Linear artifacts use exact coefficient contributions (they sum to the
    unclamped prediction); multiplier/heuristic paths report the delta each
    multiplicative step adds. The execution-log blend appears as its own
    factor so users can see when live signals moved the number.
    """
    if model is not None and model.get("model_type") == "linear-json":
        contributions = linear_contributions(task_features(task), model)
        factors = [PredictionFactor(name=name, impact_minutes=round(impact, 1)) for name, impact in contributions.items()]
    else:
        factors = multiplicative_factors(task, model)

    pre_blend = (
        calculate_artifact_prediction(task, model) if model is not None else calculate_heuristic_prediction(task)
    )
    if task.actual_minutes > 0:
        blend_weight = 0.45 if model is not None else 0.35
        blended = (pre_blend * (1 - blend_weight)) + (task.actual_minutes * blend_weight)
        factors.append(PredictionFactor(name="execution_log_blend", impact_minutes=round(blended - pre_blend, 1)))

    return sorted(factors, key=lambda factor: abs(factor.impact_minutes), reverse=True)


def multiplicative_factors(task: DurationTaskInput, model: dict[str, Any] | None) -> list[PredictionFactor]:
    if model is not None:
        multiplier = float(
            model.get("category_multipliers", {}).get(task.category, model.get("global_multiplier", 1.0))
        )
        difficulty_weight = float(model.get("difficulty_weight", 0.04))
        priority_weight = float(model.get("priority_weight", 0.015))
        focus_multiplier = float(model.get("focus_multiplier", 1.05)) if task.requires_focus else 1.0
    else:
        multiplier = category_multiplier(task.category)
        difficulty_weight = 0.08
        priority_weight = 0.02
        focus_multiplier = 1.06 if task.requires_focus else 1.0

    steps = [
        ("category_history", multiplier),
        ("difficulty", 1 + ((task.difficulty - 3) * difficulty_weight)),
        ("priority", 1 + max(0, task.priority - 3) * priority_weight),
        ("focus_requirement", focus_multiplier),
    ]
    factors = [PredictionFactor(name="baseline_estimate", impact_minutes=float(task.estimated_minutes))]
    running = float(task.estimated_minutes)
    for name, step_multiplier in steps:
        factors.append(PredictionFactor(name=name, impact_minutes=round(running * (step_multiplier - 1), 1)))
        running *= step_multiplier
    return factors


def clamp_minutes(value: int) -> int:
    return min(PREDICTION_MAX_MINUTES, max(PREDICTION_MIN_MINUTES, value))


@lru_cache(maxsize=1)
def load_duration_model() -> dict[str, Any] | None:
    """Load the active artifact, falling back to None (heuristic) on any defect.

    A corrupted file, an unreadable path, a missing required key, or an
    artifact from an incompatible schema major version must degrade to the
    heuristic instead of taking the service down.
    """
    model_path = active_model_path()
    if not model_path.exists():
        return None

    try:
        with model_path.open("r", encoding="utf-8") as model_file:
            model = json.load(model_file)
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(model, dict) or "model_name" not in model or "model_version" not in model:
        return None

    schema_version = model.get("schema_version")
    if isinstance(schema_version, str) and schema_version.split(".")[0] != SUPPORTED_SCHEMA_MAJOR:
        return None

    if model.get("model_type") == "linear-json" and any(key not in model for key in LINEAR_ARTIFACT_KEYS):
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
