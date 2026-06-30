from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_FILES = [
    "docs/backup-restore.md",
    "scripts/backup_mysql.ps1",
    "scripts/backup_mysql.sh",
    "scripts/verify_mysql_backup.ps1",
    "scripts/verify_mysql_backup.sh",
]

REQUIRED_POLICY_TERMS = [
    "temporary target",
    "retention",
    "approval",
    "off-host",
    "encryption",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit OrdoStack backup policy and local backup scripts.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    root = args.root.resolve()
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing required file: {relative_path}")

    backup_doc = root / "docs" / "backup-restore.md"
    if backup_doc.exists():
        normalized_doc = backup_doc.read_text(encoding="utf-8").lower()
        for required_term in REQUIRED_POLICY_TERMS:
            if required_term not in normalized_doc:
                failures.append(f"backup policy missing term: {required_term}")

    if failures:
        print("Backup policy audit failed:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Backup policy audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
