from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store


def test_demo_reset_restores_seed_data() -> None:
    store.reset()
    client = TestClient(app)

    create_response = client.post(
        "/api/tasks",
        json={
            "user_id": 1,
            "title": "Temporary demo pollution",
            "description": "",
            "category": "qa",
            "estimated_minutes": 15,
            "priority": 2,
            "difficulty": 1,
            "deadline": "2026-06-03T12:00:00",
            "requires_focus": False,
            "is_fixed": False,
            "is_splittable": False,
            "dependency_ids": [],
        },
    )
    assert create_response.status_code == 201

    reset_response = client.post("/api/demo/reset", params={"user_id": 1})

    assert reset_response.status_code == 200
    reset_payload = reset_response.json()
    assert reset_payload["status"] == "ok"
    assert reset_payload["seeded_tasks"] >= 1
    assert reset_payload["seeded_fixed_events"] >= 1

    task_response = client.get(
        "/api/tasks",
        params={"user_id": 1, "target_date": "2026-06-03"},
    )
    titles = [task["title"] for task in task_response.json()]
    assert "Temporary demo pollution" not in titles
    assert "ML course chapter notes" in titles
