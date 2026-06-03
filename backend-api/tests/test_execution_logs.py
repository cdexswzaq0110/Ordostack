from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store


def test_start_and_pause_task_records_actual_minutes() -> None:
    store.reset()
    client = TestClient(app)

    start_response = client.post(
        "/api/tasks/1/execution/start",
        json={"user_id": 1, "occurred_at": "2026-06-03T09:00:00"},
    )
    pause_response = client.post(
        "/api/tasks/1/execution/pause",
        json={"user_id": 1, "occurred_at": "2026-06-03T09:25:00"},
    )
    analytics_response = client.get(
        "/api/analytics/daily",
        params={"user_id": 1, "target_date": "2026-06-03"},
    )

    assert start_response.status_code == 200
    assert start_response.json()["event_type"] == "start"
    assert pause_response.status_code == 200
    assert pause_response.json()["event_type"] == "pause"
    assert analytics_response.status_code == 200

    task_summary = next(
        summary for summary in analytics_response.json()["task_summaries"] if summary["task_id"] == 1
    )
    assert task_summary["actual_minutes"] == 25
    assert task_summary["estimate_delta_minutes"] == -80


def test_complete_task_closes_running_interval_and_updates_status() -> None:
    store.reset()
    client = TestClient(app)

    client.post(
        "/api/tasks/2/execution/start",
        json={"user_id": 1, "occurred_at": "2026-06-03T10:00:00"},
    )
    complete_response = client.post(
        "/api/tasks/2/execution/complete",
        json={"user_id": 1, "occurred_at": "2026-06-03T11:10:00"},
    )
    tasks_response = client.get("/api/tasks", params={"user_id": 1, "target_date": "2026-06-03"})
    analytics_response = client.get(
        "/api/analytics/daily",
        params={"user_id": 1, "target_date": "2026-06-03"},
    )

    assert complete_response.status_code == 200
    assert complete_response.json()["event_type"] == "complete"
    task = next(task for task in tasks_response.json() if task["id"] == 2)
    assert task["status"] == "completed"

    task_summary = next(
        summary for summary in analytics_response.json()["task_summaries"] if summary["task_id"] == 2
    )
    assert task_summary["actual_minutes"] == 70


def test_pause_requires_in_progress_task() -> None:
    store.reset()
    client = TestClient(app)

    response = client.post(
        "/api/tasks/1/execution/pause",
        json={"user_id": 1, "occurred_at": "2026-06-03T09:25:00"},
    )

    assert response.status_code == 409


def test_skip_task_updates_status_and_log() -> None:
    store.reset()
    client = TestClient(app)

    skip_response = client.post(
        "/api/tasks/1/execution/skip",
        json={"user_id": 1, "occurred_at": "2026-06-03T09:25:00"},
    )
    logs_response = client.get(
        "/api/task-execution-logs",
        params={"user_id": 1, "target_date": "2026-06-03", "task_id": 1},
    )

    assert skip_response.status_code == 200
    assert skip_response.json()["event_type"] == "skip"
    assert logs_response.status_code == 200
    assert logs_response.json()[0]["event_type"] == "skip"


def test_default_occurred_at_can_be_listed_with_seeded_logs() -> None:
    store.reset()
    client = TestClient(app)

    start_response = client.post(
        "/api/tasks/1/execution/start",
        json={"user_id": 1},
    )
    logs_response = client.get("/api/task-execution-logs", params={"user_id": 1})

    assert start_response.status_code == 200
    assert logs_response.status_code == 200
    assert any(log["task_id"] == 1 and log["event_type"] == "start" for log in logs_response.json())
