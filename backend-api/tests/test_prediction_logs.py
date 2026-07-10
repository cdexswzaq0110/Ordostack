from typing import Any

from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store
from app.schemas.predictions import DurationPredictionResponse
from app.services import schedules as schedule_service
from tests.helpers import auth_headers

GENERATE_PAYLOAD = {
    "user_id": 1,
    "target_date": "2026-06-03",
    "planning_mode": "balanced",
    "start_hour": 9,
    "end_hour": 23,
    "buffer_minutes": 10,
    "include_fixed_events": True,
}


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


def fake_predict_for_tasks(user_id, target_date, tasks) -> DurationPredictionResponse:
    return DurationPredictionResponse(
        user_id=user_id,
        target_date=target_date,
        model_name="local-duration-regressor",
        model_version="0.2.0",
        predictions=[
            {
                "task_id": task.id,
                "predicted_minutes": task.estimated_minutes + 10,
                "confidence": 0.6,
                "model_name": "local-duration-regressor",
                "reason": "trained local artifact",
            }
            for task in tasks
        ],
    )


def generate_plan(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(schedule_service.httpx, "post", lambda *args, **kwargs: FakeSchedulerResponse())
    monkeypatch.setattr(schedule_service.prediction_service, "predict_for_tasks", fake_predict_for_tasks)
    response = client.post("/api/schedules/generate", json=GENERATE_PAYLOAD)
    assert response.status_code == 200


def test_generation_logs_served_predictions(monkeypatch) -> None:
    store.reset()
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    generate_plan(client, monkeypatch)

    accuracy = client.get("/api/ml/prediction-accuracy", params={"days": 365}).json()
    assert accuracy["logged_count"] >= 3
    assert accuracy["paired_count"] == 0
    assert accuracy["model_mae"] is None

    logs = store.list_prediction_logs(user_id=1)
    assert all(log["model_version"] == "0.2.0" for log in logs)
    assert all(log["predicted_minutes"] == log["estimated_minutes"] + 10 for log in logs)


def test_completion_pairs_actual_minutes(monkeypatch) -> None:
    store.reset()
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    generate_plan(client, monkeypatch)

    task_id = next(task for task in store.list_tasks(user_id=1) if task["status"] == "pending")["id"]
    start = client.post(
        f"/api/tasks/{task_id}/execution/start",
        json={"occurred_at": "2026-06-03T15:00:00"},
    )
    assert start.status_code == 200
    complete = client.post(
        f"/api/tasks/{task_id}/execution/complete",
        json={"occurred_at": "2026-06-03T15:52:00"},
    )
    assert complete.status_code == 200

    paired = [log for log in store.list_prediction_logs(user_id=1) if log["task_id"] == task_id]
    assert paired and paired[0]["actual_minutes"] == 52
    assert paired[0]["actual_recorded_at"] is not None


def test_prediction_accuracy_reports_model_vs_estimate(monkeypatch) -> None:
    store.reset()
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    generate_plan(client, monkeypatch)

    task = next(task for task in store.list_tasks(user_id=1) if task["status"] == "pending")
    client.post(f"/api/tasks/{task['id']}/execution/start", json={"occurred_at": "2026-06-03T15:00:00"})
    client.post(f"/api/tasks/{task['id']}/execution/complete", json={"occurred_at": "2026-06-03T15:52:00"})

    accuracy = client.get("/api/ml/prediction-accuracy", params={"days": 365}).json()

    assert accuracy["paired_count"] == 1
    estimated = task["estimated_minutes"]
    assert accuracy["estimate_mae"] == abs(estimated - 52)
    assert accuracy["model_mae"] == abs((estimated + 10) - 52)
    assert len(accuracy["daily"]) == 1
    assert accuracy["daily"][0]["target_date"] == "2026-06-03"
    assert accuracy["daily"][0]["paired_count"] == 1


def test_zero_minute_completion_is_not_paired(monkeypatch) -> None:
    store.reset()
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    generate_plan(client, monkeypatch)

    task_id = next(task for task in store.list_tasks(user_id=1) if task["status"] == "pending")["id"]
    # Complete without a start event: no measurable actual minutes.
    complete = client.post(
        f"/api/tasks/{task_id}/execution/complete",
        json={"occurred_at": "2026-06-03T15:52:00"},
    )
    assert complete.status_code == 200

    paired = [log for log in store.list_prediction_logs(user_id=1) if log["actual_minutes"] is not None]
    assert paired == []


def test_prediction_accuracy_requires_auth() -> None:
    store.reset()
    client = TestClient(app)

    response = client.get("/api/ml/prediction-accuracy")

    assert response.status_code in {401, 403}
