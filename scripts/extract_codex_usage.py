#!/usr/bin/env python3
"""Extract normalized provider usage from Codex `--json` event streams.

Codex 0.139 emits lines such as:

    {"type":"turn.completed","usage":{"input_tokens":23720,
      "cached_input_tokens":4480,"output_tokens":5,
      "reasoning_output_tokens":0}}

The extractor preserves every raw usage block and normalizes Codex exec's
cumulative thread accounting. Codex 0.144.0 serializes `ThreadTokenUsage.total`
into each `turn.completed.usage` event, so resumed turns from the same thread
must use the final cumulative snapshot rather than summing snapshots. Final
snapshots from distinct threads are summed. `input_tokens` is total provider
input; fresh input is `input_tokens - cached_input_tokens`. Total provider
tokens are `input_tokens + output_tokens`; reasoning tokens remain a detail of
output usage.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TOKEN_KEYS = {
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "reasoning_tokens",
    "total_tokens",
}


def load_events(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    non_json_lines: list[str] = []
    for line in path.read_text(errors="replace").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            non_json_lines.append(stripped[:500])
            continue
        if isinstance(value, dict):
            events.append(value)
    return events, non_json_lines


def usage_blocks(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return raw usage blocks annotated with the active Codex thread."""
    blocks: list[dict[str, Any]] = []
    current_thread_id: str | None = None
    for event in events:
        if event.get("type") == "thread.started":
            candidate = event.get("thread_id")
            current_thread_id = candidate if isinstance(candidate, str) and candidate else None
        usage = event.get("usage")
        if isinstance(usage, dict):
            blocks.append(
                {
                    "event_type": event.get("type"),
                    "thread_id": current_thread_id,
                    "usage": usage,
                }
            )
    return blocks


def effective_usage_blocks(
    blocks: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str, list[str]]:
    """Select final cumulative usage per thread, failing on counter regressions."""
    if not blocks:
        return [], "no-usage-blocks", []
    if any(not isinstance(block.get("thread_id"), str) for block in blocks):
        warning = (
            "Usage blocks lack thread identity; retained legacy sum semantics because "
            "cumulative snapshots cannot be grouped safely."
        )
        return blocks, "legacy-sum-without-thread-identity", [warning]

    by_thread: dict[str, list[dict[str, Any]]] = {}
    thread_order: list[str] = []
    for block in blocks:
        thread_id = str(block["thread_id"])
        if thread_id not in by_thread:
            by_thread[thread_id] = []
            thread_order.append(thread_id)
        by_thread[thread_id].append(block)

    monotonic_keys = sorted(TOKEN_KEYS)
    for thread_id, thread_blocks in by_thread.items():
        previous: dict[str, Any] | None = None
        for block in thread_blocks:
            usage = block.get("usage", {})
            if not isinstance(usage, dict):
                continue
            if previous is not None:
                for key in monotonic_keys:
                    old = numeric(previous.get(key))
                    new = numeric(usage.get(key))
                    if old is not None and new is not None and new < old:
                        raise ValueError(
                            f"Codex cumulative usage decreased for thread {thread_id}: "
                            f"{key} {old} -> {new}"
                        )
            previous = usage

    return (
        [by_thread[thread_id][-1] for thread_id in thread_order],
        "final-cumulative-total-per-thread",
        [],
    )


def incremental_usage_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert cumulative per-thread snapshots into per-turn increments."""
    effective_usage_blocks(blocks)  # validates monotonic cumulative counters
    previous_by_thread: dict[str, dict[str, Any]] = {}
    increments: list[dict[str, Any]] = []
    for block in blocks:
        thread_id_value = block.get("thread_id")
        thread_id = thread_id_value if isinstance(thread_id_value, str) else None
        current = block.get("usage", {})
        if not isinstance(current, dict):
            continue
        previous = previous_by_thread.get(thread_id, {}) if thread_id is not None else {}
        delta: dict[str, int] = {}
        for key in sorted(TOKEN_KEYS):
            value = numeric(current.get(key))
            if value is None:
                continue
            prior_value = numeric(previous.get(key))
            delta[key] = value - prior_value if prior_value is not None else value
        increments.append(
            {
                "event_type": block.get("event_type"),
                "thread_id": thread_id,
                "usage": delta,
            }
        )
        if thread_id is not None:
            previous_by_thread[thread_id] = current
    return increments


def numeric(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def sum_key(blocks: list[dict[str, Any]], key: str) -> int | None:
    values = []
    for block in blocks:
        usage = block.get("usage", {})
        if isinstance(usage, dict):
            n = numeric(usage.get(key))
            if n is not None:
                values.append(n)
    return sum(values) if values else None


def token_field_totals(blocks: list[dict[str, Any]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for block in blocks:
        usage = block.get("usage", {})
        if not isinstance(usage, dict):
            continue
        for key, value in usage.items():
            number = numeric(value)
            if number is not None and "token" in str(key).lower():
                totals[str(key)] = totals.get(str(key), 0) + number
    return dict(sorted(totals.items()))


def count_tool_calls(events: list[dict[str, Any]]) -> int:
    count = 0
    for event in events:
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type") or "").lower()
        if "tool" in item_type or item_type in {"function_call", "function_call_output"}:
            count += 1
    return count


def build_summary(events_path: Path) -> dict[str, Any]:
    events, non_json_lines = load_events(events_path)
    blocks = usage_blocks(events)
    effective_blocks, accounting_mode, accounting_warnings = effective_usage_blocks(blocks)
    incremental_blocks = incremental_usage_blocks(blocks)
    input_tokens = sum_key(effective_blocks, "input_tokens")
    cached_input_tokens = sum_key(effective_blocks, "cached_input_tokens")
    output_tokens = sum_key(effective_blocks, "output_tokens")
    reasoning_tokens = sum_key(effective_blocks, "reasoning_output_tokens")
    if reasoning_tokens is None:
        reasoning_tokens = sum_key(effective_blocks, "reasoning_tokens")

    fresh_input_tokens = None
    if input_tokens is not None and cached_input_tokens is not None:
        fresh_input_tokens = max(0, input_tokens - cached_input_tokens)
    elif input_tokens is not None:
        fresh_input_tokens = input_tokens

    total_provider_tokens = None
    total_from_codex = sum_key(effective_blocks, "total_tokens")
    if total_from_codex is not None:
        total_provider_tokens = total_from_codex
    elif input_tokens is not None or output_tokens is not None:
        total_provider_tokens = (input_tokens or 0) + (output_tokens or 0)

    event_types: dict[str, int] = {}
    for event in events:
        event_type = str(event.get("type") or "unknown")
        event_types[event_type] = event_types.get(event_type, 0) + 1

    warnings = list(accounting_warnings)
    if not blocks:
        warnings.append("No usage blocks found in Codex JSONL; token fields are null.")

    return {
        "schema_version": 2,
        "source": "codex-jsonl",
        "source_artifact": str(events_path),
        "extracted_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "measurement_source": "codex-jsonl-usage-events",
        "fresh_input_tokens": fresh_input_tokens,
        "cached_input_tokens": cached_input_tokens,
        # OpenAI Codex usage exposes cached reads but no cache-write category;
        # normalize the unsupported provider component to the exact integer zero
        # required by the current compact-session contract.
        "cache_write_tokens": 0,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_provider_tokens": total_provider_tokens,
        "raw_artifact_tokens": None,
        "transformed_artifact_tokens": None,
        "codex_usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached_input_tokens,
            "output_tokens": output_tokens,
            "reasoning_output_tokens": reasoning_tokens,
            "total_tokens_formula": "input_tokens + output_tokens unless Codex emits total_tokens",
            "accounting_mode": accounting_mode,
            "source_semantics": "Codex exec turn.completed.usage serializes ThreadTokenUsage.total; fresh input subtracts cached reads.",
            "usage_blocks": blocks,
            "effective_usage_blocks": effective_blocks,
            "incremental_usage_blocks": incremental_blocks,
        },
        "provider_usage_details": {
            "runtime": "codex-cli",
            "accounting_mode": accounting_mode,
            "raw_token_field_totals": token_field_totals(effective_blocks),
            "incremental_raw_token_field_totals": token_field_totals(incremental_blocks),
            "fresh_input_formula": "input_tokens - cached_input_tokens",
            "reasoning_tokens_available": reasoning_tokens is not None,
        },
        "agent_behavior": {
            "turns": event_types.get("turn.completed"),
            "tool_calls_observed": count_tool_calls(events),
            "event_count": len(events),
            "event_types": event_types,
            "non_json_line_count": len(non_json_lines),
        },
        "warnings": warnings,
        "non_json_line_samples": non_json_lines[:10],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events_jsonl", type=Path)
    parser.add_argument("--output", "-o", type=Path, required=True)
    args = parser.parse_args(argv)

    summary = build_summary(args.events_jsonl)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    if summary["warnings"]:
        for warning in summary["warnings"]:
            print(f"warning: {warning}")
    print(json.dumps({k: summary[k] for k in ["fresh_input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens", "total_provider_tokens"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
