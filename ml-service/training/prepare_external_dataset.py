"""Convert the public SiP effort-estimation dataset into the OrdoStack contract schema.

Source: https://github.com/Derek-Jones/SiP_dataset (Jones & Cullum 2019,
arXiv:1901.01621) — 12,299 commercial software tasks with per-task estimated
and actual hours. The authors publish it for analysis and ask to be told when
it is used in a paper; provenance and mapping decisions are documented in
docs/ml/DATA_CARD.md.

Mapping (every decision is deliberately lossy-but-honest):
- estimated_minutes / actual_minutes  <- HoursEstimate/HoursActual * 60
- category                            <- Category (development/management/operational)
- priority                            <- ceil(Priority / 2): SiP 1-10 -> contract 1-5
- difficulty                          <- constant 3 (no such field in SiP; neutral)
- requires_focus                      <- constant false (no such field in SiP)

Filters: StatusCode == FINISHED (actuals are final), both efforts > 0, both
within the contract's 1-1440 minute bounds.

    python ml-service/training/prepare_external_dataset.py            # download + convert
    python ml-service/training/prepare_external_dataset.py --raw x.csv  # offline convert
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import urllib.request
from math import ceil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.data_contract import TARGET_MAX_MINUTES, normalize_category, validate_rows

RAW_URL = "https://raw.githubusercontent.com/Derek-Jones/SiP_dataset/master/Sip-task-info.csv"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "training" / "data" / "external" / "sip_duration_tasks.csv"
CONTRACT_HEADER = ["category", "estimated_minutes", "priority", "difficulty", "requires_focus", "actual_minutes"]


def download_raw(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {RAW_URL}")
    with urllib.request.urlopen(RAW_URL, timeout=60) as response:
        destination.write_bytes(response.read())
    return destination


def map_priority(raw_priority: str) -> int:
    """SiP priorities run 1-10 (1 = most urgent); contract wants 1-5."""
    try:
        value = int(raw_priority)
    except ValueError:
        return 3
    return min(5, max(1, ceil(value / 2)))


def convert_rows(raw_path: Path) -> tuple[list[dict], dict]:
    with raw_path.open("r", encoding="utf-8", errors="replace", newline="") as raw_file:
        raw_rows = list(csv.DictReader(raw_file))

    converted: list[dict] = []
    dropped = {"not_finished": 0, "missing_effort": 0, "out_of_bounds": 0}
    for row in raw_rows:
        if row.get("StatusCode", "").strip('"') != "FINISHED":
            dropped["not_finished"] += 1
            continue
        try:
            estimated_minutes = round(float(row["HoursEstimate"]) * 60)
            actual_minutes = round(float(row["HoursActual"]) * 60)
        except (KeyError, ValueError):
            dropped["missing_effort"] += 1
            continue
        if not (1 <= estimated_minutes <= TARGET_MAX_MINUTES and 1 <= actual_minutes <= TARGET_MAX_MINUTES):
            dropped["out_of_bounds"] += 1
            continue
        converted.append(
            {
                "category": normalize_category(row.get("Category", "unknown")),
                "estimated_minutes": estimated_minutes,
                "priority": map_priority(row.get("Priority", "")),
                "difficulty": 3,
                "requires_focus": False,
                "actual_minutes": actual_minutes,
            }
        )

    summary = {
        "raw_rows": len(raw_rows),
        "converted_rows": len(converted),
        "dropped": dropped,
        "raw_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
    }
    return converted, summary


def write_contract_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file, lineterminator="\n")
        writer.writerow(CONTRACT_HEADER)
        for row in rows:
            writer.writerow(
                [
                    row["category"],
                    row["estimated_minutes"],
                    row["priority"],
                    row["difficulty"],
                    "true" if row["requires_focus"] else "false",
                    row["actual_minutes"],
                ]
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert the SiP dataset to the OrdoStack contract schema.")
    parser.add_argument("--raw", type=Path, default=None, help="Local Sip-task-info.csv (skips download).")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    raw_path = args.raw
    if raw_path is None:
        raw_path = args.output.parent / "raw" / "Sip-task-info.csv"
        download_raw(raw_path)

    rows, summary = convert_rows(raw_path)
    report = validate_rows(rows)
    if not report.ok:
        print("conversion produced contract violations:")
        for error in report.errors[:20]:
            print("  ERROR", error)
        return 1

    write_contract_csv(rows, args.output)
    print(f"raw rows:        {summary['raw_rows']}")
    print(f"converted rows:  {summary['converted_rows']}")
    print(f"dropped:         {summary['dropped']}")
    print(f"raw sha256:      {summary['raw_sha256']}")
    print(f"contract check:  ok ({len(report.warnings)} warnings: ratio outliers/duplicates kept, see DATA_CARD)")
    print(f"written to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
