from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SECRET_PATTERNS = {
    "openai_api_key": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "github_token": re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    "slack_bot_token": re.compile(r"xoxb-[A-Za-z0-9-]{20,}"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key": re.compile(r"BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY"),
}

DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    ".vite",
    "artifacts",
}


def should_skip(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    return any(part in DEFAULT_EXCLUDES for part in relative_parts)


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and not should_skip(path, root):
            yield path


def scan_file(path: Path) -> list[tuple[str, int]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    findings: list[tuple[str, int]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(line):
                findings.append((name, line_number))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local secret-pattern audit for OrdoStack.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    root = args.root.resolve()
    findings: list[str] = []
    for path in iter_files(root):
        for pattern_name, line_number in scan_file(path):
            findings.append(f"{path.relative_to(root)}:{line_number}: {pattern_name}")

    if findings:
        print("Security audit failed:")
        for finding in findings:
            print(f"  {finding}")
        return 1

    print("Security audit passed: no known secret patterns found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
