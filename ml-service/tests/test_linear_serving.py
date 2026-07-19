"""Serving behavior for linear-json artifacts, degraded artifacts, and the
honest reliability/explainability fields."""

import json

from fastapi.testclient import TestClient

from app.main import app
from app.predict import reset_model_cache

LINEAR_ARTIFACT = {
    "model_name": "duration-linear",
    "model_version": "0.3.0",
    "model_type": "linear-json",
    "estimator": "ridge",
    "source": "local-artifact",
    "schema_version": "1.0.0",
    "categories": ["coding", "study"],
    "feature_names": [
        "estimated_minutes",
        "priority",
        "difficulty",
        "requires_focus",
        "category=coding",
        "category=study",
    ],
    "scaler_mean": [60.0, 3.0, 3.0, 0.5, 0.5, 0.5],
    "scaler_scale": [30.0, 1.0, 1.0, 0.5, 0.5, 0.5],
    "coefficients": [30.0, 1.0, 2.0, 1.0, -1.0, 2.0],
    "intercept": 70.0,
    "category_mae": {"coding": 6.0, "study": 20.0},
    "global_mae": 12.0,
    "category_sample_counts": {"coding": 5, "study": 6},
    "estimated_minutes_range": [30, 120],
}


def make_task(**overrides) -> dict:
    task = {
        "task_id": 1,
        "title": "probe",
        "category": "study",
        "estimated_minutes": 60,
        "priority": 3,
        "difficulty": 3,
        "requires_focus": True,
        "actual_minutes": 0,
    }
    task.update(overrides)
    return task


def predict_with_artifact(monkeypatch, tmp_path, artifact_content: str, tasks: list[dict]) -> dict:
    model_path = tmp_path / "duration_model.json"
    model_path.write_text(artifact_content, encoding="utf-8")
    monkeypatch.setenv("DURATION_MODEL_PATH", str(model_path))
    reset_model_cache()
    client = TestClient(app)
    try:
        response = client.post("/duration/predict", json={"user_id": 1, "tasks": tasks})
    finally:
        reset_model_cache()
    assert response.status_code == 200
    return response.json()


def test_linear_artifact_serves_with_reliability_and_factors(monkeypatch, tmp_path) -> None:
    payload = predict_with_artifact(monkeypatch, tmp_path, json.dumps(LINEAR_ARTIFACT), [make_task()])

    assert payload["model_name"] == "duration-linear"
    prediction = payload["predictions"][0]
    assert prediction["fallback"] is False
    assert prediction["model_version"] == "0.3.0"
    assert prediction["sample_count"] == 6
    assert prediction["reliability"] in {"high", "medium", "low"}
    assert prediction["lower_bound"] <= prediction["predicted_minutes"] <= prediction["upper_bound"]
    factor_names = {factor["name"] for factor in prediction["factors"]}
    assert "baseline" in factor_names
    assert "estimated_minutes" in factor_names
    assert "category" in factor_names


def test_unseen_category_is_flagged_out_of_distribution(monkeypatch, tmp_path) -> None:
    payload = predict_with_artifact(
        monkeypatch, tmp_path, json.dumps(LINEAR_ARTIFACT), [make_task(category="gardening")]
    )

    prediction = payload["predictions"][0]
    assert prediction["out_of_distribution"] is True
    # Unknown category has no per-category history: sample_count is zero and
    # the reliability label must say the data is insufficient.
    assert prediction["sample_count"] == 0
    assert prediction["reliability"] == "insufficient-data"


def test_extreme_estimate_is_flagged_out_of_distribution(monkeypatch, tmp_path) -> None:
    payload = predict_with_artifact(
        monkeypatch, tmp_path, json.dumps(LINEAR_ARTIFACT), [make_task(estimated_minutes=400)]
    )

    assert payload["predictions"][0]["out_of_distribution"] is True


def test_corrupted_artifact_falls_back_to_heuristic(monkeypatch, tmp_path) -> None:
    payload = predict_with_artifact(monkeypatch, tmp_path, "{ this is not json", [make_task()])

    assert payload["model_name"] == "heuristic-duration"
    prediction = payload["predictions"][0]
    assert prediction["fallback"] is True
    assert prediction["reliability"] == "insufficient-data"
    assert prediction["predicted_minutes"] > 0


def test_incompatible_schema_major_falls_back_to_heuristic(monkeypatch, tmp_path) -> None:
    incompatible = dict(LINEAR_ARTIFACT, schema_version="2.0.0")
    payload = predict_with_artifact(monkeypatch, tmp_path, json.dumps(incompatible), [make_task()])

    assert payload["model_name"] == "heuristic-duration"


def test_linear_artifact_missing_required_keys_falls_back(monkeypatch, tmp_path) -> None:
    broken = {key: value for key, value in LINEAR_ARTIFACT.items() if key != "coefficients"}
    payload = predict_with_artifact(monkeypatch, tmp_path, json.dumps(broken), [make_task()])

    assert payload["model_name"] == "heuristic-duration"


def test_prediction_bounds_are_clamped_to_serving_limits(monkeypatch, tmp_path) -> None:
    heavy = dict(LINEAR_ARTIFACT, category_mae={"study": 400.0}, global_mae=400.0)
    payload = predict_with_artifact(monkeypatch, tmp_path, json.dumps(heavy), [make_task()])

    prediction = payload["predictions"][0]
    assert prediction["lower_bound"] >= 1
    assert prediction["upper_bound"] <= 480


def test_legacy_multiplier_artifact_still_serves_without_new_fields(monkeypatch, tmp_path) -> None:
    legacy = {
        "model_name": "local-duration-regressor",
        "model_version": "0.1.0",
        "source": "local-artifact",
        "global_multiplier": 1.1,
        "category_multipliers": {"qa": 0.95},
        "difficulty_weight": 0.04,
        "priority_weight": 0.015,
        "focus_multiplier": 1.05,
    }
    payload = predict_with_artifact(
        monkeypatch, tmp_path, json.dumps(legacy), [make_task(category="qa", requires_focus=False)]
    )

    assert payload["model_name"] == "local-duration-regressor"
    prediction = payload["predictions"][0]
    # No error profile in the artifact: no invented bounds, honest label.
    assert prediction["lower_bound"] is None
    assert prediction["upper_bound"] is None
    assert prediction["reliability"] == "insufficient-data"
    assert prediction["sample_count"] is None
