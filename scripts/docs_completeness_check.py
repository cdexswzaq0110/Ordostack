from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentRequirement:
    path: str
    required_terms: tuple[str, ...]


REQUIREMENTS = [
    DocumentRequirement(
        path="README.md",
        required_terms=("Quick Start", "Docker", "Health Checks", "Clean Check", "Documentation Map"),
    ),
    DocumentRequirement(
        path="ORDOSTACK_PROJECT_SPEC.md",
        required_terms=("Current Baseline", "System Components", "Quality Gates", "Definition Of Done"),
    ),
    DocumentRequirement(
        path="ARCHITECTURE.md",
        required_terms=("Runtime Boundaries", "Data Flow", "Persistence", "Quality Gates"),
    ),
    DocumentRequirement(
        path="docs/system-analysis.md",
        required_terms=("Problem", "Actors", "Data Ownership", "Acceptance Baseline"),
    ),
    DocumentRequirement(
        path="docs/qa-mvp.md",
        required_terms=("Smoke Tests", "Issue 46-53", "Auth hardening", "Backup and beta policy"),
    ),
    DocumentRequirement(
        path="docs/release-process.md",
        required_terms=("Current Version", "Clean Check", "Tagging"),
    ),
    DocumentRequirement(
        path="docs/documentation-completeness.md",
        required_terms=("Testing Documents", "System Design Documents", "Status"),
    ),
    DocumentRequirement(
        path="CONTRIBUTING.md",
        required_terms=("Local Setup", "Quality Gate", "No Secrets"),
    ),
    DocumentRequirement(
        path="SECURITY.md",
        required_terms=("Supported Version", "Reporting", "Secrets"),
    ),
    DocumentRequirement(
        path="SUPPORT.md",
        required_terms=("Support Scope", "Before Asking", "Known Limits"),
    ),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that launch-facing OrdoStack docs are complete.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    root = args.root.resolve()
    failures: list[str] = []

    for requirement in REQUIREMENTS:
        path = root / requirement.path
        if not path.exists():
            failures.append(f"missing document: {requirement.path}")
            continue

        text = path.read_text(encoding="utf-8").lower()
        for term in requirement.required_terms:
            if term.lower() not in text:
                failures.append(f"{requirement.path} missing term: {term}")

    if failures:
        print("Documentation completeness check failed:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Documentation completeness check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
