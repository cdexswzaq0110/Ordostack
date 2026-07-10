"""Metrics-gated promotion of a trained duration model into the local JSON registry.

A candidate is promoted only when its holdout MAE beats the naive-estimate
baseline and does not regress against the currently active model. Promotion
copies the artifact to a versioned file and rewrites model_registry.json, so
the serving path (app/model_registry.py) picks it up after POST /model/reload.
"""

import argparse
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clearml_utils import register_promoted_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = PROJECT_ROOT / "training" / "artifacts"
DEFAULT_ARTIFACT_PATH = DEFAULT_ARTIFACT_DIR / "duration_model.json"
DEFAULT_METRICS_PATH = DEFAULT_ARTIFACT_DIR / "duration_metrics.json"
DEFAULT_REGISTRY_PATH = DEFAULT_ARTIFACT_DIR / "model_registry.json"
DEFAULT_REGRESSION_TOLERANCE = 0.05


class PromotionError(Exception):
    """Raised when a candidate fails a promotion gate."""


def promote_duration_model(
    artifact_path: Path = DEFAULT_ARTIFACT_PATH,
    metrics_path: Path = DEFAULT_METRICS_PATH,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    tolerance: float = DEFAULT_REGRESSION_TOLERANCE,
    allow_regression: bool = False,
) -> dict:
    model = load_json(artifact_path, "model artifact")
    metrics = load_json(metrics_path, "metrics file")
    validate_candidate(model, metrics)

    registry = load_registry(registry_path)
    if not allow_regression:
        check_gates(metrics, registry, tolerance)

    promoted_at = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    promoted_filename = f"duration_model-{model['model_version']}-{promoted_at}.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(artifact_path, registry_path.parent / promoted_filename)

    for entry in registry["models"]:
        if entry.get("stage") == "active":
            entry["stage"] = "archived"

    new_entry = {
        "name": str(model["model_name"]),
        "version": str(model["model_version"]),
        "path": promoted_filename,
        "stage": "active",
        "promoted_at": promoted_at,
        "metrics": {
            "baseline_mae": metrics["baseline_mae"],
            "model_mae": metrics["model_mae"],
            "evaluation_mode": metrics.get("evaluation_mode", "unknown"),
            "evaluation_rows": metrics.get("evaluation_rows", 0),
        },
    }
    registry["models"].insert(0, new_entry)
    registry["active_model"] = {key: new_entry[key] for key in ("name", "version", "path", "promoted_at", "metrics")}

    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    clearml_model_id = register_promoted_model(model, metrics, registry_path.parent / promoted_filename)
    return {"promoted": True, "active_model": registry["active_model"], "clearml_model_id": clearml_model_id}


def validate_candidate(model: dict, metrics: dict) -> None:
    for field in ("model_name", "model_version"):
        if model.get(field) != metrics.get(field):
            raise PromotionError(
                f"candidate {field} mismatch: artifact={model.get(field)!r} metrics={metrics.get(field)!r}"
            )
    for field in ("baseline_mae", "model_mae"):
        if not isinstance(metrics.get(field), (int, float)):
            raise PromotionError(f"metrics missing numeric field: {field}")


def check_gates(metrics: dict, registry: dict, tolerance: float) -> None:
    if metrics["model_mae"] > metrics["baseline_mae"]:
        raise PromotionError(
            f"candidate model_mae {metrics['model_mae']} does not beat baseline_mae {metrics['baseline_mae']}"
        )

    active_model = registry.get("active_model")
    if isinstance(active_model, dict):
        active_mae = active_model.get("metrics", {}).get("model_mae")
        if isinstance(active_mae, (int, float)) and metrics["model_mae"] > active_mae * (1 + tolerance):
            raise PromotionError(
                f"candidate model_mae {metrics['model_mae']} regresses beyond active model "
                f"{active_mae} with tolerance {tolerance}"
            )


def load_registry(registry_path: Path) -> dict:
    if not registry_path.exists():
        return {"registry_type": "local-json", "active_model": None, "models": []}

    registry = load_json(registry_path, "registry")
    registry.setdefault("registry_type", "local-json")
    registry.setdefault("active_model", None)
    if not isinstance(registry.get("models"), list):
        registry["models"] = []
    return registry


def load_json(path: Path, label: str) -> dict:
    if not path.exists():
        raise PromotionError(f"{label} not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PromotionError(f"{label} is not a JSON object: {path}")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote the trained duration model when metrics gates pass.")
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT_PATH)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--tolerance", type=float, default=DEFAULT_REGRESSION_TOLERANCE)
    parser.add_argument(
        "--allow-regression",
        action="store_true",
        help="Skip metric gates. Only for deliberate rollbacks or emergency overrides.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        result = promote_duration_model(
            artifact_path=args.artifact,
            metrics_path=args.metrics,
            registry_path=args.registry,
            tolerance=args.tolerance,
            allow_regression=args.allow_regression,
        )
    except PromotionError as error:
        print(f"Promotion rejected: {error}")
        raise SystemExit(1)

    print(json.dumps(result, indent=2, sort_keys=True))
