from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store
from tests.helpers import auth_headers, register_user


def test_schedule_template_crud_for_authenticated_user() -> None:
    store.reset()
    client = TestClient(app)
    headers = auth_headers(client)

    create_response = client.post(
        "/api/schedule-templates",
        headers=headers,
        json={
            "name": "Deep work morning",
            "planning_mode": "focus-heavy",
            "start_hour": 8,
            "end_hour": 13,
            "buffer_minutes": 15,
            "include_fixed_events": True,
        },
    )
    assert create_response.status_code == 201
    template = create_response.json()
    assert template["id"] == 1
    assert template["name"] == "Deep work morning"

    update_response = client.patch(
        f"/api/schedule-templates/{template['id']}",
        headers=headers,
        json={"name": "Client demo morning", "buffer_minutes": 20},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Client demo morning"
    assert update_response.json()["buffer_minutes"] == 20

    list_response = client.get("/api/schedule-templates", headers=headers)
    assert list_response.status_code == 200
    assert [item["name"] for item in list_response.json()] == ["Client demo morning"]

    delete_response = client.delete(f"/api/schedule-templates/{template['id']}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True

    next_list_response = client.get("/api/schedule-templates", headers=headers)
    assert next_list_response.json() == []


def test_schedule_template_update_is_scoped_to_authenticated_user() -> None:
    store.reset()
    client = TestClient(app)
    demo_headers = auth_headers(client)
    _, other_headers = register_user(client, "templates-other@example.com")

    create_response = client.post(
        "/api/schedule-templates",
        headers=demo_headers,
        json={"name": "Demo template", "start_hour": 9, "end_hour": 17},
    )
    template_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/schedule-templates/{template_id}",
        headers=other_headers,
        json={"name": "Cross user edit"},
    )

    assert update_response.status_code == 404
