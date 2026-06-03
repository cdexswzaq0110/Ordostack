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


def test_update_fixed_event_returns_updated_event() -> None:
    store.reset()
    client = TestClient(app)

    response = client.patch(
        "/api/fixed-events/1",
        json={
            "title": "Dinner with family",
            "start_time": "2026-06-03T18:30:00",
            "end_time": "2026-06-03T19:30:00",
            "event_type": "family",
        },
    )

    assert response.status_code == 200
    fixed_event = response.json()
    assert fixed_event["title"] == "Dinner with family"
    assert fixed_event["event_type"] == "family"
    assert fixed_event["start_time"] == "2026-06-03T18:30:00"
    assert fixed_event["end_time"] == "2026-06-03T19:30:00"
    assert fixed_event["updated_at"] is not None


def test_update_fixed_event_rejects_invalid_existing_range() -> None:
    store.reset()
    client = TestClient(app)

    response = client.patch(
        "/api/fixed-events/2",
        json={
            "start_time": "2026-06-03T20:00:00",
        },
    )

    assert response.status_code == 422


def test_delete_fixed_event_soft_deletes_event() -> None:
    store.reset()
    client = TestClient(app)

    response = client.delete("/api/fixed-events/2")

    assert response.status_code == 204
    list_response = client.get(
        "/api/fixed-events",
        params={"user_id": 1, "target_date": "2026-06-03"},
    )
    titles = [fixed_event["title"] for fixed_event in list_response.json()]
    assert "Dinner break" not in titles
