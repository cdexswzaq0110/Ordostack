"""Single source of truth for the duration-model feature schema.

Training scripts and the serving path both import this module, so a feature
added or changed in one place is automatically visible to the other. Keeping
the contract dependency-free (stdlib only) lets the runtime validate data
without installing scikit-learn.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SCHEMA_VERSION = "1.0.0"

# Serving clamps every prediction into these bounds (minutes).
PREDICTION_MIN_MINUTES = 1
PREDICTION_MAX_MINUTES = 480

# A completed task longer than a waking day is a logging error, not a signal.
TARGET_MAX_MINUTES = 1440

# actual/estimated outside this band is flagged as a suspicious row: people
# misestimate, but a 10x blowout in curated demo data means bad input.
DURATION_RATIO_MIN = 0.2
DURATION_RATIO_MAX = 5.0

# Model input features, in the order the linear model consumes them.
FEATURE_COLUMNS = ["category", "estimated_minutes", "priority", "difficulty", "requires_focus"]
TARGET_COLUMN = "actual_minutes"

# Fields that reach the ML service but MUST NOT enter the model:
# - title: free text, user-private content, high-dimensional overfitting trap
# - task_id / user_id: identifiers, would memorize instead of generalize
EXCLUDED_FIELDS = ["title", "task_id", "user_id"]

NUMERIC_RANGES = {
    "estimated_minutes": (1, TARGET_MAX_MINUTES),
    "priority": (1, 5),
    "difficulty": (1, 5),
    "actual_minutes": (1, TARGET_MAX_MINUTES),
}


def normalize_category(category: str) -> str:
    return category.strip().lower()


def encode_features(rows: list[dict], categories: list[str]) -> list[list[float]]:
    """One-hot encode rows against a fixed category list.

    Shared by training and pure-Python inference so both sides produce the
    same vector layout: [estimated, priority, difficulty, focus, *categories].
    A category outside `categories` encodes as all-zero dummies, which is the
    documented unseen-category strategy for linear artifacts.
    """
    return [
        [
            float(row["estimated_minutes"]),
            float(row["priority"]),
            float(row["difficulty"]),
            1.0 if row["requires_focus"] else 0.0,
            *[1.0 if normalize_category(row["category"]) == category else 0.0 for category in categories],
        ]
        for row in rows
    ]


def feature_names(categories: list[str]) -> list[str]:
    return ["estimated_minutes", "priority", "difficulty", "requires_focus", *[f"category={c}" for c in categories]]


def linear_predict(row: dict, model: dict) -> float:
    """Pure-Python inference for a `linear-json` artifact, clamped to bounds.

    This is the single implementation used by both training-time evaluation
    and runtime serving, so the two sides cannot drift apart. The parity test
    additionally checks it against the fitted scikit-learn pipeline.
    """
    features = encode_features([row], model["categories"])[0]
    scaled = [
        (value - mean) / scale
        for value, mean, scale in zip(features, model["scaler_mean"], model["scaler_scale"])
    ]
    prediction = model["intercept"] + sum(
        coefficient * value for coefficient, value in zip(model["coefficients"], scaled)
    )
    return float(min(PREDICTION_MAX_MINUTES, max(PREDICTION_MIN_MINUTES, prediction)))


def linear_contributions(row: dict, model: dict) -> dict[str, float]:
    """Per-feature contribution in minutes: coefficient x standardized value.

    Contributions plus the intercept reconstruct the unclamped prediction, so
    the explanation is the model, not a story about it. Category dummies are
    collapsed into a single "category" entry.
    """
    features = encode_features([row], model["categories"])[0]
    contributions: dict[str, float] = {"baseline": float(model["intercept"])}
    for name, value, mean, scale, coefficient in zip(
        model["feature_names"], features, model["scaler_mean"], model["scaler_scale"], model["coefficients"]
    ):
        impact = coefficient * ((value - mean) / scale)
        key = "category" if name.startswith("category=") else name
        contributions[key] = round(contributions.get(key, 0.0) + impact, 2)
    return contributions


@dataclass
class ValidationReport:
    schema_version: str = SCHEMA_VERSION
    row_count: int = 0
    valid_row_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "row_count": self.row_count,
            "valid_row_count": self.valid_row_count,
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def validate_rows(rows: list[dict[str, Any]]) -> ValidationReport:
    """Validate parsed dataset rows against the contract.

    Errors block training; warnings are surfaced in the report but keep the
    row usable. Row numbers are 1-based data rows (header excluded).
    """
    report = ValidationReport(row_count=len(rows))
    if not rows:
        report.errors.append("dataset is empty")
        return report

    required = set(FEATURE_COLUMNS) | {TARGET_COLUMN}
    seen_rows: dict[tuple, int] = {}

    for index, row in enumerate(rows, start=1):
        missing = required - set(row)
        if missing:
            report.errors.append(f"row {index}: missing columns {sorted(missing)}")
            continue

        if not isinstance(row["category"], str) or not normalize_category(row["category"]):
            report.errors.append(f"row {index}: category must be a non-empty string")
            continue

        type_error = False
        for column in ("estimated_minutes", "priority", "difficulty", "actual_minutes"):
            if not isinstance(row[column], int) or isinstance(row[column], bool):
                report.errors.append(f"row {index}: {column} must be an integer, got {row[column]!r}")
                type_error = True
        if not isinstance(row["requires_focus"], bool):
            report.errors.append(f"row {index}: requires_focus must be a boolean, got {row['requires_focus']!r}")
            type_error = True
        if type_error:
            continue

        range_error = False
        for column, (low, high) in NUMERIC_RANGES.items():
            if not low <= row[column] <= high:
                report.errors.append(f"row {index}: {column}={row[column]} outside [{low}, {high}]")
                range_error = True
        if range_error:
            continue

        ratio = row["actual_minutes"] / row["estimated_minutes"]
        if not DURATION_RATIO_MIN <= ratio <= DURATION_RATIO_MAX:
            report.warnings.append(
                f"row {index}: actual/estimated ratio {ratio:.2f} outside "
                f"[{DURATION_RATIO_MIN}, {DURATION_RATIO_MAX}] — check for logging mistakes"
            )

        fingerprint = tuple(row[column] for column in sorted(required))
        if fingerprint in seen_rows:
            report.warnings.append(f"row {index}: exact duplicate of row {seen_rows[fingerprint]}")
        else:
            seen_rows[fingerprint] = index

        report.valid_row_count += 1

    return report
