from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store
from tests.helpers import auth_headers, register_user


def test_list_fixed_events_returns_seeded_events_for_date() -> None:
    store.reset()
    client = TestClient(app)
    headers = auth_headers(client)

    response = client.get(
        "/api/fixed-events",
        headers=headers,
        params={"target_date": "2026-06-03"},
    )

    assert response.status_code == 200
    fixed_events = response.json()
    assert len(fixed_events) == 2
    assert fixed_events[0]["title"] == "Dinner break"


def test_create_fixed_event_returns_created_event() -> None:
    store.reset()
    client = TestClient(app)
    headers = auth_headers(client)

    response = client.post(
        "/api/fixed-events",
        headers=headers,
        json={
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
    headers = auth_headers(client)

    response = client.post(
        "/api/fixed-events",
        headers=headers,
        json={
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
    headers = auth_headers(client)

    response = client.patch(
        "/api/fixed-events/1",
        headers=headers,
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
    headers = auth_headers(client)

    response = client.patch(
        "/api/fixed-events/2",
        headers=headers,
        json={
            "start_time": "2026-06-03T20:00:00",
        },
    )

    assert response.status_code == 422


def test_delete_fixed_event_soft_deletes_event() -> None:
    store.reset()
    client = TestClient(app)
    headers = auth_headers(client)

    response = client.delete("/api/fixed-events/2", headers=headers)

    assert response.status_code == 204
    list_response = client.get(
        "/api/fixed-events",
        headers=headers,
        params={"target_date": "2026-06-03"},
    )
    titles = [fixed_event["title"] for fixed_event in list_response.json()]
    assert "Dinner break" not in titles


def test_fixed_event_update_is_scoped_to_authenticated_user() -> None:
    store.reset()
    client = TestClient(app)
    demo_headers = auth_headers(client)
    _, other_headers = register_user(client, "fixed-other@example.com")

    other_response = client.patch(
        "/api/fixed-events/1",
        headers=other_headers,
        json={"title": "Cross user event"},
    )
    demo_response = client.get(
        "/api/fixed-events",
        headers=demo_headers,
        params={"target_date": "2026-06-03"},
    )

    assert other_response.status_code == 404
    assert any(event["id"] == 1 and event["title"] != "Cross user event" for event in demo_response.json())
