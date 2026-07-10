#!/usr/bin/env python3
"""Audit experiment artifacts against a run record's tool manifest.

The audit accepts one or more transcript/artifact files. Official runs should
include the model event stream plus environment-preflight artifacts such as
`codex-mcp-list.txt`, effective config, and rendered prompt snippets. A run is
excluded if any forbidden surface appears in artifacts for a profile that did not
explicitly allow that surface.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_FORBIDDEN = [
    "lean-ctx",
    "mcp_lean_ctx",
    "ctx_read",
    "ctx_search",
    "ctx_shell",
    "ctx_graph",
    "codegraph",
    "serena",
    "rtk",
    "ponytail",
    "lowfat",
    "tokenjuice",
    "repomix",
    "mex",
    "cavemem",
    "cartog",
    "ponytail",
    "caveman",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def forbidden_for(record: dict[str, Any]) -> tuple[list[str], set[str]]:
    setup = record.get("setup", {})
    perms = setup.get("tool_permissions", {})
    if isinstance(perms, list):
        perms = {}
    forbidden = sorted(set(DEFAULT_FORBIDDEN) | set(perms.get("forbidden_tools") or []))
    allowed = set(perms.get("allowed_token_saving_tools") or [])
    return forbidden, allowed


def forbidden_pattern(term: str) -> re.Pattern[str]:
    # Avoid false positives for short tool names embedded in code symbols, e.g.
    # `mex` inside Django's `JSONExact`. Hyphen/underscore are treated as token
    # characters because many forbidden tool surfaces use them.
    return re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(term)}(?![A-Za-z0-9_-])", re.IGNORECASE)


def scan_file(path: Path, forbidden: list[str], allowed: set[str]) -> list[dict[str, str]]:
    text = path.read_text(errors="replace") if path.exists() else ""
    hits: list[dict[str, str]] = []
    for term in forbidden:
        if term in allowed:
            continue
        pattern = forbidden_pattern(term)
        match = pattern.search(text)
        if match:
            start = max(0, match.start() - 80)
            end = min(len(text), match.end() + 80)
            snippet = text[start:end].replace("\n", " ")
            hits.append({"term": term, "artifact": str(path), "snippet": snippet})
    return hits


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, help="write machine-readable audit result")
    parser.add_argument("run_record", type=Path)
    parser.add_argument("artifacts", nargs="+")
    args = parser.parse_args(argv)

    run_record = load_json(args.run_record)
    forbidden, allowed = forbidden_for(run_record)
    hits: list[dict[str, str]] = []
    missing: list[str] = []
    for artifact_text in args.artifacts:
        artifact = Path(artifact_text)
        if not artifact.exists():
            missing.append(str(artifact))
            continue
        hits.extend(scan_file(artifact, forbidden, allowed))

    result = {
        "passed": not hits and not missing,
        "run_record": str(args.run_record),
        "artifacts_scanned": [str(Path(p)) for p in args.artifacts if Path(p).exists()],
        "missing_artifacts": missing,
        "forbidden_tool_hits": hits,
        "allowed_token_saving_tools": sorted(allowed),
    }
    if args.json_output:
        args.json_output.write_text(json.dumps(result, indent=2) + "\n")

    if missing:
        print("TOOL ISOLATION FAILED")
        print("missing required artifacts:")
        for artifact in missing:
            print(f"- {artifact}")
        return 1
    if hits:
        print("TOOL ISOLATION FAILED")
        print("forbidden terms:", ", ".join(sorted({hit["term"] for hit in hits})))
        for hit in hits[:20]:
            print(f"- {hit['term']} in {hit['artifact']}: {hit['snippet']}")
        return 1
    print("tool isolation audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
