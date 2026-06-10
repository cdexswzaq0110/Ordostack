from typing import Any
import base64

from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store
from app.schemas.predictions import DurationPredictionResponse
from app.services import schedules as schedule_service
from tests.helpers import auth_headers


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


class PayloadSchedulerResponse:
    status_code = 200

    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self.payload


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
    client.headers.update(auth_headers(client))

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


def test_schedule_history_diff_compares_two_runs(monkeypatch) -> None:
    store.reset()
    schedule_payloads = [
        {
            "schedule_date": "2026-06-03",
            "planning_mode": "balanced",
            "items": [
                {
                    "type": "task",
                    "task_id": 1,
                    "fixed_event_id": None,
                    "title": "ML course chapter notes",
                    "start_time": "2026-06-03T09:00:00",
                    "end_time": "2026-06-03T10:00:00",
                    "planned_minutes": 60,
                    "order_index": 0,
                    "category": "study",
                    "requires_focus": True,
                    "score": 70,
                },
                {
                    "type": "task",
                    "task_id": 2,
                    "fixed_event_id": None,
                    "title": "Backend API review",
                    "start_time": "2026-06-03T10:10:00",
                    "end_time": "2026-06-03T10:40:00",
                    "planned_minutes": 30,
                    "order_index": 1,
                    "category": "backend",
                    "requires_focus": False,
                    "score": 50,
                },
            ],
            "algorithm_summary": {
                "available_minutes": 600,
                "selected_task_count": 2,
                "scheduled_task_count": 2,
                "skipped_task_count": 0,
                "total_task_minutes": 90,
                "applied_algorithms": ["priority-score"],
                "warnings": [],
            },
        },
        {
            "schedule_date": "2026-06-03",
            "planning_mode": "balanced",
            "items": [
                {
                    "type": "task",
                    "task_id": 1,
                    "fixed_event_id": None,
                    "title": "ML course chapter notes",
                    "start_time": "2026-06-03T09:30:00",
                    "end_time": "2026-06-03T10:45:00",
                    "planned_minutes": 75,
                    "order_index": 0,
                    "category": "study",
                    "requires_focus": True,
                    "score": 70,
                },
                {
                    "type": "task",
                    "task_id": 3,
                    "fixed_event_id": None,
                    "title": "Record task execution samples",
                    "start_time": "2026-06-03T11:00:00",
                    "end_time": "2026-06-03T11:30:00",
                    "planned_minutes": 30,
                    "order_index": 1,
                    "category": "analytics",
                    "requires_focus": False,
                    "score": 45,
                },
            ],
            "algorithm_summary": {
                "available_minutes": 600,
                "selected_task_count": 2,
                "scheduled_task_count": 2,
                "skipped_task_count": 0,
                "total_task_minutes": 105,
                "applied_algorithms": ["priority-score"],
                "warnings": [],
            },
        },
    ]

    def fake_post(url: str, json: dict[str, Any], timeout: float) -> PayloadSchedulerResponse:
        return PayloadSchedulerResponse(schedule_payloads.pop(0))

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
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    for _ in range(2):
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

    history_response = client.get(
        "/api/schedules/history",
        params={"user_id": 1, "target_date": "2026-06-03", "limit": 5},
    )
    newest_run = history_response.json()[0]
    older_run = history_response.json()[1]

    diff_response = client.get(
        f"/api/schedules/history/{newest_run['id']}/diff",
        params={"user_id": 1, "against_run_id": older_run["id"]},
    )

    assert diff_response.status_code == 200
    diff = diff_response.json()
    assert diff["base_run_id"] == older_run["id"]
    assert diff["compare_run_id"] == newest_run["id"]
    assert diff["added_count"] == 1
    assert diff["removed_count"] == 1
    assert diff["changed_count"] == 1
    assert diff["total_delta_minutes"] == 15


def test_latest_schedule_returns_404_when_missing() -> None:
    store.reset()
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    response = client.get(
        "/api/schedules/latest",
        params={"user_id": 1, "target_date": "2026-06-03"},
    )

    assert response.status_code == 404


def test_schedule_history_returns_recent_generated_runs(monkeypatch) -> None:
    store.reset()

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
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    for _ in range(2):
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

    history_response = client.get(
        "/api/schedules/history",
        params={"user_id": 1, "target_date": "2026-06-03", "limit": 5},
    )

    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 2
    assert history[0]["id"] > history[1]["id"]
    assert history[0]["title"].startswith("Balanced plan")
    assert history[0]["scheduled_task_count"] == 1
    assert history[0]["schedule"]["schedule_date"] == "2026-06-03"


def test_schedule_history_export_returns_markdown_and_csv(monkeypatch) -> None:
    store.reset()

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
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    generate_response = client.post(
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
    assert generate_response.status_code == 200

    history_response = client.get(
        "/api/schedules/history",
        params={"user_id": 1, "target_date": "2026-06-03", "limit": 5},
    )
    schedule_run_id = history_response.json()[0]["id"]

    markdown_response = client.get(
        f"/api/schedules/history/{schedule_run_id}/export",
        params={"user_id": 1, "format": "markdown"},
    )
    csv_response = client.get(
        f"/api/schedules/history/{schedule_run_id}/export",
        params={"user_id": 1, "format": "csv"},
    )
    pdf_response = client.get(
        f"/api/schedules/history/{schedule_run_id}/export",
        params={"user_id": 1, "format": "pdf"},
    )

    assert markdown_response.status_code == 200
    assert markdown_response.json()["filename"].endswith(".md")
    assert markdown_response.json()["content"].startswith("# Balanced plan")
    assert "| Start | End | Type | Title | Minutes |" in markdown_response.json()["content"]

    assert csv_response.status_code == 200
    assert csv_response.json()["filename"].endswith(".csv")
    assert csv_response.json()["content"].startswith("start_time,end_time,type,title,planned_minutes,category")

    assert pdf_response.status_code == 200
    assert pdf_response.json()["filename"].endswith(".pdf")
    assert pdf_response.json()["encoding"] == "base64"
    assert base64.b64decode(pdf_response.json()["content"]).startswith(b"%PDF-1.4")


def test_schedule_item_lock_and_manual_adjustment_preserved_on_next_generation(monkeypatch) -> None:
    store.reset()
    captured_requests: list[dict[str, Any]] = []
    schedule_payload = {
        "schedule_date": "2026-06-03",
        "planning_mode": "balanced",
        "items": [
            {
                "type": "task",
                "task_id": 1,
                "fixed_event_id": None,
                "title": "ML course chapter notes",
                "start_time": "2026-06-03T09:00:00",
                "end_time": "2026-06-03T10:00:00",
                "planned_minutes": 60,
                "order_index": 0,
                "category": "study",
                "requires_focus": True,
                "score": 70,
                "locked": False,
                "manual_override": False,
            },
            {
                "type": "fixed_event",
                "task_id": None,
                "fixed_event_id": 2,
                "title": "Dinner break",
                "start_time": "2026-06-03T18:20:00",
                "end_time": "2026-06-03T19:00:00",
                "planned_minutes": 40,
                "order_index": 1,
                "category": "rest",
                "requires_focus": False,
                "score": None,
            },
        ],
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

    def fake_post(url: str, json: dict[str, Any], timeout: float) -> PayloadSchedulerResponse:
        captured_requests.append(json)
        return PayloadSchedulerResponse(schedule_payload)

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
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    generate_response = client.post(
        "/api/schedules/generate",
        json={
            "target_date": "2026-06-03",
            "planning_mode": "balanced",
            "start_hour": 9,
            "end_hour": 23,
            "buffer_minutes": 10,
            "include_fixed_events": True,
        },
    )
    assert generate_response.status_code == 200

    history_response = client.get("/api/schedules/history", params={"target_date": "2026-06-03"})
    schedule_run_id = history_response.json()[0]["id"]

    lock_response = client.patch(
        f"/api/schedules/history/{schedule_run_id}/items/task:1/lock",
        json={"locked": True},
    )
    assert lock_response.status_code == 200
    assert lock_response.json()["schedule"]["items"][0]["locked"] is True

    conflict_response = client.patch(
        f"/api/schedules/history/{schedule_run_id}/items/task:1/time",
        json={"start_time": "2026-06-03T18:30:00", "end_time": "2026-06-03T19:00:00"},
    )
    assert conflict_response.status_code == 409

    adjust_response = client.patch(
        f"/api/schedules/history/{schedule_run_id}/items/task:1/time",
        json={"start_time": "2026-06-03T11:00:00", "end_time": "2026-06-03T12:15:00"},
    )
    assert adjust_response.status_code == 200
    adjusted_item = adjust_response.json()["schedule"]["items"][0]
    assert adjusted_item["locked"] is True
    assert adjusted_item["manual_override"] is True
    assert adjusted_item["planned_minutes"] == 75

    second_generate_response = client.post(
        "/api/schedules/generate",
        json={
            "target_date": "2026-06-03",
            "planning_mode": "balanced",
            "start_hour": 9,
            "end_hour": 23,
            "buffer_minutes": 10,
            "include_fixed_events": True,
        },
    )
    assert second_generate_response.status_code == 200
    assert captured_requests[-1]["locked_items"][0]["task_id"] == 1
    assert captured_requests[-1]["locked_items"][0]["manual_override"] is True


def test_schedule_history_title_update_and_soft_delete(monkeypatch) -> None:
    store.reset()

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
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    for _ in range(2):
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

    history_response = client.get(
        "/api/schedules/history",
        params={"user_id": 1, "target_date": "2026-06-03", "limit": 5},
    )
    newest_run = history_response.json()[0]
    older_run = history_response.json()[1]

    rename_response = client.patch(
        f"/api/schedules/history/{older_run['id']}",
        params={"user_id": 1},
        json={"title": "Client review plan"},
    )

    assert rename_response.status_code == 200
    assert rename_response.json()["title"] == "Client review plan"

    delete_response = client.delete(
        f"/api/schedules/history/{newest_run['id']}",
        params={"user_id": 1},
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True

    next_history_response = client.get(
        "/api/schedules/history",
        params={"user_id": 1, "target_date": "2026-06-03", "limit": 5},
    )
    next_history = next_history_response.json()

    assert len(next_history) == 1
    assert next_history[0]["id"] == older_run["id"]
    assert next_history[0]["title"] == "Client review plan"

    latest_response = client.get(
        "/api/schedules/latest",
        params={"user_id": 1, "target_date": "2026-06-03"},
    )

    assert latest_response.status_code == 200
