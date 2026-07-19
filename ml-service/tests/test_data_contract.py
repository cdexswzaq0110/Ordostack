import sys
from pathlib import Path

from app.data_contract import (
    SCHEMA_VERSION,
    encode_features,
    feature_names,
    validate_rows,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "training"))
from validate_dataset import validate_dataset  # noqa: E402


def make_row(**overrides) -> dict:
    row = {
        "category": "study",
        "estimated_minutes": 60,
        "priority": 3,
        "difficulty": 3,
        "requires_focus": True,
        "actual_minutes": 70,
    }
    row.update(overrides)
    return row


def test_valid_rows_pass_with_no_errors() -> None:
    report = validate_rows([make_row(), make_row(category="qa", requires_focus=False)])
    assert report.ok
    assert report.row_count == 2
    assert report.valid_row_count == 2
    assert report.schema_version == SCHEMA_VERSION


def test_empty_dataset_is_an_error() -> None:
    report = validate_rows([])
    assert not report.ok
    assert "dataset is empty" in report.errors[0]


def test_missing_column_is_an_error() -> None:
    row = make_row()
    del row["priority"]
    report = validate_rows([row])
    assert not report.ok
    assert "missing columns" in report.errors[0]


def test_non_integer_minutes_is_an_error() -> None:
    report = validate_rows([make_row(estimated_minutes="sixty")])
    assert not report.ok
    assert "estimated_minutes" in report.errors[0]


def test_zero_or_negative_minutes_is_an_error() -> None:
    report = validate_rows([make_row(estimated_minutes=0), make_row(actual_minutes=-5)])
    assert not report.ok
    assert len(report.errors) == 2


def test_priority_and_difficulty_range_enforced() -> None:
    report = validate_rows([make_row(priority=6), make_row(difficulty=0)])
    assert not report.ok
    assert any("priority=6" in error for error in report.errors)
    assert any("difficulty=0" in error for error in report.errors)


def test_extreme_duration_ratio_is_a_warning_not_an_error() -> None:
    report = validate_rows([make_row(estimated_minutes=10, actual_minutes=120)])
    assert report.ok
    assert any("ratio" in warning for warning in report.warnings)


def test_exact_duplicate_rows_are_flagged() -> None:
    report = validate_rows([make_row(), make_row()])
    assert report.ok
    assert any("duplicate" in warning for warning in report.warnings)


def test_encode_features_matches_contract_order_and_unseen_category_is_all_zero() -> None:
    categories = ["coding", "study"]
    encoded = encode_features([make_row(category="Study "), make_row(category="brand-new")], categories)
    assert encoded[0] == [60.0, 3.0, 3.0, 1.0, 0.0, 1.0]
    assert encoded[1][4:] == [0.0, 0.0]
    assert feature_names(categories) == [
        "estimated_minutes",
        "priority",
        "difficulty",
        "requires_focus",
        "category=coding",
        "category=study",
    ]


def test_validate_dataset_cli_reports_missing_file(tmp_path) -> None:
    report = validate_dataset(tmp_path / "missing.csv", tmp_path / "report.json")
    assert not report.ok
    assert (tmp_path / "report.json").exists()


def test_validate_dataset_reads_real_csv(tmp_path) -> None:
    csv_path = tmp_path / "data.csv"
    csv_path.write_text(
        "category,estimated_minutes,priority,difficulty,requires_focus,actual_minutes\n"
        "study,60,3,3,true,70\n"
        "qa,45,4,2,false,bad-value\n",
        encoding="utf-8",
    )
    report = validate_dataset(csv_path, tmp_path / "report.json")
    assert report.row_count == 2
    assert report.valid_row_count == 1
    assert any("actual_minutes" in error for error in report.errors)
