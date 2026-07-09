import json

from fastapi.testclient import TestClient

from app.main import app
from app.predict import reset_model_cache


def write_model(path, version: str) -> None:
    path.write_text(
        json.dumps(
            {
                "model_name": "local-duration-regressor",
                "model_version": version,
                "source": "local-artifact",
                "global_multiplier": 1.1,
                "category_multipliers": {"study": 1.2},
                "difficulty_weight": 0.04,
                "priority_weight": 0.015,
                "focus_multiplier": 1.05,
            }
        ),
        encoding="utf-8",
    )


def test_model_reload_serves_newly_promoted_artifact_without_restart(monkeypatch, tmp_path) -> None:
    model_path = tmp_path / "duration_model.json"
    write_model(model_path, version="0.2.0")
    monkeypatch.setenv("DURATION_MODEL_PATH", str(model_path))
    reset_model_cache()
    client = TestClient(app)

    try:
        first_info = client.get("/model/info")
        write_model(model_path, version="0.3.0")
        stale_info = client.get("/model/info")
        reload_response = client.post("/model/reload")
        fresh_info = client.get("/model/info")
    finally:
        reset_model_cache()

    assert first_info.json()["model_version"] == "0.2.0"
    assert stale_info.json()["model_version"] == "0.2.0"
    assert reload_response.status_code == 200
    assert reload_response.json()["status"] == "reloaded"
    assert reload_response.json()["model_version"] == "0.3.0"
    assert fresh_info.json()["model_version"] == "0.3.0"
