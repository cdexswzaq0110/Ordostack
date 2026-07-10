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


def test_train_duration_model_reports_holdout_metrics(tmp_path) -> None:
    training_module = load_training_module()

    result = training_module.train_duration_model(artifact_dir=tmp_path)

    metrics = result["metrics"]
    assert metrics["evaluation_mode"] == "holdout"
    assert metrics["evaluation_rows"] >= 1
    assert metrics["training_rows"] + metrics["evaluation_rows"] > metrics["training_rows"]
    assert metrics["baseline_mae"] > 0
    assert metrics["model_mae"] > 0
    assert "improvement_ratio" in metrics


def test_train_duration_model_is_deterministic_for_same_seed(tmp_path) -> None:
    training_module = load_training_module()

    first = training_module.train_duration_model(artifact_dir=tmp_path / "first", seed=7)
    second = training_module.train_duration_model(artifact_dir=tmp_path / "second", seed=7)

    assert first["model"]["category_multipliers"] == second["model"]["category_multipliers"]
    assert first["metrics"]["model_mae"] == second["metrics"]["model_mae"]


def test_train_duration_model_merges_feedback_rows(tmp_path) -> None:
    training_module = load_training_module()
    feedback_path = tmp_path / "duration_feedback.csv"
    feedback_path.write_text(
        "category,estimated_minutes,priority,difficulty,requires_focus,actual_minutes\n"
        "writing,40,3,2,false,52\n"
        "writing,55,4,3,true,70\n",
        encoding="utf-8",
    )

    without_feedback = training_module.train_duration_model(artifact_dir=tmp_path / "base")
    with_feedback = training_module.train_duration_model(
        artifact_dir=tmp_path / "merged",
        feedback_path=feedback_path,
    )

    assert with_feedback["model"]["feedback_rows"] == 2
    total_base = without_feedback["metrics"]["training_rows"] + without_feedback["metrics"]["evaluation_rows"]
    total_merged = with_feedback["metrics"]["training_rows"] + with_feedback["metrics"]["evaluation_rows"]
    assert total_merged == total_base + 2


def test_train_duration_model_ignores_missing_feedback_file(tmp_path) -> None:
    training_module = load_training_module()

    result = training_module.train_duration_model(
        artifact_dir=tmp_path,
        feedback_path=tmp_path / "does_not_exist.csv",
    )

    assert result["model"]["feedback_rows"] == 0


def test_train_duration_model_accepts_header_only_feedback_file(tmp_path) -> None:
    training_module = load_training_module()
    feedback_path = tmp_path / "duration_feedback.csv"
    feedback_path.write_text(
        "category,estimated_minutes,priority,difficulty,requires_focus,actual_minutes\n",
        encoding="utf-8",
    )

    result = training_module.train_duration_model(artifact_dir=tmp_path, feedback_path=feedback_path)

    assert result["model"]["feedback_rows"] == 0
