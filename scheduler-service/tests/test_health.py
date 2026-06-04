import json
import logging

from fastapi.testclient import TestClient

from app.main import app


REQUEST_ID_HEADER = "X-Request-ID"


def test_health_check_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "scheduler-service",
        "version": "0.1.0",
    }


def test_ready_check_returns_ready() -> None:
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "scheduler-service",
        "version": "0.1.0",
        "checks": {
            "schedule_generator": "ok",
        },
    }


def test_request_id_header_is_added_to_response() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER] != ""


def test_valid_request_id_header_is_preserved() -> None:
    client = TestClient(app)

    response = client.get("/health", headers={REQUEST_ID_HEADER: "scheduler-qa-001"})

    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER] == "scheduler-qa-001"


def test_request_log_contains_request_id(caplog) -> None:
    caplog.set_level(logging.INFO, logger="ordostack.requests")
    client = TestClient(app)

    response = client.get("/health", headers={REQUEST_ID_HEADER: "scheduler-log-001"})

    assert response.status_code == 200
    request_logs = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "ordostack.requests" and record.message.startswith("{")
    ]
    assert any(log["request_id"] == "scheduler-log-001" and log["path"] == "/health" for log in request_logs)
