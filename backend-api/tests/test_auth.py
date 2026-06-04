from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import DEMO_AUTH_EMAIL, DEMO_AUTH_PASSWORD, store


def test_register_user_returns_token_and_me() -> None:
    store.reset()
    client = TestClient(app)

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "qa@example.com",
            "display_name": "QA Tester",
            "password": "strong-password",
        },
    )

    assert register_response.status_code == 201
    token_payload = register_response.json()
    assert token_payload["token_type"] == "bearer"
    assert token_payload["access_token"]
    assert token_payload["user"]["email"] == "qa@example.com"

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token_payload['access_token']}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "qa@example.com"


def test_demo_user_can_login() -> None:
    store.reset()
    client = TestClient(app)

    response = client.post(
        "/api/auth/login",
        json={
            "email": DEMO_AUTH_EMAIL,
            "password": DEMO_AUTH_PASSWORD,
        },
    )

    assert response.status_code == 200
    assert response.json()["user"]["id"] == 1


def test_register_rejects_duplicate_email() -> None:
    store.reset()
    client = TestClient(app)

    payload = {
        "email": "duplicate@example.com",
        "display_name": "Duplicate",
        "password": "strong-password",
    }

    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_login_rejects_wrong_password() -> None:
    store.reset()
    client = TestClient(app)

    response = client.post(
        "/api/auth/login",
        json={
            "email": DEMO_AUTH_EMAIL,
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_me_requires_bearer_token() -> None:
    store.reset()
    client = TestClient(app)

    response = client.get("/api/auth/me")

    assert response.status_code == 403
