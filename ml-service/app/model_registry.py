import json
import os
from pathlib import Path
from typing import Any

DEFAULT_ARTIFACT_PATH = Path(__file__).resolve().parents[1] / "training" / "artifacts" / "duration_model.json"
DEFAULT_REGISTRY_PATH = Path(__file__).resolve().parents[1] / "training" / "artifacts" / "model_registry.json"


def active_model_path() -> Path:
    explicit_value = os.getenv("DURATION_MODEL_PATH")
    if explicit_value:
        return Path(explicit_value)

    registry = load_registry()
    active_model = registry.get("active_model")
    if isinstance(active_model, dict):
        model_path = active_model.get("path")
        if isinstance(model_path, str) and model_path.strip():
            candidate = Path(model_path)
            return candidate if candidate.is_absolute() else DEFAULT_REGISTRY_PATH.parent / candidate

    return DEFAULT_ARTIFACT_PATH


def load_registry() -> dict[str, Any]:
    registry_path = Path(os.getenv("MODEL_REGISTRY_PATH", str(DEFAULT_REGISTRY_PATH)))
    if not registry_path.exists():
        return {
            "registry_type": "local-json",
            "active_model": None,
            "models": [],
            "source": "fallback",
        }

    with registry_path.open("r", encoding="utf-8") as registry_file:
        registry = json.load(registry_file)

    if not isinstance(registry, dict):
        return {
            "registry_type": "local-json",
            "active_model": None,
            "models": [],
            "source": "invalid",
        }
    return registry


def model_registry_info() -> dict[str, Any]:
    registry = load_registry()
    return {
        "registry_type": str(registry.get("registry_type", "local-json")),
        "active_model": registry.get("active_model"),
        "model_count": len(registry.get("models", [])) if isinstance(registry.get("models"), list) else 0,
        "fallback_model_path": str(DEFAULT_ARTIFACT_PATH),
    }
