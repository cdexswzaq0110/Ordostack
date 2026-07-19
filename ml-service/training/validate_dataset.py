"""Validate a duration training CSV against the shared data contract.

Run before training; the pipeline refuses to train on a dataset whose report
contains errors. Writes a machine-readable JSON report next to the artifacts
so a failed run leaves evidence of why.

    python ml-service/training/validate_dataset.py
    python ml-service/training/validate_dataset.py --input path/to.csv --output report.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.data_contract import FEATURE_COLUMNS, TARGET_COLUMN, ValidationReport, validate_rows

DEFAULT_INPUT_PATH = PROJECT_ROOT / "training" / "data" / "duration_training_samples.csv"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "training" / "artifacts" / "dataset_validation_report.json"
MAX_REPORTED_ISSUES = 100

INT_COLUMNS = ("estimated_minutes", "priority", "difficulty", "actual_minutes")


def load_raw_rows(input_path: Path) -> list[dict[str, Any]]:
    """Parse CSV rows with best-effort typing, keeping bad values for the report.

    Unlike the training loader this does not silently drop rows — validation
    must see every row, including the broken ones.
    """
    with input_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = []
        for row in reader:
            parsed: dict[str, Any] = {"category": row.get("category", "")}
            for column in INT_COLUMNS:
                raw_value = (row.get(column) or "").strip()
                try:
                    parsed[column] = int(raw_value)
                except ValueError:
                    parsed[column] = raw_value
            focus_raw = (row.get("requires_focus") or "").strip().lower()
            parsed["requires_focus"] = focus_raw == "true" if focus_raw in ("true", "false") else focus_raw
            missing = [c for c in (*FEATURE_COLUMNS, TARGET_COLUMN) if row.get(c) is None]
            for column in missing:
                parsed.pop(column, None)
            rows.append(parsed)
    return rows


def validate_dataset(input_path: Path, report_path: Path | None = None) -> ValidationReport:
    if not input_path.exists():
        report = ValidationReport()
        report.errors.append(f"dataset not found: {input_path}")
    else:
        report = validate_rows(load_raw_rows(input_path))

    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"dataset": str(input_path), **report.to_dict()}
        # Large datasets can produce thousands of duplicate/ratio warnings;
        # keep the report readable while preserving the full counts.
        for key in ("errors", "warnings"):
            if len(payload[key]) > MAX_REPORTED_ISSUES:
                total = len(payload[key])
                payload[key] = payload[key][:MAX_REPORTED_ISSUES] + [
                    f"... {total - MAX_REPORTED_ISSUES} more (total {total})"
                ]
                payload[f"{key[:-1]}_count"] = total
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the duration training dataset.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    report = validate_dataset(args.input, args.output)
    print(f"rows: {report.row_count}, valid: {report.valid_row_count}")
    for error in report.errors:
        print(f"  ERROR {error}")
    for warning in report.warnings:
        print(f"  WARN  {warning}")
    print(f"report written to {args.output}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
