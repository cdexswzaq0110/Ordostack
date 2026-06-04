from typing import Any

from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store
from app.services import predictions as prediction_service
from tests.helpers import auth_headers


class FakeMlResponse:
    status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return {
            "user_id": 1,
            "model_name": "heuristic-duration",
            "model_version": "0.1.0",
            "predictions": [
                {
                    "task_id": 1,
                    "predicted_minutes": 121,
                    "confidence": 0.45,
                    "model_name": "heuristic-duration",
                    "reason": "feature baseline",
                },
                {
                    "task_id": 2,
                    "predicted_minutes": 84,
                    "confidence": 0.45,
                    "model_name": "heuristic-duration",
                    "reason": "feature baseline",
                },
                {
                    "task_id": 3,
                    "predicted_minutes": 47,
                    "confidence": 0.62,
                    "model_name": "heuristic-duration",
                    "reason": "blended with execution logs",
                },
            ],
        }


def test_duration_predictions_calls_ml_service(monkeypatch) -> None:
    store.reset()
    captured_request: dict[str, Any] = {}

    def fake_post(url: str, json: dict[str, Any], timeout: float) -> FakeMlResponse:
        captured_request["url"] = url
        captured_request["json"] = json
        captured_request["timeout"] = timeout
        return FakeMlResponse()

    monkeypatch.setattr(prediction_service.httpx, "post", fake_post)
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    response = client.get(
        "/api/ml/duration-predictions",
        params={"user_id": 1, "target_date": "2026-06-03"},
    )

    assert response.status_code == 200
    assert captured_request["url"].endswith("/duration/predict")
    assert captured_request["json"]["tasks"][0]["actual_minutes"] == 47
    assert response.json()["model_name"] == "heuristic-duration"
    assert response.json()["predictions"][0]["predicted_minutes"] == 121


def test_duration_predictions_falls_back_when_ml_service_is_unavailable(monkeypatch) -> None:
    store.reset()

    def fake_post(url: str, json: dict[str, Any], timeout: float) -> None:
        raise prediction_service.httpx.ConnectError("offline")

    monkeypatch.setattr(prediction_service.httpx, "post", fake_post)
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    response = client.get(
        "/api/ml/duration-predictions",
        params={"user_id": 1, "target_date": "2026-06-03"},
    )

    assert response.status_code == 200
    assert response.json()["model_name"] == "estimate-fallback"
    assert response.json()["predictions"][0]["confidence"] == 0.2
