from fastapi.testclient import TestClient

from app.main import app


def test_api_health_check_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "backend-api",
        "version": "0.1.0",
    }

