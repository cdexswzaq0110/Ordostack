import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest


def load_clearml_utils():
    script_path = Path(__file__).resolve().parents[1] / "training" / "clearml_utils.py"
    spec = importlib.util.spec_from_file_location("clearml_utils_under_test", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load clearml_utils module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_fake_clearml(record: dict, fail_init: bool = False):
    fake = types.ModuleType("clearml")

    class FakeLogger:
        def report_scalar(self, title, series, value, iteration):
            record.setdefault("scalars", []).append((title, series, value, iteration))

    class FakeTask:
        id = "fake-task-id"

        class TaskTypes:
            training = "training"
            custom = "custom"

        @classmethod
        def set_offline(cls, offline_mode):
            record["offline"] = offline_mode

        @classmethod
        def init(cls, **kwargs):
            if fail_init:
                raise RuntimeError("no clearml server configured")
            record["init_kwargs"] = kwargs
            return cls()

        def connect(self, params, name=None):
            record.setdefault("connected", []).append((name, params))

        def get_logger(self):
            return FakeLogger()

        def upload_artifact(self, name, artifact_object):
            record.setdefault("artifacts", []).append((name, Path(artifact_object).name))

        def add_tags(self, tags):
            record.setdefault("tags", []).extend(tags)

        def close(self):
            record["closed"] = True

    class FakeOutputModel:
        fail_update = False

        def __init__(self, task, name, framework):
            record["output_model"] = {"name": name, "framework": framework}

        def update_weights(self, weights_filename, auto_delete_file):
            if FakeOutputModel.fail_update:
                raise RuntimeError("offline mode does not support OutputModel")
            record["weights"] = Path(weights_filename).name

    fake.Task = FakeTask
    fake.OutputModel = FakeOutputModel
    return fake


def write_artifacts(tmp_path: Path) -> Path:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    (artifact_dir / "duration_model.json").write_text("{}", encoding="utf-8")
    (artifact_dir / "duration_metrics.json").write_text("{}", encoding="utf-8")
    return artifact_dir


MODEL = {
    "model_name": "local-duration-regressor",
    "model_version": "0.2.0",
    "seed": 42,
    "training_rows": 11,
    "feedback_rows": 0,
}
METRICS = {"baseline_mae": 7.33, "model_mae": 4.33, "improvement_ratio": 0.4093}


def test_tracking_is_disabled_by_default(monkeypatch, tmp_path) -> None:
    clearml_utils = load_clearml_utils()
    monkeypatch.delenv(clearml_utils.ENABLED_ENV, raising=False)

    result = clearml_utils.track_training_run(MODEL, METRICS, write_artifacts(tmp_path), dataset_paths=[])

    assert result is None
    assert clearml_utils.clearml_enabled() is False


def test_tracking_records_params_metrics_and_artifacts(monkeypatch, tmp_path) -> None:
    clearml_utils = load_clearml_utils()
    record: dict = {}
    monkeypatch.setitem(sys.modules, "clearml", build_fake_clearml(record))
    monkeypatch.setenv(clearml_utils.ENABLED_ENV, "1")
    monkeypatch.setenv(clearml_utils.OFFLINE_ENV, "1")
    artifact_dir = write_artifacts(tmp_path)
    dataset = tmp_path / "duration_training_samples.csv"
    dataset.write_text("category\n", encoding="utf-8")

    task_id = clearml_utils.track_training_run(MODEL, METRICS, artifact_dir, dataset_paths=[dataset])

    assert task_id == "fake-task-id"
    assert record["offline"] is True
    assert record["init_kwargs"]["project_name"] == "OrdoStack"
    assert record["init_kwargs"]["task_type"] == "training"
    assert len(record["scalars"]) == 3
    artifact_names = [name for name, _ in record["artifacts"]]
    assert "duration_model" in artifact_names
    assert "duration_metrics" in artifact_names
    assert "dataset-duration_training_samples.csv" in artifact_names
    assert record["closed"] is True


def test_tracking_failure_never_raises(monkeypatch, tmp_path) -> None:
    clearml_utils = load_clearml_utils()
    monkeypatch.setitem(sys.modules, "clearml", build_fake_clearml({}, fail_init=True))
    monkeypatch.setenv(clearml_utils.ENABLED_ENV, "1")

    result = clearml_utils.track_training_run(MODEL, METRICS, write_artifacts(tmp_path), dataset_paths=[])

    assert result is None


def test_promotion_registers_output_model(monkeypatch, tmp_path) -> None:
    clearml_utils = load_clearml_utils()
    record: dict = {}
    monkeypatch.setitem(sys.modules, "clearml", build_fake_clearml(record))
    monkeypatch.setenv(clearml_utils.ENABLED_ENV, "1")
    monkeypatch.delenv(clearml_utils.OFFLINE_ENV, raising=False)
    promoted = tmp_path / "duration_model-0.2.0-20260710T000000Z.json"
    promoted.write_text("{}", encoding="utf-8")

    task_id = clearml_utils.register_promoted_model(MODEL, METRICS, promoted)

    assert task_id == "fake-task-id"
    assert record["init_kwargs"]["task_type"] == "custom"
    assert record["weights"] == promoted.name
    assert "promoted" in record["tags"]
    assert "0.2.0" in record["tags"]


def test_promotion_falls_back_to_artifact_when_output_model_unsupported(monkeypatch, tmp_path) -> None:
    clearml_utils = load_clearml_utils()
    record: dict = {}
    fake = build_fake_clearml(record)
    fake.OutputModel.fail_update = True
    monkeypatch.setitem(sys.modules, "clearml", fake)
    monkeypatch.setenv(clearml_utils.ENABLED_ENV, "1")
    promoted = tmp_path / "duration_model-0.2.0-20260710T000000Z.json"
    promoted.write_text("{}", encoding="utf-8")

    task_id = clearml_utils.register_promoted_model(MODEL, METRICS, promoted)

    assert task_id == "fake-task-id"
    assert "weights" not in record
    assert ("promoted_model", promoted.name) in record["artifacts"]
    assert "promoted" in record["tags"]


def test_training_pipeline_returns_none_task_id_when_disabled(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("ORDOSTACK_CLEARML_ENABLED", raising=False)
    script_path = Path(__file__).resolve().parents[1] / "training" / "train_duration_model.py"
    spec = importlib.util.spec_from_file_location("train_duration_model_clearml", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    result = module.train_duration_model(artifact_dir=tmp_path)

    assert result["clearml_task_id"] is None
    assert json.loads((tmp_path / "duration_model.json").read_text(encoding="utf-8"))["model_name"]
