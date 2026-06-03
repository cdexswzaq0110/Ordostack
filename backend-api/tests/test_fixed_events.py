from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store


def test_list_fixed_events_returns_seeded_events_for_date() -> None:
    store.reset()
    client = TestClient(app)

    response = client.get(
        "/api/fixed-events",
        params={"user_id": 1, "target_date": "2026-06-03"},
    )

    assert response.status_code == 200
    fixed_events = response.json()
    assert len(fixed_events) == 2
    assert fixed_events[0]["title"] == "Dinner break"


def test_create_fixed_event_returns_created_event() -> None:
    store.reset()
    client = TestClient(app)

    response = client.post(
        "/api/fixed-events",
        json={
            "user_id": 1,
            "title": "Gym",
            "start_time": "2026-06-03T17:30:00",
            "end_time": "2026-06-03T18:15:00",
            "event_type": "exercise",
        },
    )

    assert response.status_code == 201
    fixed_event = response.json()
    assert fixed_event["id"] == 3
    assert fixed_event["title"] == "Gym"


def test_create_fixed_event_rejects_invalid_time_range() -> None:
    store.reset()
    client = TestClient(app)

    response = client.post(
        "/api/fixed-events",
        json={
            "user_id": 1,
            "title": "Invalid event",
            "start_time": "2026-06-03T18:15:00",
            "end_time": "2026-06-03T17:30:00",
            "event_type": "exercise",
        },
    )

    assert response.status_code == 422
