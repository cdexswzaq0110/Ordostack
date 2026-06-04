from typing import Any

from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store
from app.schemas.predictions import DurationPredictionResponse
from app.services import schedules as schedule_service
from tests.helpers import auth_headers, register_user


class FakeSchedulerResponse:
    status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return {
            "schedule_date": "2026-06-03",
            "planning_mode": "balanced",
            "items": [
                {
                    "type": "task",
                    "task_id": 1,
                    "fixed_event_id": None,
                    "title": "ML course chapter notes",
                    "start_time": "2026-06-03T09:00:00",
                    "end_time": "2026-06-03T10:45:00",
                    "planned_minutes": 105,
                    "order_index": 0,
                    "category": "study",
                    "requires_focus": True,
                    "score": 80,
                }
            ],
            "algorithm_summary": {
                "available_minutes": 600,
                "selected_task_count": 1,
                "scheduled_task_count": 1,
                "skipped_task_count": 0,
                "total_task_minutes": 105,
                "applied_algorithms": ["priority-score"],
                "warnings": [],
            },
        }


def test_planner_data_is_scoped_to_authenticated_user(monkeypatch) -> None:
    store.reset()
    client = TestClient(app)
    demo_headers = auth_headers(client)
    _, other_headers = register_user(client, "isolated@example.com")

    def fake_post(url: str, json: dict[str, Any], timeout: float) -> FakeSchedulerResponse:
        return FakeSchedulerResponse()

    def fake_predict_for_tasks(user_id, target_date, tasks) -> DurationPredictionResponse:
        return DurationPredictionResponse(
            user_id=user_id,
            target_date=target_date,
            model_name="heuristic-duration",
            model_version="0.1.0",
            predictions=[],
        )

    monkeypatch.setattr(schedule_service.httpx, "post", fake_post)
    monkeypatch.setattr(schedule_service.prediction_service, "predict_for_tasks", fake_predict_for_tasks)

    other_tasks = client.get(
        "/api/tasks",
        headers=other_headers,
        params={"target_date": "2026-06-03"},
    )
    other_fixed_events = client.get(
        "/api/fixed-events",
        headers=other_headers,
        params={"target_date": "2026-06-03"},
    )
    cross_user_execution = client.post(
        "/api/tasks/1/execution/start",
        headers=other_headers,
        json={"occurred_at": "2026-06-03T09:00:00"},
    )

    generate_response = client.post(
        "/api/schedules/generate",
        headers=demo_headers,
        json={
            "target_date": "2026-06-03",
            "planning_mode": "balanced",
            "start_hour": 9,
            "end_hour": 23,
            "buffer_minutes": 10,
            "include_fixed_events": True,
        },
    )
    demo_history = client.get(
        "/api/schedules/history",
        headers=demo_headers,
        params={"target_date": "2026-06-03", "limit": 5},
    )
    schedule_run_id = demo_history.json()[0]["id"]
    other_history = client.get(
        "/api/schedules/history",
        headers=other_headers,
        params={"target_date": "2026-06-03", "limit": 5},
    )
    cross_user_export = client.get(
        f"/api/schedules/history/{schedule_run_id}/export",
        headers=other_headers,
        params={"format": "markdown"},
    )

    assert other_tasks.status_code == 200
    assert other_tasks.json() == []
    assert other_fixed_events.status_code == 200
    assert other_fixed_events.json() == []
    assert cross_user_execution.status_code == 404
    assert generate_response.status_code == 200
    assert other_history.status_code == 200
    assert other_history.json() == []
    assert cross_user_export.status_code == 404
