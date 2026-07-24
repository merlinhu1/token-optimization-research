#!/usr/bin/env python3
"""Extract provider-token usage from Claude Code ``--output-format stream-json``.

Claude Code emits an ``assistant`` event for each provider message and a final
``result`` event for the turn. The assistant message usage blocks are the
accounting source because the final result can be cumulative or model-aggregated
and must not be added a second time. Thinking-token detail is not exposed by the
CLI usage object, so reasoning_tokens is explicitly zero rather than inferred.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any


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


def nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"Claude Code usage {field} must be a non-negative integer")
    return value


def usage_block(message: dict[str, Any], event_index: int) -> dict[str, Any] | None:
    usage = message.get("usage")
    if not isinstance(usage, dict):
        return None
    fresh = nonnegative_int(usage.get("input_tokens", 0), "input_tokens")
    cached = nonnegative_int(usage.get("cache_read_input_tokens", 0), "cache_read_input_tokens")
    cache_creation = usage.get("cache_creation")
    if isinstance(cache_creation, dict):
        cache_write = sum(
            nonnegative_int(cache_creation.get(key, 0), f"cache_creation.{key}")
            for key in ("ephemeral_5m_input_tokens", "ephemeral_1h_input_tokens")
        )
    else:
        cache_write = nonnegative_int(usage.get("cache_creation_input_tokens", 0), "cache_creation_input_tokens")
    output = nonnegative_int(usage.get("output_tokens", 0), "output_tokens")
    return {
        "event_index": event_index,
        "message_id": str(message.get("id") or f"assistant-event-{event_index}"),
        "usage": {
            "fresh_input_tokens": fresh,
            "cached_input_tokens": cached,
            "cache_write_tokens": cache_write,
            "output_tokens": output,
            "reasoning_tokens": 0,
            "total_provider_tokens": fresh + cached + cache_write + output,
        },
        "raw_usage": usage,
    }


def build_summary(events_path: Path) -> dict[str, Any]:
    events, non_json = load_events(events_path)
    blocks: list[dict[str, Any]] = []
    seen: set[str] = set()
    sessions: set[str] = set()
    event_types: dict[str, int] = {}
    tool_calls = 0
    result_events: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        kind = str(event.get("type") or "unknown")
        event_types[kind] = event_types.get(kind, 0) + 1
        session_id = event.get("session_id")
        if isinstance(session_id, str) and session_id:
            sessions.add(session_id)
        if kind == "assistant":
            message = event.get("message")
            if isinstance(message, dict):
                block = usage_block(message, index)
                if block is not None and block["message_id"] not in seen:
                    blocks.append(block)
                    seen.add(block["message_id"])
                content = message.get("content")
                if isinstance(content, list):
                    tool_calls += sum(
                        isinstance(item, dict) and item.get("type") == "tool_use"
                        for item in content
                    )
        elif kind == "result":
            result_events.append(event)

    cumulative = {
        "fresh_input_tokens": sum(item["usage"]["fresh_input_tokens"] for item in blocks),
        "cached_input_tokens": sum(item["usage"]["cached_input_tokens"] for item in blocks),
        "cache_write_tokens": sum(item["usage"]["cache_write_tokens"] for item in blocks),
        "output_tokens": sum(item["usage"]["output_tokens"] for item in blocks),
        "reasoning_tokens": 0,
        "total_provider_tokens": sum(item["usage"]["total_provider_tokens"] for item in blocks),
    }
    warnings: list[str] = []
    if not blocks:
        warnings.append("No Claude Code assistant usage blocks found; token fields are null.")
    if non_json:
        warnings.append("Claude Code stream-json contains non-JSON lines.")
    failed = [event for event in result_events if event.get("is_error") is True or event.get("subtype") == "error"]
    if failed:
        warnings.append("Claude Code emitted an error result event.")
    values: dict[str, int | None] = {
        key: value if blocks else None for key, value in cumulative.items()
    }
    return {
        "schema_version": 1,
        "source": "claude-code-stream-json",
        "source_artifact": str(events_path),
        "extracted_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "measurement_source": "claude-code-stream-json-assistant-usage",
        **values,
        "raw_artifact_tokens": None,
        "transformed_artifact_tokens": None,
        "claude_code_usage": {
            "accounting_mode": "sum-unique-assistant-message-usage",
            "source_semantics": "Claude Code assistant message usage is summed once per unique message id; final result/modelUsage is metadata only.",
            "session_ids": sorted(sessions),
            "assistant_usage_blocks": blocks,
            "result_event_count": len(result_events),
            "reasoning_tokens_available": False,
        },
        "agent_behavior": {
            "turns": len(blocks),
            "tool_calls_observed": tool_calls,
            "event_count": len(events),
            "event_types": event_types,
            "non_json_line_count": len(non_json),
            "result_events": [
                {
                    "subtype": event.get("subtype"),
                    "is_error": event.get("is_error"),
                    "stop_reason": event.get("stop_reason"),
                    "num_turns": event.get("num_turns"),
                    "model_usage_present": bool(event.get("modelUsage")),
                }
                for event in result_events
            ],
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
    print(json.dumps({key: summary[key] for key in (
        "fresh_input_tokens", "cached_input_tokens", "cache_write_tokens",
        "output_tokens", "reasoning_tokens", "total_provider_tokens",
    )}, indent=2))
    return 1 if summary["warnings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
