#!/usr/bin/env python3
"""Extract normalized provider usage from OpenCode ``run --format json`` evidence.

OpenCode emits one ``step_finish`` part per provider turn. Its token fields are
incremental: ``input`` is non-cache input, ``cache.read`` and ``cache.write``
are separate input components, ``output`` excludes hidden reasoning, and
``reasoning`` is therefore added to output for compatibility with the
repository's provider-token contract. Canonical fresh input includes both
``input`` and ``cache.write``.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

try:
    from scripts import opencode_workflow_adapter as adapter
except ImportError:
    import opencode_workflow_adapter as adapter  # type: ignore


def load_events(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    non_json: list[str] = []
    for line in path.read_text(errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            non_json.append(line[:500])
            continue
        if isinstance(value, dict):
            events.append(value)
    return events, non_json


def raw_opencode_event(event: dict[str, Any]) -> dict[str, Any] | None:
    if event.get("type") != "opencode.event":
        return None
    raw = event.get("event")
    return raw if isinstance(raw, dict) else None


def raw_token_field_totals(blocks: list[dict[str, Any]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for block in blocks:
        raw_tokens = block.get("raw_tokens")
        if not isinstance(raw_tokens, dict):
            continue
        for key, value in raw_tokens.items():
            if type(value) is int and value >= 0 and "token" in str(key).lower():
                totals[str(key)] = totals.get(str(key), 0) + value
            if key == "cache" and isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    if type(nested_value) is int and nested_value >= 0 and "token" in str(nested_key).lower():
                        path = f"cache.{nested_key}"
                        totals[path] = totals.get(path, 0) + nested_value
    return dict(sorted(totals.items()))


def build_summary(events_path: Path) -> dict[str, Any]:
    events, non_json = load_events(events_path)
    cumulative = {
        "fresh_input_tokens": 0,
        "cached_input_tokens": 0,
        "cache_write_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "total_provider_tokens": 0,
    }
    seen: set[tuple[str, str]] = set()
    raw_step_blocks: list[dict[str, Any]] = []
    tool_calls = 0
    sessions: set[str] = set()
    for outer in events:
        raw = raw_opencode_event(outer)
        if raw is None:
            continue
        session_id = raw.get("sessionID")
        if isinstance(session_id, str) and session_id:
            sessions.add(session_id)
        if raw.get("type") == "tool_use":
            tool_calls += 1
        if raw.get("type") != "step_finish":
            continue
        part = raw.get("part")
        if not isinstance(part, dict) or part.get("type") != "step-finish":
            raise ValueError("OpenCode step_finish event has an invalid part")
        part_id = part.get("id")
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("OpenCode usage event is missing session identity")
        if not isinstance(part_id, str) or not part_id:
            raise ValueError("OpenCode usage event is missing part identity")
        identity = (session_id, part_id)
        if identity in seen:
            continue
        usage = adapter.step_usage(part)
        for key in cumulative:
            cumulative[key] += usage[key]
        seen.add(identity)
        raw_step_blocks.append(
            {
                "session_id": session_id,
                "part_id": part_id,
                "usage": usage,
                "raw_tokens": part.get("tokens"),
            }
        )

    warnings: list[str] = []
    if not raw_step_blocks:
        warnings.append("No OpenCode step_finish usage blocks found; token fields are null.")
    if non_json:
        warnings.append("OpenCode JSONL contains non-JSON lines.")
    values: dict[str, int | None] = {
        key: value if raw_step_blocks else None for key, value in cumulative.items()
    }
    event_types: dict[str, int] = {}
    for outer in events:
        raw = raw_opencode_event(outer)
        name = str(raw.get("type") if raw is not None else outer.get("type") or "unknown")
        event_types[name] = event_types.get(name, 0) + 1

    return {
        "schema_version": 2,
        "source": "opencode-jsonl",
        "source_artifact": str(events_path),
        "extracted_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "measurement_source": "opencode-jsonl-step-finish-usage",
        **values,
        "raw_artifact_tokens": None,
        "transformed_artifact_tokens": None,
        "opencode_usage": {
            "accounting_mode": "sum-unique-incremental-step-finish-parts",
            "source_semantics": (
                "OpenCode step_finish tokens separate fresh input, cache reads, cache writes, "
                "visible output, and reasoning; normalized output includes reasoning."
            ),
            "session_ids": sorted(sessions),
            "unique_step_finish_parts": len(raw_step_blocks),
            "usage_blocks": raw_step_blocks,
            "total_tokens_formula": "fresh_input + cached_input + output_including_reasoning; fresh_input includes cache_write",
        },
        "provider_usage_details": {
            "runtime": "opencode-cli",
            "accounting_mode": "sum-unique-incremental-step-finish-parts",
            "raw_token_field_totals": raw_token_field_totals(raw_step_blocks),
            "fresh_input_formula": "input + cache.write",
            "reasoning_tokens_available": any(
                isinstance(block.get("raw_tokens"), dict)
                and type(block["raw_tokens"].get("reasoning")) is int
                for block in raw_step_blocks
            ),
        },
        "agent_behavior": {
            "turns": len(raw_step_blocks),
            "tool_calls_observed": tool_calls,
            "event_count": len(events),
            "event_types": event_types,
            "non_json_line_count": len(non_json),
        },
        "warnings": warnings,
        "non_json_line_samples": non_json[:10],
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
    fields = (
        "fresh_input_tokens",
        "cached_input_tokens",
        "cache_write_tokens",
        "output_tokens",
        "reasoning_tokens",
        "total_provider_tokens",
    )
    print(json.dumps({key: summary[key] for key in fields}, indent=2))
    return 1 if summary["warnings"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
