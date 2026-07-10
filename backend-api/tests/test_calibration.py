from datetime import date
from typing import Any

from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory_store import store
from app.services import predictions as prediction_service
from tests.helpers import auth_headers

DEMO_DATE = date(2026, 6, 3)


def seed_paired_logs(ratios: list[tuple[int, int]]) -> None:
    """Seed paired prediction logs as (raw_predicted, actual) tuples."""
    entries = [
        {
            "user_id": 1,
            "task_id": 900 + index,
            "target_date": DEMO_DATE,
            "model_name": "local-duration-regressor",
            "model_version": "0.2.0",
            "predicted_minutes": raw,
            "raw_predicted_minutes": raw,
            "estimated_minutes": raw,
        }
        for index, (raw, _actual) in enumerate(ratios)
    ]
    store.create_prediction_logs(entries)
    for index, (_raw, actual) in enumerate(ratios):
        store.record_prediction_actual(user_id=1, task_id=900 + index, actual_minutes=actual)


class FakeMlResponse:
    status_code = 200

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return {
            "user_id": 1,
            "model_name": "local-duration-regressor",
            "model_version": "0.2.0",
            "predictions": [
                {
                    "task_id": 1,
                    "predicted_minutes": 100,
                    "confidence": 0.8,
                    "model_name": "local-duration-regressor",
                    "reason": "trained local artifact",
                }
            ],
        }


def test_calibration_needs_minimum_samples() -> None:
    store.reset()
    seed_paired_logs([(100, 80), (50, 45)])

    factor, samples = prediction_service.get_user_calibration(user_id=1)

    assert factor is None
    assert samples == 2


def test_calibration_uses_median_ratio() -> None:
    store.reset()
    # Ratios 0.8, 0.9, 0.7 -> median 0.8.
    seed_paired_logs([(100, 80), (50, 45), (60, 42)])

    factor, samples = prediction_service.get_user_calibration(user_id=1)

    assert factor == 0.8
    assert samples == 3


def test_calibration_factor_is_clamped() -> None:
    store.reset()
    # Ratios 4.0, 5.0, 6.0 -> median 5.0, clamped to the ceiling.
    seed_paired_logs([(10, 40), (10, 50), (10, 60)])

    factor, _samples = prediction_service.get_user_calibration(user_id=1)

    assert factor == 2.0


def test_predictions_apply_user_calibration(monkeypatch) -> None:
    store.reset()
    seed_paired_logs([(100, 80), (50, 45), (60, 42)])
    monkeypatch.setattr(prediction_service.httpx, "post", lambda *args, **kwargs: FakeMlResponse())
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    response = client.get("/api/ml/duration-predictions", params={"target_date": "2026-06-03"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["calibration_factor"] == 0.8
    assert payload["calibration_samples"] == 3
    calibrated = next(p for p in payload["predictions"] if p["task_id"] == 1)
    assert calibrated["raw_predicted_minutes"] == 100
    assert calibrated["predicted_minutes"] == 80


def test_calibration_ignores_served_values_to_avoid_feedback() -> None:
    store.reset()
    # Served values differ from raw: the factor must come from raw only.
    store.create_prediction_logs(
        [
            {
                "user_id": 1,
                "task_id": 900 + index,
                "target_date": DEMO_DATE,
                "model_name": "local-duration-regressor",
                "model_version": "0.2.0",
                "predicted_minutes": 999,
                "raw_predicted_minutes": 100,
                "estimated_minutes": 100,
            }
            for index in range(3)
        ]
    )
    for index in range(3):
        store.record_prediction_actual(user_id=1, task_id=900 + index, actual_minutes=90)

    factor, _samples = prediction_service.get_user_calibration(user_id=1)

    assert factor == 0.9


def test_fallback_predictions_are_not_calibrated(monkeypatch) -> None:
    store.reset()
    seed_paired_logs([(100, 80), (50, 45), (60, 42)])

    def unreachable(*args: Any, **kwargs: Any):
        raise prediction_service.httpx.RequestError("ml-service down")

    monkeypatch.setattr(prediction_service.httpx, "post", unreachable)
    client = TestClient(app)
    client.headers.update(auth_headers(client))

    response = client.get("/api/ml/duration-predictions", params={"target_date": "2026-06-03"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["model_name"] == "estimate-fallback"
    assert payload["calibration_factor"] is None
