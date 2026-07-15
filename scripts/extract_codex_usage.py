#!/usr/bin/env python3
"""Extract normalized provider usage from Codex `--json` event streams.

Codex 0.139 emits lines such as:

    {"type":"turn.completed","usage":{"input_tokens":23720,
      "cached_input_tokens":4480,"output_tokens":5,
      "reasoning_output_tokens":0}}

The extractor preserves raw usage blocks and writes the repository's normalized
fields. `input_tokens` is treated as total provider input; fresh input is
`input_tokens - cached_input_tokens` when both are available. Total provider
tokens are computed as `input_tokens + output_tokens`; reasoning tokens are
reported separately because Codex exposes them as a detail of output usage.
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
    blocks: list[dict[str, Any]] = []
    for event in events:
        usage = event.get("usage")
        if isinstance(usage, dict):
            blocks.append({"event_type": event.get("type"), "usage": usage})
    return blocks


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
    input_tokens = sum_key(blocks, "input_tokens")
    cached_input_tokens = sum_key(blocks, "cached_input_tokens")
    output_tokens = sum_key(blocks, "output_tokens")
    reasoning_tokens = sum_key(blocks, "reasoning_output_tokens")
    if reasoning_tokens is None:
        reasoning_tokens = sum_key(blocks, "reasoning_tokens")

    fresh_input_tokens = None
    if input_tokens is not None and cached_input_tokens is not None:
        fresh_input_tokens = max(0, input_tokens - cached_input_tokens)
    elif input_tokens is not None:
        fresh_input_tokens = input_tokens

    total_provider_tokens = None
    total_from_codex = sum_key(blocks, "total_tokens")
    if total_from_codex is not None:
        total_provider_tokens = total_from_codex
    elif input_tokens is not None or output_tokens is not None:
        total_provider_tokens = (input_tokens or 0) + (output_tokens or 0)

    event_types: dict[str, int] = {}
    for event in events:
        event_type = str(event.get("type") or "unknown")
        event_types[event_type] = event_types.get(event_type, 0) + 1

    return {
        "schema_version": 1,
        "source": "codex-jsonl",
        "source_artifact": str(events_path),
        "extracted_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "measurement_source": "codex-jsonl-usage-events",
        "fresh_input_tokens": fresh_input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "cache_write_tokens": None,
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
            "usage_blocks": blocks,
        },
        "agent_behavior": {
            "turns": event_types.get("turn.completed"),
            "tool_calls_observed": count_tool_calls(events),
            "event_count": len(events),
            "event_types": event_types,
            "non_json_line_count": len(non_json_lines),
        },
        "warnings": [
            "No usage blocks found in Codex JSONL; token fields are null."
        ]
        if not blocks
        else [],
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
