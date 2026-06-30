import importlib.util
from pathlib import Path


def load_training_module():
    script_path = Path(__file__).resolve().parents[1] / "training" / "train_duration_model.py"
    spec = importlib.util.spec_from_file_location("train_duration_model", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load training module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_train_duration_model_writes_artifacts(tmp_path) -> None:
    training_module = load_training_module()

    result = training_module.train_duration_model(artifact_dir=tmp_path)

    model_path = tmp_path / "duration_model.json"
    metrics_path = tmp_path / "duration_metrics.json"
    assert model_path.exists()
    assert metrics_path.exists()
    assert result["model"]["model_name"] == "local-duration-regressor"
    assert result["metrics"]["training_rows"] > 0
