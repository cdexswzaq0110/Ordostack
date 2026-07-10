import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("sklearn", reason="scikit-learn is an optional training dependency")


def load_comparison_module():
    script_path = Path(__file__).resolve().parents[1] / "training" / "compare_models.py"
    spec = importlib.util.spec_from_file_location("compare_models_under_test", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load compare_models module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def write_synthetic_dataset(tmp_path: Path) -> Path:
    """Rows where actuals are exactly 1.3x estimates: a learnable multiplier."""
    lines = ["category,estimated_minutes,priority,difficulty,requires_focus,actual_minutes"]
    for index in range(12):
        estimate = 40 + index * 10
        lines.append(f"study,{estimate},3,3,false,{round(estimate * 1.3)}")
    dataset = tmp_path / "synthetic.csv"
    dataset.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dataset


def test_comparison_covers_all_candidates_on_seed_data() -> None:
    comparison_module = load_comparison_module()

    comparison = comparison_module.compare_models()

    assert comparison["rows"] >= 10
    assert set(comparison["results"]) == {
        "naive-estimate",
        "multiplier-table (production)",
        "ridge-regression",
        "gradient-boosting",
    }
    assert all(stats["mae_mean"] >= 0 for stats in comparison["results"].values())
    naive_mae = comparison["results"]["naive-estimate"]["mae_mean"]
    assert naive_mae >= min(stats["mae_mean"] for stats in comparison["results"].values())


def test_comparison_is_deterministic_for_same_seed() -> None:
    comparison_module = load_comparison_module()

    first = comparison_module.compare_models(seed=7)
    second = comparison_module.compare_models(seed=7)

    assert first["results"] == second["results"]


def test_learnable_multiplier_beats_naive_baseline(tmp_path) -> None:
    comparison_module = load_comparison_module()
    dataset = write_synthetic_dataset(tmp_path)

    comparison = comparison_module.compare_models(input_path=dataset)

    results = comparison["results"]
    assert results["multiplier-table (production)"]["mae_mean"] < results["naive-estimate"]["mae_mean"]
