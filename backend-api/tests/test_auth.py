from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import DEMO_AUTH_EMAIL, DEMO_AUTH_PASSWORD, store
from app.services import auth as auth_service


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
    assert token_payload["expires_at"]
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


def test_register_rejects_weak_password() -> None:
    store.reset()
    client = TestClient(app)

    response = client.post(
        "/api/auth/register",
        json={
            "email": "weak@example.com",
            "display_name": "Weak Password",
            "password": "weakpass",
        },
    )

    assert response.status_code == 422
    assert "Password must include" in response.json()["detail"]


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


def test_login_rate_limit_locks_repeated_failures(monkeypatch) -> None:
    store.reset()
    auth_service.clear_login_rate_limit()
    monkeypatch.setenv("AUTH_LOGIN_MAX_FAILURES", "2")
    monkeypatch.setenv("AUTH_LOGIN_WINDOW_SECONDS", "60")
    monkeypatch.setenv("AUTH_LOGIN_LOCKOUT_SECONDS", "60")
    client = TestClient(app)

    payload = {
        "email": DEMO_AUTH_EMAIL,
        "password": "wrong-password",
    }

    assert client.post("/api/auth/login", json=payload).status_code == 401
    locked_response = client.post("/api/auth/login", json=payload)

    assert locked_response.status_code == 429
    assert locked_response.json()["detail"]["message"] == "Too many failed login attempts"
    auth_service.clear_login_rate_limit()


def test_me_requires_bearer_token() -> None:
    store.reset()
    client = TestClient(app)

    response = client.get("/api/auth/me")

    # Missing credentials: 401 per RFC 7235 (FastAPI >= 0.116 corrected this from 403).
    assert response.status_code == 401


def test_password_hashing_uses_current_iterations_and_verifies_legacy() -> None:
    from app.security import PBKDF2_ITERATIONS, hash_password, verify_password
    import hashlib

    fresh_hash = hash_password("Sample-Passw0rd")
    assert f"pbkdf2_sha256${PBKDF2_ITERATIONS}$" in fresh_hash
    assert verify_password("Sample-Passw0rd", fresh_hash)
    assert not verify_password("wrong-password", fresh_hash)

    # Hashes minted before the iteration bump keep verifying.
    legacy_digest = hashlib.pbkdf2_hmac("sha256", b"Sample-Passw0rd", b"legacysalt", 120_000).hex()
    legacy_hash = f"pbkdf2_sha256$120000$legacysalt${legacy_digest}"
    assert verify_password("Sample-Passw0rd", legacy_hash)
