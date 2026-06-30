import json
import logging

from fastapi.testclient import TestClient

from app.main import app


REQUEST_ID_HEADER = "X-Request-ID"


def test_api_health_check_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "backend-api",
        "version": "0.1.0",
    }


def test_api_ready_check_returns_ready() -> None:
    client = TestClient(app)

    response = client.get("/api/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "backend-api",
        "version": "0.1.0",
        "checks": {
            "configuration": "ok",
        },
    }


def test_request_id_header_is_added_to_response() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER] != ""


def test_valid_request_id_header_is_preserved() -> None:
    client = TestClient(app)

    response = client.get("/api/health", headers={REQUEST_ID_HEADER: "qa-run-001"})

    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER] == "qa-run-001"


def test_request_log_contains_request_id(caplog) -> None:
    caplog.set_level(logging.INFO, logger="ordostack.requests")
    client = TestClient(app)

    response = client.get("/api/health", headers={REQUEST_ID_HEADER: "qa-log-001"})

    assert response.status_code == 200
    request_logs = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "ordostack.requests" and record.message.startswith("{")
    ]
    assert any(log["request_id"] == "qa-log-001" and log["path"] == "/api/health" for log in request_logs)
