from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_DOCUMENTS = [
    "ORDOSTACK_PROJECT_SPEC.md",
    "docs/internal/project-status-report.md",
    "docs/qa-mvp.md",
    "docs/release-process.md",
    "docs/deployment.md",
    "docs/backup-restore.md",
    "docs/observability.md",
    "docs/internal/beta-readiness.md",
    "docs/accessibility-qa.md",
]

REQUIRED_ENV_KEYS = [
    "ORDOSTACK_ENV",
    "DATA_STORE",
    "AUTH_TOKEN_SECRET",
    "AUTH_TOKEN_TTL_MINUTES",
    "AUTH_LOGIN_MAX_FAILURES",
    "AUTH_LOGIN_WINDOW_SECONDS",
    "AUTH_LOGIN_LOCKOUT_SECONDS",
    "AUTH_PASSWORD_MIN_LENGTH",
]

REQUIRED_STATUS_MARKERS = [
    "Issue 50",
    "Docker finalization",
    "Issue 51",
    "Hosted beta deployment",
    "not ready for public launch",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local OrdoStack private-beta readiness documentation.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    root = args.root.resolve()
    failures: list[str] = []

    for relative_path in REQUIRED_DOCUMENTS:
        if not (root / relative_path).exists():
            failures.append(f"missing document: {relative_path}")

    env_example = (root / ".env.example").read_text(encoding="utf-8")
    production_env_example = (root / ".env.production.example").read_text(encoding="utf-8")
    for key in REQUIRED_ENV_KEYS:
        if key not in env_example:
            failures.append(f".env.example missing {key}")
        if key not in production_env_example:
            failures.append(f".env.production.example missing {key}")

    status_report = (root / "docs" / "internal" / "project-status-report.md").read_text(encoding="utf-8")
    for marker in REQUIRED_STATUS_MARKERS:
        if marker not in status_report:
            failures.append(f"project status report missing marker: {marker}")

    if failures:
        print("Beta readiness check failed:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Beta readiness check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
