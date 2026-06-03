import json

from fastapi.testclient import TestClient

from app.main import app
from app.predict import reset_model_cache


def test_duration_prediction_returns_fallback_metadata_and_predictions(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DURATION_MODEL_PATH", str(tmp_path / "missing_model.json"))
    reset_model_cache()
    client = TestClient(app)

    try:
        response = client.post(
            "/duration/predict",
            json={
                "user_id": 1,
                "tasks": [
                    {
                        "task_id": 1,
                        "title": "ML course chapter notes",
                        "category": "study",
                        "estimated_minutes": 100,
                        "priority": 5,
                        "difficulty": 4,
                        "requires_focus": True,
                        "actual_minutes": 0,
                    }
                ],
            },
        )
    finally:
        reset_model_cache()

    assert response.status_code == 200
    payload = response.json()
    assert payload["model_name"] == "heuristic-duration"
    assert payload["model_version"] == "0.1.0"
    assert payload["predictions"][0]["task_id"] == 1
    assert payload["predictions"][0]["predicted_minutes"] > 100


def test_duration_prediction_uses_local_artifact_when_available(monkeypatch, tmp_path) -> None:
    model_path = tmp_path / "duration_model.json"
    model_path.write_text(
        json.dumps(
            {
                "model_name": "local-duration-regressor",
                "model_version": "0.1.0",
                "source": "local-artifact",
                "global_multiplier": 1.1,
                "category_multipliers": {"qa": 0.95},
                "difficulty_weight": 0.04,
                "priority_weight": 0.015,
                "focus_multiplier": 1.05,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("DURATION_MODEL_PATH", str(model_path))
    reset_model_cache()
    client = TestClient(app)

    try:
        response = client.post(
            "/duration/predict",
            json={
                "user_id": 1,
                "tasks": [
                    {
                        "task_id": 2,
                        "title": "Short review",
                        "category": "qa",
                        "estimated_minutes": 60,
                        "priority": 3,
                        "difficulty": 3,
                        "requires_focus": False,
                        "actual_minutes": 30,
                    }
                ],
            },
        )
        info_response = client.get("/model/info")
    finally:
        reset_model_cache()

    assert response.status_code == 200
    assert response.json()["model_name"] == "local-duration-regressor"
    prediction = response.json()["predictions"][0]
    assert prediction["confidence"] == 0.74
    assert prediction["reason"] == "trained local artifact blended with execution logs"
    assert info_response.status_code == 200
    assert info_response.json()["source"] == "local-artifact"
