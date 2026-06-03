from fastapi.testclient import TestClient

from app.main import app


def test_schedule_generate_avoids_fixed_events() -> None:
    client = TestClient(app)

    response = client.post(
        "/schedule/generate",
        json={
            "user_id": 1,
            "target_date": "2026-06-03",
            "planning_mode": "balanced",
            "start_hour": 9,
            "end_hour": 12,
            "buffer_minutes": 10,
            "include_fixed_events": True,
            "tasks": [
                {
                    "id": 1,
                    "title": "Deep work",
                    "category": "study",
                    "estimated_minutes": 60,
                    "priority": 5,
                    "difficulty": 3,
                    "deadline": "2026-06-03T18:00:00",
                    "requires_focus": True,
                    "dependency_ids": [],
                    "status": "pending",
                },
                {
                    "id": 2,
                    "title": "Review",
                    "category": "admin",
                    "estimated_minutes": 45,
                    "priority": 4,
                    "difficulty": 2,
                    "deadline": "2026-06-03T17:00:00",
                    "requires_focus": False,
                    "dependency_ids": [],
                    "status": "pending",
                },
            ],
            "fixed_events": [
                {
                    "id": 10,
                    "title": "Class",
                    "start_time": "2026-06-03T10:00:00",
                    "end_time": "2026-06-03T11:00:00",
                    "event_type": "class",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    task_items = [item for item in payload["items"] if item["type"] == "task"]
    assert task_items
    assert all(not ("2026-06-03T10:" <= item["start_time"] < "2026-06-03T11:") for item in task_items)
    assert payload["algorithm_summary"]["scheduled_task_count"] >= 1
