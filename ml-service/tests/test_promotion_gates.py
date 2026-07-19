"""Evidence gate, dry-run, audit log, and rollback behavior."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def load_module(script_name: str):
    script_path = Path(__file__).resolve().parents[1] / "training" / script_name
    spec = importlib.util.spec_from_file_location(script_name.removesuffix(".py") + "_under_test", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {script_name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_candidate(
    tmp_path: Path,
    model_mae: float = 8.0,
    baseline_mae: float = 20.0,
    evaluation_rows: int = 3,
    evaluation_mode: str = "holdout",
    version: str = "0.2.0",
) -> tuple[Path, Path]:
    artifact_path = tmp_path / "duration_model.json"
    metrics_path = tmp_path / "duration_metrics.json"
    artifact_path.write_text(
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
    metrics_path.write_text(
        json.dumps(
            {
                "model_name": "local-duration-regressor",
                "model_version": version,
                "evaluation_mode": evaluation_mode,
                "evaluation_rows": evaluation_rows,
                "baseline_mae": baseline_mae,
                "model_mae": model_mae,
            }
        ),
        encoding="utf-8",
    )
    return artifact_path, metrics_path


def test_small_evaluation_sample_is_rejected_with_explicit_message(tmp_path) -> None:
    promotion = load_module("promote_duration_model.py")
    artifact_path, metrics_path = write_candidate(tmp_path, evaluation_rows=3)

    with pytest.raises(promotion.PromotionError, match="insufficient evidence for automatic promotion"):
        promotion.promote_duration_model(
            artifact_path=artifact_path,
            metrics_path=metrics_path,
            registry_path=tmp_path / "model_registry.json",
        )
    assert not (tmp_path / "model_registry.json").exists()


def test_in_sample_evaluation_is_rejected_even_with_many_rows(tmp_path) -> None:
    promotion = load_module("promote_duration_model.py")
    artifact_path, metrics_path = write_candidate(tmp_path, evaluation_rows=50, evaluation_mode="in-sample")

    with pytest.raises(promotion.PromotionError, match="insufficient evidence"):
        promotion.promote_duration_model(
            artifact_path=artifact_path,
            metrics_path=metrics_path,
            registry_path=tmp_path / "model_registry.json",
        )


def test_sufficient_holdout_sample_promotes_without_overrides(tmp_path) -> None:
    promotion = load_module("promote_duration_model.py")
    artifact_path, metrics_path = write_candidate(tmp_path, evaluation_rows=12)

    result = promotion.promote_duration_model(
        artifact_path=artifact_path,
        metrics_path=metrics_path,
        registry_path=tmp_path / "model_registry.json",
    )

    assert result["promoted"] is True


def test_dry_run_reports_outcome_without_writing_registry(tmp_path) -> None:
    promotion = load_module("promote_duration_model.py")
    artifact_path, metrics_path = write_candidate(tmp_path, evaluation_rows=12)
    registry_path = tmp_path / "model_registry.json"

    result = promotion.promote_duration_model(
        artifact_path=artifact_path,
        metrics_path=metrics_path,
        registry_path=registry_path,
        dry_run=True,
    )

    assert result == {
        "promoted": False,
        "dry_run": True,
        "would_promote": True,
        "candidate": {"name": "local-duration-regressor", "version": "0.2.0"},
        "active_model": None,
    }
    assert not registry_path.exists()


def test_every_decision_is_appended_to_the_audit_log(tmp_path) -> None:
    promotion = load_module("promote_duration_model.py")
    artifact_path, metrics_path = write_candidate(tmp_path, evaluation_rows=12)
    registry_path = tmp_path / "model_registry.json"

    promotion.promote_duration_model(
        artifact_path=artifact_path, metrics_path=metrics_path, registry_path=registry_path
    )
    _, small_metrics = write_candidate(tmp_path, evaluation_rows=2)
    with pytest.raises(promotion.PromotionError):
        promotion.promote_duration_model(
            artifact_path=artifact_path, metrics_path=small_metrics, registry_path=registry_path
        )

    audit_lines = (tmp_path / "promotion_audit.jsonl").read_text(encoding="utf-8").strip().splitlines()
    actions = [json.loads(line)["action"] for line in audit_lines]
    assert actions == ["promoted", "rejected"]


def test_rollback_restores_previous_model_and_survives_reload(tmp_path) -> None:
    promotion = load_module("promote_duration_model.py")
    rollback = load_module("rollback_duration_model.py")
    registry_path = tmp_path / "model_registry.json"

    artifact_path, metrics_path = write_candidate(tmp_path, evaluation_rows=12, version="0.2.0")
    promotion.promote_duration_model(
        artifact_path=artifact_path, metrics_path=metrics_path, registry_path=registry_path
    )
    artifact_path, metrics_path = write_candidate(
        tmp_path, evaluation_rows=12, version="0.3.0", model_mae=7.0
    )
    promotion.promote_duration_model(
        artifact_path=artifact_path, metrics_path=metrics_path, registry_path=registry_path
    )

    result = rollback.rollback_duration_model(registry_path=registry_path)

    assert result["rolled_back"] is True
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert registry["active_model"]["version"] == "0.2.0"
    stages = {entry["version"]: entry["stage"] for entry in registry["models"]}
    assert stages["0.2.0"] == "active"
    assert stages["0.3.0"] == "archived"
    restored_artifact = registry_path.parent / registry["active_model"]["path"]
    assert restored_artifact.exists()


def test_rollback_to_specific_version(tmp_path) -> None:
    promotion = load_module("promote_duration_model.py")
    rollback = load_module("rollback_duration_model.py")
    registry_path = tmp_path / "model_registry.json"

    for version, mae in (("0.1.0", 9.0), ("0.2.0", 8.0), ("0.3.0", 7.0)):
        artifact_path, metrics_path = write_candidate(
            tmp_path, evaluation_rows=12, version=version, model_mae=mae
        )
        promotion.promote_duration_model(
            artifact_path=artifact_path, metrics_path=metrics_path, registry_path=registry_path
        )

    result = rollback.rollback_duration_model(registry_path=registry_path, target_version="0.1.0")

    assert result["active_model"]["version"] == "0.1.0"


def test_rollback_without_history_fails_clearly(tmp_path) -> None:
    rollback = load_module("rollback_duration_model.py")

    with pytest.raises(rollback.RollbackError):
        rollback.rollback_duration_model(registry_path=tmp_path / "missing_registry.json")


def test_rollback_refuses_corrupted_target_artifact(tmp_path) -> None:
    promotion = load_module("promote_duration_model.py")
    rollback = load_module("rollback_duration_model.py")
    registry_path = tmp_path / "model_registry.json"

    for version in ("0.2.0", "0.3.0"):
        artifact_path, metrics_path = write_candidate(tmp_path, evaluation_rows=12, version=version)
        promotion.promote_duration_model(
            artifact_path=artifact_path, metrics_path=metrics_path, registry_path=registry_path
        )

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    archived = next(entry for entry in registry["models"] if entry["stage"] == "archived")
    (tmp_path / archived["path"]).write_text("{ corrupted", encoding="utf-8")

    with pytest.raises(rollback.RollbackError, match="not valid JSON"):
        rollback.rollback_duration_model(registry_path=registry_path)
