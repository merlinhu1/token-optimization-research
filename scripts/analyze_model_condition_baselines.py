#!/usr/bin/env python3
"""Analyze accepted persistent baseline replicates across two model conditions."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import statistics
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SESSIONS = ROOT / "data/workflow-sessions.json"
DEFAULT_OUTPUT = ROOT / "sources/evaluations/audits/gpt-5-6-sol-high-baseline-variance-20260718.json"
CONDITIONS = (
    "codex-openai-gpt-5-6-luna-xhigh",
    "codex-openai-gpt-5-6-sol-high",
)
SEQUENCES = (
    "fastify-lifecycle-sequence-v0",
    "beets-lifecycle-sequence-v0",
    "terraform-lifecycle-sequence-v0",
)
REPLICATES = (0, 1, 2)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sample_stats(values: list[int | float]) -> dict[str, Any]:
    if not values:
        raise ValueError("sample_stats requires values")
    floats = [float(value) for value in values]
    mean = statistics.fmean(floats)
    sd = statistics.stdev(floats) if len(floats) > 1 else 0.0
    logs = [math.log(value) for value in floats] if all(value > 0 for value in floats) else []
    return {
        "n": len(floats),
        "values": values,
        "mean": mean,
        "median": statistics.median(floats),
        "sample_standard_deviation": sd,
        "coefficient_of_variation": sd / mean if mean else None,
        "minimum": min(floats),
        "maximum": max(floats),
        "range": max(floats) - min(floats),
        "geometric_mean": math.exp(statistics.fmean(logs)) if logs else None,
        "sample_log_standard_deviation": (
            statistics.stdev(logs) if len(logs) > 1 else (0.0 if logs else None)
        ),
    }


def verify_manifest(session_dir: Path) -> dict[str, Any]:
    manifest = session_dir / "manifest.sha256"
    checks = []
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        expected, relative = raw.split(maxsplit=1)
        target = session_dir / relative.strip()
        actual = sha256(target)
        checks.append({
            "path": str(target.relative_to(ROOT)),
            "expected_sha256": expected,
            "actual_sha256": actual,
            "passed": actual == expected,
        })
    return {
        "manifest": str(manifest.relative_to(ROOT)),
        "checks": checks,
        "passed": bool(checks) and all(item["passed"] for item in checks),
    }


def read_bundle(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            records[str(record["path"])] = str(record.get("content", ""))
    return records


def validate_nested_artifacts(bundle: dict[str, str]) -> dict[str, Any]:
    checks = []
    for path, content in sorted(bundle.items()):
        suffix = Path(path).suffix.lower()
        if suffix == ".json":
            try:
                parsed = json.loads(content)
                checks.append({
                    "path": path,
                    "format": "json",
                    "passed": True,
                    "logical_record_count": len(parsed) if isinstance(parsed, (list, dict)) else 1,
                    "invalid_line_count": 0,
                })
            except json.JSONDecodeError as exc:
                checks.append({
                    "path": path,
                    "format": "json",
                    "passed": False,
                    "logical_record_count": 0,
                    "invalid_line_count": 1,
                    "error": str(exc),
                })
        elif suffix == ".jsonl":
            valid = 0
            invalid = []
            for line_number, line in enumerate(content.splitlines(), 1):
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError as exc:
                    invalid.append({"line": line_number, "error": str(exc)})
                    continue
                if not isinstance(parsed, dict):
                    invalid.append({"line": line_number, "error": "event record is not an object"})
                    continue
                valid += 1
            checks.append({
                "path": path,
                "format": "jsonl",
                "passed": not invalid,
                "logical_record_count": valid,
                "invalid_line_count": len(invalid),
                "invalid_line_samples": invalid[:5],
            })
        elif suffix == ".toml":
            try:
                parsed = tomllib.loads(content)
                checks.append({
                    "path": path,
                    "format": "toml",
                    "passed": True,
                    "logical_record_count": len(parsed),
                    "invalid_line_count": 0,
                })
            except tomllib.TOMLDecodeError as exc:
                checks.append({
                    "path": path,
                    "format": "toml",
                    "passed": False,
                    "logical_record_count": 0,
                    "invalid_line_count": 1,
                    "error": str(exc),
                })
    return {
        "artifact_count": len(checks),
        "passed_artifact_count": sum(item["passed"] for item in checks),
        "invalid_artifact_count": sum(not item["passed"] for item in checks),
        "invalid_line_count": sum(item["invalid_line_count"] for item in checks),
        "all_passed": all(item["passed"] for item in checks),
        "checks": checks,
    }


def trajectory_metrics(bundle: dict[str, str]) -> tuple[dict[str, Any], dict[str, Any]]:
    provider = json.loads(bundle["provider-usage.json"])
    item_types: Counter[str] = Counter()
    command_failures = 0
    parsed_event_count = 0
    unparsed_event_line_count = 0
    for line in bundle["codex-events.jsonl"].splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            unparsed_event_line_count += 1
            continue
        if not isinstance(event, dict):
            unparsed_event_line_count += 1
            continue
        parsed_event_count += 1
        if event.get("type") != "item.completed":
            continue
        item = event.get("item", {})
        item_type = str(item.get("type", "unknown"))
        item_types[item_type] += 1
        if item_type == "command_execution" and item.get("exit_code") not in (0, None):
            command_failures += 1
    behavior = provider.get("agent_behavior", {})
    trajectory = {
        "turns": int(behavior.get("turns", 0)),
        "provider_event_count": int(behavior.get("event_count", 0)),
        "provider_tool_calls_observed": int(behavior.get("tool_calls_observed", 0)),
        "provider_non_json_line_count": int(behavior.get("non_json_line_count", 0)),
        "parsed_event_count": parsed_event_count,
        "unparsed_event_line_count": unparsed_event_line_count,
        "completed_item_types": dict(sorted(item_types.items())),
        "native_command_executions": item_types.get("command_execution", 0),
        "native_command_failures": command_failures,
        "file_change_items": item_types.get("file_change", 0),
        "agent_message_items": item_types.get("agent_message", 0),
        "todo_list_items": item_types.get("todo_list", 0),
    }
    return provider, trajectory


def eligible(session: dict[str, Any]) -> bool:
    return (
        session.get("session_role") == "baseline"
        and session.get("status") == "completed"
        and session.get("interpretation", {}).get("accepted_for_objective") is True
        and session.get("interpretation", {}).get("evaluation_validity") == "valid"
        and session.get("agent", {}).get("model_condition_id") in CONDITIONS
        and session.get("task_sequence", {}).get("sequence_id") in SEQUENCES
        and session.get("replicate_index") in REPLICATES
    )


def session_row(session: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    bundle_path = ROOT / session["artifacts"]["evidence_bundle"]
    bundle = read_bundle(bundle_path)
    nested_artifact_validation = validate_nested_artifacts(bundle)
    provider, trajectory = trajectory_metrics(bundle)
    tasks = []
    usage_blocks = provider.get("codex_usage", {}).get("usage_blocks", [])
    task_results = sorted(session["per_task_results"], key=lambda item: item["order"])
    if len(usage_blocks) != len(task_results):
        raise ValueError(f"usage block/task mismatch for {session['session_id']}")
    for result, block in zip(task_results, usage_blocks, strict=True):
        usage = block["usage"]
        input_tokens = int(usage["input_tokens"])
        cached = int(usage["cached_input_tokens"])
        output = int(usage["output_tokens"])
        tasks.append({
            "task_id": result["task_id"],
            "task_class": result["task_class"],
            "order": result["order"],
            "fresh_input_tokens": input_tokens - cached,
            "cached_input_tokens": cached,
            "output_tokens": output,
            "reasoning_tokens": int(usage["reasoning_output_tokens"]),
            "total_provider_tokens": input_tokens + output,
            "operational_retry_count": int(result.get("operational_retry_count", 0)),
            "codex_exit_code": result.get("codex_exit_code"),
            "verifier_passed": result.get("verifier_passed"),
        })
    cumulative = session["cumulative_token_usage"]
    if sum(task["total_provider_tokens"] for task in tasks) != cumulative["total_provider_tokens"]:
        raise ValueError(f"task totals do not reconcile for {session['session_id']}")
    row = {
        "session_id": session["session_id"],
        "date": session["date"],
        "sequence_id": session["task_sequence"]["sequence_id"],
        "replicate_index": session["replicate_index"],
        "model_condition_id": session["agent"]["model_condition_id"],
        "model": session["agent"]["model"],
        "reasoning_effort": session["agent"]["reasoning_effort"],
        "codex_version": session["agent"]["version"],
        "profile_id": session["profile"]["profile_id"],
        "docker_image_id": session["docker_image_identity"]["image_id"],
        "fixture_runner_sha256": session["selected_execution"]["descriptor"]["runtime"]["fixture_runner_sha256"],
        "prompt_hashes": [
            item["rendered_prompt_sha256"]
            for item in session["selected_execution"]["descriptor"]["model_facing_prompts"]["tasks"]
        ],
        "protocol_fingerprint": session["baseline_pool"]["protocol_fingerprint"],
        "tokens": {
            "fresh_input_tokens": cumulative["fresh_input_tokens"],
            "cached_input_tokens": cumulative["cached_input_tokens"],
            "output_tokens": cumulative["output_tokens"],
            "reasoning_tokens": cumulative["reasoning_tokens"],
            "total_provider_tokens": cumulative["total_provider_tokens"],
        },
        "tasks": tasks,
        "trajectory": trajectory,
        "operational_retry_count": sum(task["operational_retry_count"] for task in tasks),
        "tasks_passed": session["software_quality"]["tasks_passed"],
        "final_verifier_passed": session["software_quality"]["final_verifier_passed"],
        "execution_integrity": session["execution_integrity"],
        "nested_artifact_validation": nested_artifact_validation,
    }
    session_dir = ROOT / Path(session["artifacts"]["manifest"]).parent
    return row, verify_manifest(session_dir)


def summarize_condition(rows: list[dict[str, Any]]) -> dict[str, Any]:
    token_fields = (
        "fresh_input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "reasoning_tokens",
        "total_provider_tokens",
    )
    component_totals = {
        field: sum(row["tokens"][field] for row in rows)
        for field in token_fields
    }
    total = component_totals["total_provider_tokens"]
    sequence_stats = {}
    for sequence in SEQUENCES:
        selected = sorted(
            (row for row in rows if row["sequence_id"] == sequence),
            key=lambda row: row["replicate_index"],
        )
        sequence_stats[sequence] = {
            "total_provider_tokens": sample_stats([row["tokens"]["total_provider_tokens"] for row in selected]),
            "fresh_input_tokens": sample_stats([row["tokens"]["fresh_input_tokens"] for row in selected]),
            "cached_input_tokens": sample_stats([row["tokens"]["cached_input_tokens"] for row in selected]),
            "output_tokens": sample_stats([row["tokens"]["output_tokens"] for row in selected]),
            "reasoning_tokens": sample_stats([row["tokens"]["reasoning_tokens"] for row in selected]),
            "trajectory": {
                metric: sample_stats([row["trajectory"][metric] for row in selected])
                for metric in (
                    "provider_event_count",
                    "provider_tool_calls_observed",
                    "native_command_executions",
                    "native_command_failures",
                    "file_change_items",
                    "agent_message_items",
                )
            },
        }
    aggregate_by_replicate = []
    for replicate in REPLICATES:
        selected = [row for row in rows if row["replicate_index"] == replicate]
        aggregate_by_replicate.append({
            "replicate_index": replicate,
            **{
                field: sum(row["tokens"][field] for row in selected)
                for field in token_fields
            },
            "native_command_executions": sum(row["trajectory"]["native_command_executions"] for row in selected),
            "provider_event_count": sum(row["trajectory"]["provider_event_count"] for row in selected),
        })
    task_class_stats = {}
    all_tasks = [task for row in rows for task in row["tasks"]]
    for task_class in sorted({task["task_class"] for task in all_tasks}):
        selected = [task for task in all_tasks if task["task_class"] == task_class]
        task_class_stats[task_class] = {
            "total_provider_tokens": sample_stats([task["total_provider_tokens"] for task in selected]),
            "fresh_input_tokens": sample_stats([task["fresh_input_tokens"] for task in selected]),
            "cached_input_tokens": sample_stats([task["cached_input_tokens"] for task in selected]),
            "output_tokens": sample_stats([task["output_tokens"] for task in selected]),
            "reasoning_tokens": sample_stats([task["reasoning_tokens"] for task in selected]),
        }
    return {
        "session_count": len(rows),
        "component_totals": component_totals,
        "component_shares": {
            "fresh_input_share_of_total": component_totals["fresh_input_tokens"] / total,
            "cached_input_share_of_total": component_totals["cached_input_tokens"] / total,
            "output_share_of_total": component_totals["output_tokens"] / total,
            "reasoning_share_of_output": component_totals["reasoning_tokens"] / component_totals["output_tokens"],
        },
        "sequence_stats": sequence_stats,
        "aggregate_by_replicate": aggregate_by_replicate,
        "aggregate_total_provider_tokens": sample_stats(
            [item["total_provider_tokens"] for item in aggregate_by_replicate]
        ),
        "task_class_stats": task_class_stats,
        "trajectory_totals": {
            metric: sum(row["trajectory"][metric] for row in rows)
            for metric in (
                "provider_event_count",
                "provider_tool_calls_observed",
                "provider_non_json_line_count",
                "native_command_executions",
                "native_command_failures",
                "file_change_items",
                "agent_message_items",
                "todo_list_items",
            )
        },
        "operational_retry_count": sum(row["operational_retry_count"] for row in rows),
        "tasks_passed": sum(row["tasks_passed"] for row in rows),
        "final_verifiers_passed": sum(bool(row["final_verifier_passed"]) for row in rows),
    }


def paired_comparison(by_key: dict[tuple[str, int, str], dict[str, Any]]) -> dict[str, Any]:
    luna, sol = CONDITIONS
    fields = (
        "fresh_input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "reasoning_tokens",
        "total_provider_tokens",
    )
    per_sequence = {}
    for sequence in SEQUENCES:
        pairs = []
        for replicate in REPLICATES:
            old = by_key[(sequence, replicate, luna)]
            new = by_key[(sequence, replicate, sol)]
            pairs.append({
                "replicate_index": replicate,
                **{
                    field: {
                        "luna_xhigh": old["tokens"][field],
                        "sol_high": new["tokens"][field],
                        "ratio_sol_over_luna": new["tokens"][field] / old["tokens"][field],
                        "percent_change": (new["tokens"][field] / old["tokens"][field] - 1) * 100,
                    }
                    for field in fields
                },
                "native_command_executions": {
                    "luna_xhigh": old["trajectory"]["native_command_executions"],
                    "sol_high": new["trajectory"]["native_command_executions"],
                    "ratio_sol_over_luna": (
                        new["trajectory"]["native_command_executions"]
                        / old["trajectory"]["native_command_executions"]
                    ),
                },
            })
        total_ratios = [pair["total_provider_tokens"]["ratio_sol_over_luna"] for pair in pairs]
        per_sequence[sequence] = {
            "pairs": pairs,
            "total_provider_tokens_ratio": sample_stats(total_ratios),
            "geometric_mean_percent_change": (math.exp(statistics.fmean(math.log(x) for x in total_ratios)) - 1) * 100,
        }
    aggregate_pairs = []
    for replicate in REPLICATES:
        old_rows = [by_key[(sequence, replicate, luna)] for sequence in SEQUENCES]
        new_rows = [by_key[(sequence, replicate, sol)] for sequence in SEQUENCES]
        old_total = sum(row["tokens"]["total_provider_tokens"] for row in old_rows)
        new_total = sum(row["tokens"]["total_provider_tokens"] for row in new_rows)
        aggregate_pairs.append({
            "replicate_index": replicate,
            "luna_xhigh_total_provider_tokens": old_total,
            "sol_high_total_provider_tokens": new_total,
            "ratio_sol_over_luna": new_total / old_total,
            "percent_change": (new_total / old_total - 1) * 100,
        })
    aggregate_ratios = [item["ratio_sol_over_luna"] for item in aggregate_pairs]
    return {
        "per_sequence": per_sequence,
        "aggregate_pairs": aggregate_pairs,
        "aggregate_ratio": sample_stats(aggregate_ratios),
        "aggregate_geometric_mean_percent_change": (
            math.exp(statistics.fmean(math.log(x) for x in aggregate_ratios)) - 1
        ) * 100,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    records = json.loads(SESSIONS.read_text(encoding="utf-8"))["sessions"]
    selected = [session for session in records if eligible(session)]
    rows = []
    manifests = []
    for session in selected:
        row, manifest = session_row(session)
        rows.append(row)
        manifests.append(manifest)
    by_key = {
        (row["sequence_id"], row["replicate_index"], row["model_condition_id"]): row
        for row in rows
    }
    expected_keys = {
        (sequence, replicate, condition)
        for sequence in SEQUENCES
        for replicate in REPLICATES
        for condition in CONDITIONS
    }
    if set(by_key) != expected_keys or len(rows) != len(expected_keys):
        missing = sorted(expected_keys - set(by_key))
        extra = sorted(set(by_key) - expected_keys)
        raise SystemExit(f"analysis panel mismatch: missing={missing} extra={extra} rows={len(rows)}")
    if not all(manifest["passed"] for manifest in manifests):
        raise SystemExit("artifact manifest verification failed")
    condition_summaries = {
        condition: summarize_condition([row for row in rows if row["model_condition_id"] == condition])
        for condition in CONDITIONS
    }
    matched_control_checks = []
    for sequence in SEQUENCES:
        for replicate in REPLICATES:
            old = by_key[(sequence, replicate, CONDITIONS[0])]
            new = by_key[(sequence, replicate, CONDITIONS[1])]
            checks = {
                "sequence_id": old["sequence_id"] == new["sequence_id"],
                "replicate_index": old["replicate_index"] == new["replicate_index"],
                "profile_id": old["profile_id"] == new["profile_id"],
                "docker_image_id": old["docker_image_id"] == new["docker_image_id"],
                "codex_version": old["codex_version"] == new["codex_version"],
                "fixture_runner_sha256": old["fixture_runner_sha256"] == new["fixture_runner_sha256"],
                "prompt_hashes": old["prompt_hashes"] == new["prompt_hashes"],
            }
            matched_control_checks.append({
                "sequence_id": sequence,
                "replicate_index": replicate,
                "checks": checks,
                "passed": all(checks.values()),
            })
    result = {
        "schema_version": 1,
        "evidence_through_date": max(row["date"] for row in rows),
        "scope": {
            "evidence_stage": "descriptive-model-condition-screen",
            "workflow_unit": "persistent three-task lifecycle-v0 session",
            "conditions": list(CONDITIONS),
            "sequences": list(SEQUENCES),
            "replicates": list(REPLICATES),
            "primary_metric": "total_provider_tokens including cached input",
            "reasoning_token_note": "reasoning_tokens are a reported subset of output_tokens, not an additive component",
        },
        "integrity": {
            "selected_session_count": len(rows),
            "session_count_by_condition": dict(Counter(row["model_condition_id"] for row in rows)),
            "manifest_count": len(manifests),
            "manifest_file_check_count": sum(len(item["checks"]) for item in manifests),
            "all_manifests_passed": all(item["passed"] for item in manifests),
            "manifests": manifests,
            "nested_artifact_count": sum(
                row["nested_artifact_validation"]["artifact_count"] for row in rows
            ),
            "nested_invalid_artifact_count": sum(
                row["nested_artifact_validation"]["invalid_artifact_count"] for row in rows
            ),
            "nested_invalid_line_count": sum(
                row["nested_artifact_validation"]["invalid_line_count"] for row in rows
            ),
            "all_nested_artifacts_parse_strictly": all(
                row["nested_artifact_validation"]["all_passed"] for row in rows
            ),
            "all_sessions_completed": all(row["final_verifier_passed"] for row in rows),
            "all_execution_integrity_passed": all(
                row["execution_integrity"]["verifier_integrity_passed"]
                and row["execution_integrity"]["tool_isolation_audit_passed"]
                and not row["execution_integrity"]["external_retrieval_hits"]
                for row in rows
            ),
            "matched_control_checks": matched_control_checks,
            "all_matched_controls_equal": all(item["passed"] for item in matched_control_checks),
        },
        "sessions": sorted(rows, key=lambda row: (row["model_condition_id"], row["sequence_id"], row["replicate_index"])),
        "condition_summaries": condition_summaries,
        "paired_comparison": paired_comparison(by_key),
        "limitations": [
            "Three replicates per sequence support descriptive variance comparison only.",
            "The compound condition changes both model (Luna to Sol) and reasoning effort (xhigh to high).",
            "The Luna sessions were collected on 2026-07-16 and the Sol sessions on 2026-07-18, so collection time is not blocked or randomized.",
            "Provider event item counts describe trajectories but are post-treatment mechanisms and are not adjusted out of the primary token outcome.",
            "Compact bundle manifests pass, but some embedded Codex JSONL event streams contain raw stderr or non-object lines and therefore are not strictly parseable line by line.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "selected_sessions": len(rows),
        "all_manifests_passed": result["integrity"]["all_manifests_passed"],
        "all_matched_controls_equal": result["integrity"]["all_matched_controls_equal"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
