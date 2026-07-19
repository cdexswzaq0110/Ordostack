"""Metrics-gated promotion of a trained duration model into the local JSON registry.

Gates, in order:
1. evidence gate  — enough evaluation rows to mean anything; otherwise the
   candidate is rejected with "insufficient evidence for automatic promotion"
   (override: --allow-insufficient-evidence, a deliberate human decision).
2. baseline gate  — holdout MAE must beat the naive-estimate baseline.
3. regression gate — must not regress against the currently active model
   beyond the tolerance. (2 and 3 override: --allow-regression.)

Promotion copies the artifact to a versioned file and atomically rewrites
model_registry.json, so the serving path (app/model_registry.py) picks it up
after POST /model/reload. Every decision — accepted, rejected, dry-run,
rollback — is appended to promotion_audit.jsonl next to the registry.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clearml_utils import register_promoted_model
from eval_metrics import INSUFFICIENT_EVIDENCE_MESSAGE, MIN_EVALUATION_ROWS_FOR_EVIDENCE

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = PROJECT_ROOT / "training" / "artifacts"
DEFAULT_ARTIFACT_PATH = DEFAULT_ARTIFACT_DIR / "duration_model.json"
DEFAULT_METRICS_PATH = DEFAULT_ARTIFACT_DIR / "duration_metrics.json"
DEFAULT_REGISTRY_PATH = DEFAULT_ARTIFACT_DIR / "model_registry.json"
DEFAULT_REGRESSION_TOLERANCE = 0.05
AUDIT_LOG_NAME = "promotion_audit.jsonl"


class PromotionError(Exception):
    """Raised when a candidate fails a promotion gate."""


def promote_duration_model(
    artifact_path: Path = DEFAULT_ARTIFACT_PATH,
    metrics_path: Path = DEFAULT_METRICS_PATH,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    tolerance: float = DEFAULT_REGRESSION_TOLERANCE,
    allow_regression: bool = False,
    allow_insufficient_evidence: bool = False,
    dry_run: bool = False,
) -> dict:
    model = load_json(artifact_path, "model artifact")
    metrics = load_json(metrics_path, "metrics file")
    validate_candidate(model, metrics)

    registry = load_registry(registry_path)
    try:
        if not allow_insufficient_evidence:
            check_evidence_gate(metrics)
        if not allow_regression:
            check_metric_gates(metrics, registry, tolerance)
    except PromotionError as error:
        append_audit_entry(
            registry_path,
            action="rejected" if not dry_run else "dry-run-rejected",
            model=model,
            metrics=metrics,
            detail=str(error),
        )
        raise

    if dry_run:
        append_audit_entry(registry_path, action="dry-run-accepted", model=model, metrics=metrics)
        return {
            "promoted": False,
            "dry_run": True,
            "would_promote": True,
            "candidate": {"name": model["model_name"], "version": model["model_version"]},
            "active_model": registry.get("active_model"),
        }

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

    write_registry_atomic(registry_path, registry)
    append_audit_entry(
        registry_path,
        action="promoted",
        model=model,
        metrics=metrics,
        detail=f"overrides: regression={allow_regression}, insufficient_evidence={allow_insufficient_evidence}",
    )
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


def check_evidence_gate(metrics: dict) -> None:
    evaluation_rows = metrics.get("evaluation_rows", 0)
    evaluation_mode = metrics.get("evaluation_mode", "unknown")
    if not isinstance(evaluation_rows, int) or evaluation_rows < MIN_EVALUATION_ROWS_FOR_EVIDENCE:
        raise PromotionError(
            f"{INSUFFICIENT_EVIDENCE_MESSAGE}: {evaluation_rows} evaluation rows "
            f"(minimum {MIN_EVALUATION_ROWS_FOR_EVIDENCE})"
        )
    if evaluation_mode != "holdout":
        raise PromotionError(
            f"{INSUFFICIENT_EVIDENCE_MESSAGE}: evaluation mode {evaluation_mode!r} is not out-of-sample"
        )


def check_metric_gates(metrics: dict, registry: dict, tolerance: float) -> None:
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


def write_registry_atomic(registry_path: Path, registry: dict) -> None:
    """Write via a temp file + os.replace so a crash never leaves half a registry."""
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(registry, indent=2, sort_keys=True) + "\n"
    fd, temp_name = tempfile.mkstemp(dir=registry_path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as temp_file:
            temp_file.write(payload)
        os.replace(temp_name, registry_path)
    except BaseException:
        Path(temp_name).unlink(missing_ok=True)
        raise


def append_audit_entry(
    registry_path: Path,
    action: str,
    model: dict,
    metrics: dict | None = None,
    detail: str = "",
) -> None:
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "action": action,
        "model_name": model.get("model_name"),
        "model_version": model.get("model_version"),
        "model_mae": (metrics or {}).get("model_mae"),
        "baseline_mae": (metrics or {}).get("baseline_mae"),
        "evaluation_rows": (metrics or {}).get("evaluation_rows"),
        "detail": detail,
    }
    audit_path = registry_path.parent / AUDIT_LOG_NAME
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_path.open("a", encoding="utf-8") as audit_file:
        audit_file.write(json.dumps(entry, sort_keys=True) + "\n")


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
    parser.add_argument(
        "--allow-insufficient-evidence",
        action="store_true",
        help="Promote even when the evaluation sample is too small to prove anything. "
        "A human decision that must be justified outside this tool.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Evaluate all gates and report the outcome without touching the registry.",
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
            allow_insufficient_evidence=args.allow_insufficient_evidence,
            dry_run=args.dry_run,
        )
    except PromotionError as error:
        print(f"Promotion rejected: {error}")
        raise SystemExit(1)

    print(json.dumps(result, indent=2, sort_keys=True))
