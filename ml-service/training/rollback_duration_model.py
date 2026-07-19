"""Roll the model registry back to a previously promoted artifact.

Default target is the most recently archived model; --version picks a
specific one. The target artifact file is loaded and sanity-checked before
the registry flips, so a rollback can never point serving at a missing or
corrupted file. After rolling back, call POST /model/reload (or restart the
service) to serve the restored model.

    python ml-service/training/rollback_duration_model.py
    python ml-service/training/rollback_duration_model.py --version 0.2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from promote_duration_model import (
    DEFAULT_REGISTRY_PATH,
    append_audit_entry,
    load_registry,
    write_registry_atomic,
)


class RollbackError(Exception):
    """Raised when no safe rollback target exists."""


def rollback_duration_model(
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    target_version: str | None = None,
) -> dict:
    if not registry_path.exists():
        raise RollbackError(f"registry not found: {registry_path}")

    registry = load_registry(registry_path)
    active_entry = next((entry for entry in registry["models"] if entry.get("stage") == "active"), None)
    target_entry = find_rollback_target(registry, active_entry, target_version)
    verify_artifact(registry_path.parent / target_entry["path"])

    if active_entry is not None:
        active_entry["stage"] = "archived"
    target_entry["stage"] = "active"
    target_entry["restored_at"] = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    registry["active_model"] = {
        key: target_entry[key] for key in ("name", "version", "path", "promoted_at", "metrics") if key in target_entry
    }

    write_registry_atomic(registry_path, registry)
    append_audit_entry(
        registry_path,
        action="rollback",
        model={"model_name": target_entry.get("name"), "model_version": target_entry.get("version")},
        detail=(
            f"rolled back from {active_entry.get('version') if active_entry else 'none'} "
            f"to {target_entry.get('version')}"
        ),
    )
    return {"rolled_back": True, "active_model": registry["active_model"]}


def find_rollback_target(registry: dict, active_entry: dict | None, target_version: str | None) -> dict:
    candidates = [
        entry
        for entry in registry["models"]
        if entry is not active_entry and isinstance(entry.get("path"), str)
    ]
    if target_version is not None:
        for entry in candidates:
            if entry.get("version") == target_version:
                return entry
        raise RollbackError(f"no archived model with version {target_version!r}")

    if not candidates:
        raise RollbackError("no archived model available to roll back to")
    # models[] is newest-first (promotion inserts at index 0), so the first
    # non-active entry is the most recent previous model.
    return candidates[0]


def verify_artifact(artifact_path: Path) -> None:
    if not artifact_path.exists():
        raise RollbackError(f"target artifact missing: {artifact_path}")
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RollbackError(f"target artifact is not valid JSON: {artifact_path}") from error
    if not isinstance(payload, dict) or "model_name" not in payload or "model_version" not in payload:
        raise RollbackError(f"target artifact missing required fields: {artifact_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Roll back the active duration model to a previous version.")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--version", type=str, default=None, help="Specific archived version to restore.")
    args = parser.parse_args()

    try:
        result = rollback_duration_model(registry_path=args.registry, target_version=args.version)
    except RollbackError as error:
        print(f"Rollback failed: {error}")
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    print("Remember to POST /model/reload so the service serves the restored model.")
    return 0


if __name__ == "__main__":
    return_code = main()
    sys.exit(return_code)
