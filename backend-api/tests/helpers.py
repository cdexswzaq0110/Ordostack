from fastapi.testclient import TestClient

from app.repositories.memory_store import DEMO_AUTH_EMAIL, DEMO_AUTH_PASSWORD


def auth_headers(client: TestClient, email: str = DEMO_AUTH_EMAIL, password: str = DEMO_AUTH_PASSWORD) -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def register_user(
    client: TestClient,
    email: str,
    password: str = "strong-password",
    display_name: str = "Test User",
) -> tuple[int, dict[str, str]]:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "display_name": display_name},
    )
    assert response.status_code == 201
    payload = response.json()
    return payload["user"]["id"], {"Authorization": f"Bearer {payload['access_token']}"}
