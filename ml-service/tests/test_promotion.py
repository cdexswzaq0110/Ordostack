import importlib.util
import json
from pathlib import Path

import pytest


def load_promotion_module():
    script_path = Path(__file__).resolve().parents[1] / "training" / "promote_duration_model.py"
    spec = importlib.util.spec_from_file_location("promote_duration_model", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load promotion module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_candidate(tmp_path: Path, model_mae: float, baseline_mae: float) -> tuple[Path, Path]:
    artifact_path = tmp_path / "duration_model.json"
    metrics_path = tmp_path / "duration_metrics.json"
    artifact_path.write_text(
        json.dumps(
            {
                "model_name": "local-duration-regressor",
                "model_version": "0.2.0",
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
                "model_version": "0.2.0",
                "evaluation_mode": "holdout",
                "evaluation_rows": 3,
                "baseline_mae": baseline_mae,
                "model_mae": model_mae,
            }
        ),
        encoding="utf-8",
    )
    return artifact_path, metrics_path


def test_promotion_accepts_candidate_that_beats_baseline(tmp_path) -> None:
    promotion = load_promotion_module()
    artifact_path, metrics_path = write_candidate(tmp_path, model_mae=8.0, baseline_mae=20.0)
    registry_path = tmp_path / "model_registry.json"

    result = promotion.promote_duration_model(
        artifact_path=artifact_path,
        metrics_path=metrics_path,
        registry_path=registry_path,
    )

    assert result["promoted"] is True
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert registry["active_model"]["version"] == "0.2.0"
    assert registry["active_model"]["metrics"]["model_mae"] == 8.0
    assert registry["models"][0]["stage"] == "active"
    promoted_artifact = registry_path.parent / registry["active_model"]["path"]
    assert promoted_artifact.exists()


def test_promotion_rejects_candidate_worse_than_baseline(tmp_path) -> None:
    promotion = load_promotion_module()
    artifact_path, metrics_path = write_candidate(tmp_path, model_mae=25.0, baseline_mae=20.0)

    with pytest.raises(promotion.PromotionError):
        promotion.promote_duration_model(
            artifact_path=artifact_path,
            metrics_path=metrics_path,
            registry_path=tmp_path / "model_registry.json",
        )


def test_promotion_rejects_regression_against_active_model(tmp_path) -> None:
    promotion = load_promotion_module()
    artifact_path, metrics_path = write_candidate(tmp_path, model_mae=8.0, baseline_mae=20.0)
    registry_path = tmp_path / "model_registry.json"

    promotion.promote_duration_model(
        artifact_path=artifact_path,
        metrics_path=metrics_path,
        registry_path=registry_path,
    )

    # A later candidate that is much worse than the active model must be rejected.
    _, worse_metrics = write_candidate(tmp_path, model_mae=15.0, baseline_mae=20.0)
    with pytest.raises(promotion.PromotionError):
        promotion.promote_duration_model(
            artifact_path=artifact_path,
            metrics_path=worse_metrics,
            registry_path=registry_path,
        )


def test_promotion_archives_previous_active_model(tmp_path) -> None:
    promotion = load_promotion_module()
    artifact_path, metrics_path = write_candidate(tmp_path, model_mae=8.0, baseline_mae=20.0)
    registry_path = tmp_path / "model_registry.json"

    promotion.promote_duration_model(
        artifact_path=artifact_path,
        metrics_path=metrics_path,
        registry_path=registry_path,
    )
    _, better_metrics = write_candidate(tmp_path, model_mae=6.0, baseline_mae=20.0)
    promotion.promote_duration_model(
        artifact_path=artifact_path,
        metrics_path=better_metrics,
        registry_path=registry_path,
    )

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    stages = [entry["stage"] for entry in registry["models"]]
    assert stages.count("active") == 1
    assert stages.count("archived") == 1
    assert registry["active_model"]["metrics"]["model_mae"] == 6.0


def test_promotion_allow_regression_overrides_gates(tmp_path) -> None:
    promotion = load_promotion_module()
    artifact_path, metrics_path = write_candidate(tmp_path, model_mae=25.0, baseline_mae=20.0)

    result = promotion.promote_duration_model(
        artifact_path=artifact_path,
        metrics_path=metrics_path,
        registry_path=tmp_path / "model_registry.json",
        allow_regression=True,
    )

    assert result["promoted"] is True
