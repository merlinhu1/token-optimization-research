#!/usr/bin/env python3
"""Audit source snapshot metadata in tool dossiers."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOSSIER_DIR = ROOT / "docs" / "tool-dossiers"
VALID_STATUSES = {"pinned-commit", "unpinned-historical-inspection"}
COMMIT_RE = re.compile(r"[0-9a-f]{7,40}", re.IGNORECASE)


def dossier_field(text: str, field: str) -> str | None:
    match = re.search(rf"^- {re.escape(field)}:\s*(.*)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def classify(path: Path) -> tuple[str, list[str]]:
    if path.name == "README.md":
        return "index", []

    text = path.read_text(encoding="utf-8")
    status = dossier_field(text, "Snapshot status")
    commit = dossier_field(text, "Commit inspected")
    source_artifact = dossier_field(text, "Source artifact path")
    errors: list[str] = []

    if status not in VALID_STATUSES:
        errors.append("missing valid Snapshot status")
    if not source_artifact:
        errors.append("missing Source artifact path")

    if status == "pinned-commit":
        normalized_commit = (commit or "").strip().strip("`")
        if not COMMIT_RE.fullmatch(normalized_commit):
            errors.append("pinned-commit without valid Commit inspected")
    elif status == "unpinned-historical-inspection":
        if commit != "not recorded during original pass":
            errors.append("unpinned-historical-inspection without required Commit inspected disclosure")

    if errors:
        return "invalid", errors
    return status or "invalid", []


def main() -> int:
    categories: dict[str, list[str]] = {
        "pinned-commit": [],
        "unpinned-historical-inspection": [],
        "invalid": [],
        "index": [],
    }
    invalid_details: dict[str, list[str]] = {}

    for path in sorted(DOSSIER_DIR.glob("*.md")):
        category, errors = classify(path)
        categories.setdefault(category, []).append(path.name)
        if errors:
            invalid_details[path.name] = errors

    candidate_eligibility = {
        "valid_candidate_snapshot": categories["pinned-commit"],
        "invalid_candidate_versioning": categories["unpinned-historical-inspection"] + categories["invalid"],
    }
    result = {
        "counts": {key: len(value) for key, value in categories.items()},
        "candidate_eligibility_counts": {
            key: len(value) for key, value in candidate_eligibility.items()
        },
        "files": categories,
        "candidate_eligibility": candidate_eligibility,
        "invalid_details": invalid_details,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if categories["invalid"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
