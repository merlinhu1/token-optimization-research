#!/usr/bin/env python3
"""Audit and correct cumulative Codex usage snapshots in retained workflows.

Historical compact bundles remain immutable. This script derives corrected
session and per-task accounting from their raw Codex JSONL events.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import extract_codex_usage

DEFAULT_OUTPUT = (
    ROOT
    / "sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json"
)
USAGE_KEYS = (
    "fresh_input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "output_tokens",
    "reasoning_tokens",
    "total_provider_tokens",
)


def read_bundle(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            artifact_path = record.get("path")
            if not isinstance(artifact_path, str) or artifact_path in records:
                raise ValueError(f"invalid or duplicate bundle path in {path}: {artifact_path!r}")
            records[artifact_path] = str(record.get("content", ""))
    return records


def parse_events(content: str) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    invalid_lines: list[str] = []
    for line in content.splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            invalid_lines.append(line[:500])
            continue
        if isinstance(value, dict):
            events.append(value)
        else:
            invalid_lines.append(line[:500])
    return events, invalid_lines


def verify_manifest(session_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for line in (session_dir / "manifest.sha256").read_text().splitlines():
        expected, relative = line.split(maxsplit=1)
        path = session_dir / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        checks.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "passed": actual == expected,
            }
        )
    return {"passed": bool(checks) and all(check["passed"] for check in checks), "checks": checks}


def summarize_blocks(blocks: list[dict[str, Any]]) -> dict[str, int | None]:
    input_tokens = extract_codex_usage.sum_key(blocks, "input_tokens")
    cached_input_tokens = extract_codex_usage.sum_key(blocks, "cached_input_tokens")
    output_tokens = extract_codex_usage.sum_key(blocks, "output_tokens")
    reasoning_tokens = extract_codex_usage.sum_key(blocks, "reasoning_output_tokens")
    if reasoning_tokens is None:
        reasoning_tokens = extract_codex_usage.sum_key(blocks, "reasoning_tokens")
    total_tokens = extract_codex_usage.sum_key(blocks, "total_tokens")
    if total_tokens is None and (input_tokens is not None or output_tokens is not None):
        total_tokens = (input_tokens or 0) + (output_tokens or 0)
    fresh_input_tokens = None
    if input_tokens is not None and cached_input_tokens is not None:
        fresh_input_tokens = input_tokens - cached_input_tokens
    elif input_tokens is not None:
        fresh_input_tokens = input_tokens
    return {
        "fresh_input_tokens": fresh_input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "cache_write_tokens": None,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_provider_tokens": total_tokens,
    }


def normalized_usage(value: dict[str, Any]) -> dict[str, Any]:
    return {key: value.get(key) for key in USAGE_KEYS}


def session_correction(session: dict[str, Any]) -> dict[str, Any]:
    session_id = str(session["session_id"])
    session_dir = ROOT / "sources/evaluations/workflow-sessions" / session_id
    bundle_path = session_dir / "evidence.jsonl.gz"
    bundle = read_bundle(bundle_path)
    events, invalid_lines = parse_events(bundle["codex-events.jsonl"])
    blocks = extract_codex_usage.usage_blocks(events)
    effective_blocks, accounting_mode, accounting_warnings = (
        extract_codex_usage.effective_usage_blocks(blocks)
    )
    incremental_blocks = extract_codex_usage.incremental_usage_blocks(blocks)
    corrected = summarize_blocks(effective_blocks)
    legacy_provider = json.loads(bundle["provider-usage.json"])
    legacy_provider_usage = normalized_usage(legacy_provider)
    legacy_registry_usage = normalized_usage(session.get("cumulative_token_usage", {}))
    if legacy_provider_usage != legacy_registry_usage:
        raise ValueError(
            f"legacy registry/provider usage mismatch for {session_id}: "
            f"{legacy_registry_usage} != {legacy_provider_usage}"
        )
    if len(blocks) != len(incremental_blocks):
        raise ValueError(f"incremental block count mismatch for {session_id}")

    task_records = sorted(session.get("per_task_results", []), key=lambda item: item["order"])
    if len(task_records) != len(incremental_blocks):
        raise ValueError(
            f"task/usage block count mismatch for {session_id}: "
            f"{len(task_records)} != {len(incremental_blocks)}"
        )
    tasks: list[dict[str, Any]] = []
    for task, cumulative, incremental in zip(task_records, blocks, incremental_blocks, strict=True):
        tasks.append(
            {
                "task_id": task["task_id"],
                "task_class": task["task_class"],
                "order": task["order"],
                "thread_id": incremental.get("thread_id"),
                "legacy_cumulative_snapshot": summarize_blocks([cumulative]),
                "corrected_incremental_usage": summarize_blocks([incremental]),
            }
        )

    expected_model_outputs = [
        f"model-output/task-{task['order']:02d}-codex-last-message.txt" for task in task_records
    ]
    missing_model_outputs = [path for path in expected_model_outputs if path not in bundle]
    legacy_total = legacy_registry_usage["total_provider_tokens"]
    corrected_total = corrected["total_provider_tokens"]
    if not isinstance(legacy_total, int) or not isinstance(corrected_total, int):
        raise ValueError(f"missing integer total for {session_id}")
    manifest = verify_manifest(session_dir)
    if not manifest["passed"]:
        raise ValueError(f"manifest failed for {session_id}")

    return {
        "session_id": session_id,
        "date": session.get("date"),
        "sequence_id": session.get("task_sequence", {}).get("sequence_id"),
        "replicate_index": session.get("replicate_index"),
        "profile_id": session.get("profile", {}).get("profile_id"),
        "model_condition_id": session.get("agent", {}).get("model_condition_id"),
        "model": session.get("agent", {}).get("model"),
        "reasoning_effort": session.get("agent", {}).get("reasoning_effort"),
        "accounting_mode": accounting_mode,
        "accounting_warnings": accounting_warnings,
        "raw_usage_block_count": len(blocks),
        "effective_usage_block_count": len(effective_blocks),
        "thread_ids": list(dict.fromkeys(block.get("thread_id") for block in blocks)),
        "legacy_registry_usage": legacy_registry_usage,
        "corrected_usage": corrected,
        "legacy_overcount_tokens": legacy_total - corrected_total,
        "legacy_inflation_factor": legacy_total / corrected_total,
        "correction_required": legacy_registry_usage != corrected,
        "tasks": tasks,
        "raw_event_diagnostics": {
            "valid_event_count": len(events),
            "invalid_or_non_object_line_count": len(invalid_lines),
            "invalid_or_non_object_line_samples": invalid_lines[:5],
            "missing_model_output_artifacts": missing_model_outputs,
        },
        "manifest": manifest,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
    rows = [session_correction(session) for session in registry["sessions"]]
    required = [row for row in rows if row["correction_required"]]
    if len(rows) != len(registry["sessions"]):
        raise ValueError("not every retained workflow session was audited")
    if any(row["accounting_mode"] != "final-cumulative-total-per-thread" for row in rows):
        raise ValueError("every retained workflow must have attributable thread-level usage")

    result = {
        "schema_version": 1,
        "evidence_through_date": max(str(row["date"]) for row in rows),
        "scope": {
            "session_count": len(rows),
            "policy": "preserve immutable compact bundles; derive final cumulative total per Codex thread",
            "legacy_defect": "scripts/extract_codex_usage.py summed cumulative turn.completed snapshots from resumed threads",
            "corrected_semantics": "select the final ThreadTokenUsage.total snapshot per thread and sum only across distinct threads",
        },
        "codex_source_evidence": {
            "installed_version": "0.144.0",
            "source_tag": "rust-v0.144.0",
            "source_commit": "767822446c7a594caa19609ca435281a9ec67e0d",
            "upstream_file": "codex-rs/exec/src/event_processor_with_jsonl_output.rs",
            "upstream_lines": "496-522",
            "observation": "ThreadTokenUsageUpdated stores notification.token_usage and TurnCompleted emits usage_from_last_total(), which reads token_usage.total",
            "upstream_url": "https://github.com/openai/codex/blob/rust-v0.144.0/codex-rs/exec/src/event_processor_with_jsonl_output.rs#L496-L522",
        },
        "integrity": {
            "audited_session_count": len(rows),
            "correction_required_count": len(required),
            "all_manifests_passed": all(row["manifest"]["passed"] for row in rows),
            "all_usage_monotonic": True,
            "all_usage_blocks_attributed_to_threads": all(
                all(isinstance(thread_id, str) for thread_id in row["thread_ids"])
                for row in rows
            ),
            "raw_compact_bundles_mutated": False,
        },
        "aggregate": {
            "legacy_total_provider_tokens": sum(
                row["legacy_registry_usage"]["total_provider_tokens"] for row in rows
            ),
            "corrected_total_provider_tokens": sum(
                row["corrected_usage"]["total_provider_tokens"] for row in rows
            ),
            "legacy_overcount_tokens": sum(row["legacy_overcount_tokens"] for row in rows),
            "by_profile_id": {
                profile_id: {
                    "session_count": sum(row["profile_id"] == profile_id for row in rows),
                    "legacy_total_provider_tokens": sum(
                        row["legacy_registry_usage"]["total_provider_tokens"]
                        for row in rows
                        if row["profile_id"] == profile_id
                    ),
                    "corrected_total_provider_tokens": sum(
                        row["corrected_usage"]["total_provider_tokens"]
                        for row in rows
                        if row["profile_id"] == profile_id
                    ),
                }
                for profile_id in sorted({str(row["profile_id"]) for row in rows})
            },
            "by_model_condition_id": {
                condition_id: {
                    "session_count": sum(
                        row["model_condition_id"] == condition_id for row in rows
                    ),
                    "legacy_total_provider_tokens": sum(
                        row["legacy_registry_usage"]["total_provider_tokens"]
                        for row in rows
                        if row["model_condition_id"] == condition_id
                    ),
                    "corrected_total_provider_tokens": sum(
                        row["corrected_usage"]["total_provider_tokens"]
                        for row in rows
                        if row["model_condition_id"] == condition_id
                    ),
                }
                for condition_id in sorted(
                    {str(row["model_condition_id"]) for row in rows}
                )
            },
        },
        "sessions": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sessions": len(rows),
                "corrections": len(required),
                "legacy_total": result["aggregate"]["legacy_total_provider_tokens"],
                "corrected_total": result["aggregate"]["corrected_total_provider_tokens"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
