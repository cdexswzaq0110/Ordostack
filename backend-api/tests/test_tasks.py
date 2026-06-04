from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store
from tests.helpers import auth_headers, register_user


def test_list_tasks_returns_seeded_demo_tasks() -> None:
    store.reset()
    client = TestClient(app)
    headers = auth_headers(client)

    response = client.get("/api/tasks", params={"target_date": "2026-06-03"}, headers=headers)

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3
    assert tasks[0]["user_id"] == 1


def test_create_task_validates_and_returns_created_task() -> None:
    store.reset()
    client = TestClient(app)
    headers = auth_headers(client)

    response = client.post(
        "/api/tasks",
        headers=headers,
        json={
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
    headers = auth_headers(client)

    response = client.post(
        "/api/tasks",
        headers=headers,
        json={
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
    headers = auth_headers(client)

    conflict_response = client.patch("/api/tasks/3", headers=headers, json={"status": "pending"})
    assert conflict_response.status_code == 409

    reopen_response = client.post("/api/tasks/3/reopen", headers=headers)
    assert reopen_response.status_code == 200
    assert reopen_response.json()["status"] == "pending"


def test_soft_deleted_task_is_hidden_from_list() -> None:
    store.reset()
    client = TestClient(app)
    headers = auth_headers(client)

    delete_response = client.delete("/api/tasks/1", headers=headers)
    assert delete_response.status_code == 204

    list_response = client.get("/api/tasks", params={"target_date": "2026-06-03"}, headers=headers)
    assert list_response.status_code == 200
    assert all(task["id"] != 1 for task in list_response.json())


def test_task_update_is_scoped_to_authenticated_user() -> None:
    store.reset()
    client = TestClient(app)
    demo_headers = auth_headers(client)
    _, other_headers = register_user(client, "other@example.com")

    other_update_response = client.patch(
        "/api/tasks/1",
        headers=other_headers,
        json={"title": "Cross user update"},
    )
    demo_task_response = client.get("/api/tasks", headers=demo_headers, params={"target_date": "2026-06-03"})

    assert other_update_response.status_code == 404
    assert any(task["id"] == 1 and task["title"] != "Cross user update" for task in demo_task_response.json())
