"""Optional ClearML tracking for the duration-model training loop.

Disabled unless ORDOSTACK_CLEARML_ENABLED=1, so the local loop keeps working
with no ClearML package, credentials, or server. With CLEARML_OFFLINE_MODE=1
the SDK records sessions locally instead of contacting a server, which is how
the integration is verified in this repository. Failures inside ClearML must
never break training or promotion; every entry point degrades to a no-op.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

PROJECT_NAME = "OrdoStack"
ENABLED_ENV = "ORDOSTACK_CLEARML_ENABLED"
OFFLINE_ENV = "CLEARML_OFFLINE_MODE"
_TRUE_VALUES = {"1", "true", "yes"}


def clearml_enabled() -> bool:
    return os.getenv(ENABLED_ENV, "").strip().lower() in _TRUE_VALUES


def _offline_requested() -> bool:
    return os.getenv(OFFLINE_ENV, "").strip().lower() in _TRUE_VALUES


def _init_task(task_class, task_name: str, task_type) -> object:
    if _offline_requested():
        task_class.set_offline(offline_mode=True)
    return task_class.init(
        project_name=PROJECT_NAME,
        task_name=task_name,
        task_type=task_type,
        reuse_last_task_id=False,
        auto_connect_frameworks=False,
        auto_resource_monitoring=False,
    )


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


def track_training_run(
    model: dict,
    metrics: dict,
    artifact_dir: Path,
    dataset_paths: list[Path],
) -> str | None:
    """Record one training run as a ClearML task. Returns the task id or None."""
    if not clearml_enabled():
        return None

    try:
        from clearml import Task

        task = _init_task(Task, f"duration-training {_timestamp()}", Task.TaskTypes.training)
        task.connect(
            {
                key: model[key]
                for key in ("model_name", "model_version", "seed", "training_rows", "feedback_rows")
            },
            name="training",
        )
        logger = task.get_logger()
        for series in ("baseline_mae", "model_mae", "improvement_ratio"):
            logger.report_scalar(title="evaluation", series=series, value=float(metrics[series]), iteration=0)
        task.upload_artifact("duration_model", artifact_object=artifact_dir / "duration_model.json")
        task.upload_artifact("duration_metrics", artifact_object=artifact_dir / "duration_metrics.json")
        for dataset_path in dataset_paths:
            if dataset_path is not None and dataset_path.exists():
                task.upload_artifact(f"dataset-{dataset_path.name}", artifact_object=dataset_path)

        task_id = str(task.id)
        task.close()
        return task_id
    except Exception as error:  # ClearML must never break the local loop
        print(f"ClearML tracking skipped: {error}")
        return None


def register_promoted_model(model: dict, metrics: dict, promoted_path: Path) -> str | None:
    """Register a gate-passing promoted artifact as a ClearML output model."""
    if not clearml_enabled():
        return None

    try:
        from clearml import Task

        task = _init_task(Task, f"duration-promotion {_timestamp()}", Task.TaskTypes.custom)
        task.connect(
            {
                "model_name": model["model_name"],
                "model_version": model["model_version"],
                "baseline_mae": metrics["baseline_mae"],
                "model_mae": metrics["model_mae"],
            },
            name="promotion",
        )
        # OutputModel gives a real registry entry when a server is configured, but the
        # SDK does not support it in offline mode; fall back to a task artifact there.
        if not _register_output_model(task, model, promoted_path):
            task.upload_artifact("promoted_model", artifact_object=promoted_path)
        task.add_tags(["promoted", str(model["model_version"])])

        task_id = str(task.id)
        task.close()
        return task_id
    except Exception as error:  # promotion already succeeded locally; registry stays authoritative
        print(f"ClearML registration skipped: {error}")
        return None


def _register_output_model(task, model: dict, promoted_path: Path) -> bool:
    try:
        from clearml import OutputModel

        output_model = OutputModel(
            task=task,
            name=f"{model['model_name']} {model['model_version']}",
            framework="ordostack-json",
        )
        output_model.update_weights(weights_filename=str(promoted_path), auto_delete_file=False)
        return True
    except Exception:
        return False
