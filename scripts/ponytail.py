from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    command: list[str]


def run_check(check: Check, root: Path) -> bool:
    print(f"RUN {check.name}")
    completed = subprocess.run(check.command, cwd=root, text=True)
    if completed.returncode == 0:
        print(f"PASS {check.name}")
        return True
    print(f"FAIL {check.name}: exit {completed.returncode}")
    return False


def build_checks(root: Path, include_compose_config: bool, require_git_clean: bool) -> list[Check]:
    checks = [
        Check("documentation completeness", [sys.executable, "scripts/docs_completeness_check.py", "--root", "."]),
        Check("release QA gate", [sys.executable, "scripts/release_qa_gate.py"]),
        Check("git whitespace check", ["git", "-c", f"safe.directory={root.as_posix()}", "diff", "--check"]),
    ]

    if include_compose_config:
        docker_path = shutil.which("docker")
        if docker_path is None:
            checks.append(Check("docker compose config", [sys.executable, "-c", "raise SystemExit('docker not found')"]))
        else:
            checks.append(Check("docker compose config", [docker_path, "compose", "config"]))

    if require_git_clean:
        checks.append(
            Check(
                "git clean status",
                [
                    sys.executable,
                    "-c",
                    "import subprocess, sys; "
                    "result=subprocess.run(['git','status','--short'], capture_output=True, text=True); "
                    "print(result.stdout, end=''); "
                    "sys.exit(0 if result.returncode == 0 and result.stdout == '' else 1)",
                ],
            )
        )

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the compact OrdoStack clean gate.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--include-compose-config", action="store_true")
    parser.add_argument("--require-git-clean", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    checks = build_checks(
        root=root,
        include_compose_config=args.include_compose_config,
        require_git_clean=args.require_git_clean,
    )

    failed = [check for check in checks if not run_check(check, root)]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
