from typing import Any

from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store
from app.schemas.predictions import DurationPredictionResponse
from app.services import schedules as schedule_service


class FakeSchedulerResponse:
    status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return {
            "schedule_date": "2026-06-03",
            "planning_mode": "balanced",
            "items": [],
            "algorithm_summary": {
                "available_minutes": 600,
                "selected_task_count": 1,
                "scheduled_task_count": 1,
                "skipped_task_count": 0,
                "total_task_minutes": 60,
                "applied_algorithms": ["priority-score"],
                "warnings": [],
            },
        }


def test_generate_schedule_forwards_tasks_and_fixed_events(monkeypatch) -> None:
    store.reset()
    captured_request: dict[str, Any] = {}

    def fake_post(url: str, json: dict[str, Any], timeout: float) -> FakeSchedulerResponse:
        captured_request["url"] = url
        captured_request["json"] = json
        captured_request["timeout"] = timeout
        return FakeSchedulerResponse()

    def fake_predict_for_tasks(user_id, target_date, tasks) -> DurationPredictionResponse:
        return DurationPredictionResponse(
            user_id=user_id,
            target_date=target_date,
            model_name="heuristic-duration",
            model_version="0.1.0",
            predictions=[
                {
                    "task_id": task.id,
                    "predicted_minutes": task.estimated_minutes + 7,
                    "confidence": 0.45,
                    "model_name": "heuristic-duration",
                    "reason": "feature baseline",
                }
                for task in tasks
            ],
        )

    monkeypatch.setattr(schedule_service.httpx, "post", fake_post)
    monkeypatch.setattr(schedule_service.prediction_service, "predict_for_tasks", fake_predict_for_tasks)
    client = TestClient(app)

    response = client.post(
        "/api/schedules/generate",
        json={
            "user_id": 1,
            "target_date": "2026-06-03",
            "planning_mode": "balanced",
            "start_hour": 9,
            "end_hour": 23,
            "buffer_minutes": 10,
            "include_fixed_events": True,
        },
    )

    assert response.status_code == 200
    assert captured_request["url"].endswith("/schedule/generate")
    assert captured_request["json"]["target_date"] == "2026-06-03"
    assert len(captured_request["json"]["tasks"]) >= 1
    assert captured_request["json"]["tasks"][0]["predicted_minutes"] is not None
    assert len(captured_request["json"]["fixed_events"]) >= 1
    assert response.json()["algorithm_summary"]["scheduled_task_count"] == 1

    latest_response = client.get(
        "/api/schedules/latest",
        params={"user_id": 1, "target_date": "2026-06-03"},
    )

    assert latest_response.status_code == 200
    assert latest_response.json()["algorithm_summary"]["scheduled_task_count"] == 1


def test_latest_schedule_returns_404_when_missing() -> None:
    store.reset()
    client = TestClient(app)

    response = client.get(
        "/api/schedules/latest",
        params={"user_id": 1, "target_date": "2026-06-03"},
    )

    assert response.status_code == 404
