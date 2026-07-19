"""Training-serving parity: the JSON-exported linear model must predict the
same minutes as the fitted scikit-learn pipeline, and the serving endpoint
must agree with the training-side reference implementation."""

import importlib.util
import sys
from pathlib import Path

import pytest

pytest.importorskip("sklearn", reason="scikit-learn is an optional training dependency")

from fastapi.testclient import TestClient

from app.data_contract import encode_features, linear_predict
from app.main import app
from app.predict import reset_model_cache

PARITY_TOLERANCE_MINUTES = 0.01


def load_linear_training_module():
    script_path = Path(__file__).resolve().parents[1] / "training" / "train_linear_model.py"
    spec = importlib.util.spec_from_file_location("train_linear_model_under_test", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load train_linear_model module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PROBE_ROWS = [
    {"category": "study", "estimated_minutes": 90, "priority": 5, "difficulty": 4, "requires_focus": True},
    {"category": "qa", "estimated_minutes": 45, "priority": 2, "difficulty": 2, "requires_focus": False},
    {"category": "never-seen", "estimated_minutes": 60, "priority": 3, "difficulty": 3, "requires_focus": False},
]


def test_exported_json_matches_sklearn_pipeline(tmp_path) -> None:
    training = load_linear_training_module()
    result = training.train_linear_model(artifact_dir=tmp_path, estimator_name="ridge")
    model = result["model"]

    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler

    rows = training.load_training_rows(training.DEFAULT_INPUT_PATH)
    train_rows, _, _ = training.split_rows(rows, training.DEFAULT_SEED)
    categories = model["categories"]
    scaler = StandardScaler().fit(encode_features(train_rows, categories))
    estimator = Ridge(alpha=1.0).fit(
        scaler.transform(encode_features(train_rows, categories)),
        [float(row["actual_minutes"]) for row in train_rows],
    )

    for row in PROBE_ROWS:
        sklearn_prediction = float(estimator.predict(scaler.transform(encode_features([row], categories)))[0])
        sklearn_prediction = min(480.0, max(1.0, sklearn_prediction))
        json_prediction = linear_predict(row, model)
        assert abs(sklearn_prediction - json_prediction) < PARITY_TOLERANCE_MINUTES, row


def test_serving_endpoint_matches_training_reference(tmp_path, monkeypatch) -> None:
    training = load_linear_training_module()
    result = training.train_linear_model(artifact_dir=tmp_path)
    model = result["model"]

    monkeypatch.setenv("DURATION_MODEL_PATH", str(tmp_path / "duration_model.json"))
    reset_model_cache()
    client = TestClient(app)
    try:
        response = client.post(
            "/duration/predict",
            json={
                "user_id": 1,
                "tasks": [
                    {
                        "task_id": index,
                        "title": "parity probe",
                        "actual_minutes": 0,
                        **row,
                    }
                    for index, row in enumerate(PROBE_ROWS, start=1)
                ],
            },
        )
    finally:
        reset_model_cache()

    assert response.status_code == 200
    payload = response.json()
    assert payload["model_name"] == "duration-linear"
    for row, prediction in zip(PROBE_ROWS, payload["predictions"]):
        reference = round(linear_predict(row, model))
        assert prediction["predicted_minutes"] == min(480, max(1, reference)), row


def test_linear_training_is_deterministic(tmp_path) -> None:
    training = load_linear_training_module()

    first = training.train_linear_model(artifact_dir=tmp_path / "first", seed=7)
    second = training.train_linear_model(artifact_dir=tmp_path / "second", seed=7)

    assert first["model"]["coefficients"] == second["model"]["coefficients"]
    assert first["model"]["intercept"] == second["model"]["intercept"]
    assert first["metrics"]["model_mae"] == second["metrics"]["model_mae"]


def test_small_dataset_reports_insufficient_evidence(tmp_path) -> None:
    training = load_linear_training_module()

    result = training.train_linear_model(artifact_dir=tmp_path)

    metrics = result["metrics"]
    assert metrics["evaluation_rows"] < 10
    assert metrics["sufficient_evidence"] is False
    assert "insufficient evidence for automatic promotion" in metrics["evidence_note"]


def test_dataset_validation_blocks_contract_violations(tmp_path) -> None:
    training = load_linear_training_module()
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text(
        "category,estimated_minutes,priority,difficulty,requires_focus,actual_minutes\n"
        "study,60,9,3,true,70\n",
        encoding="utf-8",
    )

    with pytest.raises(training.DatasetValidationError):
        training.train_linear_model(input_path=bad_csv, artifact_dir=tmp_path)
