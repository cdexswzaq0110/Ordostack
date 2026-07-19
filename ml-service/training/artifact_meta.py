"""Provenance metadata attached to every trained duration-model artifact.

Answers "which data, which code, which environment produced this file?" so a
served model can always be traced back and an incompatible artifact can be
rejected before it serves a single prediction.
"""

from __future__ import annotations

import hashlib
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.data_contract import PREDICTION_MAX_MINUTES, PREDICTION_MIN_MINUTES, SCHEMA_VERSION


def dataset_checksum(paths: list[Path]) -> str:
    """SHA-256 over the concatenated bytes of every existing dataset file."""
    digest = hashlib.sha256()
    for path in paths:
        if path is not None and path.exists():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def source_commit_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=PROJECT_ROOT,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else None


def library_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    try:
        import sklearn

        versions["scikit-learn"] = sklearn.__version__
    except ImportError:
        pass
    return versions


def build_artifact_metadata(
    dataset_paths: list[Path],
    training_rows: int,
    evaluation_rows: int,
    evaluation_strategy: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "trained_at": datetime.now(UTC).isoformat(),
        "training_rows": training_rows,
        "evaluation_rows": evaluation_rows,
        "evaluation_strategy": evaluation_strategy,
        "dataset_checksum": dataset_checksum(dataset_paths),
        "source_commit_sha": source_commit_sha(),
        "python_version": platform.python_version(),
        "library_versions": library_versions(),
        "prediction_bounds": {"min_minutes": PREDICTION_MIN_MINUTES, "max_minutes": PREDICTION_MAX_MINUTES},
    }
