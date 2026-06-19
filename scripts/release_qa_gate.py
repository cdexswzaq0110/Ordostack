from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GateResult:
    name: str
    status: str
    detail: str


def run_command(name: str, command: list[str], cwd: Path) -> GateResult:
    completed_process = subprocess.run(command, cwd=cwd, text=True)
    if completed_process.returncode == 0:
        return GateResult(name=name, status="passed", detail="command exited 0")
    return GateResult(name=name, status="failed", detail=f"command exited {completed_process.returncode}")


def run_optional_frontend_build(root: Path, require_frontend: bool) -> GateResult:
    npm_path = shutil.which("npm")
    if npm_path is None:
        status = "failed" if require_frontend else "skipped"
        return GateResult(
            name="web-dashboard build",
            status=status,
            detail="npm is not available in this environment",
        )

    tsc_path = root / "web-dashboard" / "node_modules" / ".bin" / ("tsc.cmd" if sys.platform == "win32" else "tsc")
    if not tsc_path.exists():
        status = "failed" if require_frontend else "skipped"
        return GateResult(
            name="web-dashboard build",
            status=status,
            detail="dashboard dependencies are not installed; run npm ci in web-dashboard",
        )

    return run_command("web-dashboard build", [npm_path, "run", "build"], root / "web-dashboard")


def run_optional_visual_regression(root: Path, require_visual: bool) -> GateResult:
    baseline = root / "artifacts" / "visual-baseline" / "dashboard.png"
    candidate = root / "artifacts" / "browser-smoke" / "dashboard.png"
    if not baseline.exists() or not candidate.exists():
        status = "failed" if require_visual else "skipped"
        return GateResult(
            name="visual regression",
            status=status,
            detail="baseline or candidate screenshot is missing",
        )

    return run_command(
        "visual regression",
        [
            sys.executable,
            "scripts/visual_regression.py",
            "--baseline",
            str(baseline),
            "--candidate",
            str(candidate),
            "--threshold",
            "0.01",
        ],
        root,
    )


def verify_translation_coverage(root: Path) -> GateResult:
    app_text = (root / "web-dashboard" / "src" / "App.tsx").read_text(encoding="utf-8")
    i18n_text = (root / "web-dashboard" / "src" / "i18n.ts").read_text(encoding="utf-8")
    keys = sorted(set(extract_translation_keys(app_text)))
    missing = [key for key in keys if f'"{key}"' not in i18n_text and f"{key}:" not in i18n_text]
    if missing:
        return GateResult(
            name="translation coverage",
            status="failed",
            detail="missing keys: " + ", ".join(missing[:10]),
        )
    return GateResult(name="translation coverage", status="passed", detail=f"{len(keys)} keys covered")


def extract_translation_keys(text: str) -> list[str]:
    pattern = re.compile(r'(?<![A-Za-z0-9_])t\("([^"]+)"\)')
    return [match.group(1) for match in pattern.finditer(text)]


def build_gate_results(root: Path, require_frontend: bool, require_visual: bool) -> list[GateResult]:
    return [
        run_command(
            "backend-api tests",
            [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "tests"],
            root / "backend-api",
        ),
        run_command(
            "scheduler-service tests",
            [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "tests"],
            root / "scheduler-service",
        ),
        run_command(
            "ml-service tests",
            [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "tests"],
            root / "ml-service",
        ),
        run_optional_frontend_build(root, require_frontend),
        run_command("a11y static audit", [sys.executable, "scripts/a11y_static_audit.py"], root),
        run_command("security audit", [sys.executable, "scripts/security_audit.py", "--root", "."], root),
        run_command("documentation completeness", [sys.executable, "scripts/docs_completeness_check.py", "--root", "."], root),
        run_command("backup policy audit", [sys.executable, "scripts/backup_policy_audit.py", "--root", "."], root),
        run_command("beta readiness check", [sys.executable, "scripts/beta_readiness_check.py", "--root", "."], root),
        verify_translation_coverage(root),
        run_optional_visual_regression(root, require_visual),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the non-Docker OrdoStack release QA gate.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--require-frontend", action="store_true")
    parser.add_argument("--require-visual", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    results = build_gate_results(
        root=root,
        require_frontend=args.require_frontend,
        require_visual=args.require_visual,
    )

    failed = [result for result in results if result.status == "failed"]
    for result in results:
        print(f"{result.status.upper():7} {result.name}: {result.detail}")

    if failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
