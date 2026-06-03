from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store


def test_list_tasks_returns_seeded_demo_tasks() -> None:
    store.reset()
    client = TestClient(app)

    response = client.get("/api/tasks", params={"user_id": 1})

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 4
    assert tasks[0]["user_id"] == 1


def test_create_task_validates_and_returns_created_task() -> None:
    store.reset()
    client = TestClient(app)

    response = client.post(
        "/api/tasks",
        json={
            "user_id": 1,
            "title": "Draft API QA cases",
            "description": "Prepare tester handoff cases.",
            "category": "qa",
            "estimated_minutes": 45,
            "priority": 4,
            "difficulty": 2,
            "deadline": "2026-06-03T16:00:00",
            "requires_focus": False,
            "is_fixed": False,
            "is_splittable": True,
            "dependency_ids": [],
        },
    )

    assert response.status_code == 201
    task = response.json()
    assert task["id"] == 5
    assert task["title"] == "Draft API QA cases"
    assert task["status"] == "pending"


def test_create_task_rejects_invalid_estimate() -> None:
    store.reset()
    client = TestClient(app)

    response = client.post(
        "/api/tasks",
        json={
            "user_id": 1,
            "title": "Invalid task",
            "category": "qa",
            "estimated_minutes": 0,
            "priority": 4,
            "difficulty": 2,
        },
    )

    assert response.status_code == 422


def test_completed_task_requires_reopen_endpoint_before_pending() -> None:
    store.reset()
    client = TestClient(app)

    conflict_response = client.patch("/api/tasks/3", json={"status": "pending"})
    assert conflict_response.status_code == 409

    reopen_response = client.post("/api/tasks/3/reopen")
    assert reopen_response.status_code == 200
    assert reopen_response.json()["status"] == "pending"


def test_soft_deleted_task_is_hidden_from_list() -> None:
    store.reset()
    client = TestClient(app)

    delete_response = client.delete("/api/tasks/1")
    assert delete_response.status_code == 204

    list_response = client.get("/api/tasks", params={"user_id": 1})
    assert list_response.status_code == 200
    assert all(task["id"] != 1 for task in list_response.json())

