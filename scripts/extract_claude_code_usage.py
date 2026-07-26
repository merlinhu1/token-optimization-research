#!/usr/bin/env python3
"""Extract lossless provider usage from a Claude Code stream-json event file.

Claude/Anthropic reports input usage in separate dimensions:

* ``input_tokens``: non-cached input tokens;
* ``cache_creation_input_tokens`` (including nested ephemeral cache fields):
  input tokens newly written to the prompt cache;
* ``cache_read_input_tokens``: input tokens read from the prompt cache; and
* ``output_tokens``: generated output tokens.

The canonical evaluation contract calls the first two dimensions together
``fresh_input_tokens``.  ``cache_write_tokens`` remains available as an
explicit audit component, but is a subset of ``fresh_input_tokens`` and must
not be added to ``total_provider_tokens`` a second time.

Claude's assistant messages are the primary accounting source.  A final
``result`` event may summarize or aggregate a different scope, so result usage
is retained as diagnostic metadata and is only used as a clearly warned
fallback when no assistant usage exists.
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
            non_json.append(line)
            continue
        if isinstance(value, dict):
            events.append(value)
    return events, non_json


def usage_value(usage: dict[str, Any], *keys: str) -> int:
    for key in keys:
        value = usage.get(key)
        if type(value) is int and value >= 0:
            return value
    return 0


def nested_usage_value(usage: dict[str, Any], key: str) -> int:
    value = usage.get(key)
    if isinstance(value, dict):
        return sum(
            item
            for item in value.values()
            if type(item) is int and item >= 0
        )
    return usage_value(usage, key)


def cache_creation_tokens(usage: dict[str, Any]) -> int:
    """Return all cache-creation input tokens without dropping subcategories."""
    explicit = usage.get("cache_creation_input_tokens")
    if type(explicit) is int and explicit >= 0:
        # The provider's parent aggregate is authoritative for arithmetic. The
        # nested ephemeral fields remain in provider_usage_details and are
        # checked for visibility, but must not replace or double-count it.
        return explicit
    nested = usage.get("cache_creation")
    if isinstance(nested, dict):
        return sum(
            value
            for key, value in nested.items()
            if "token" in str(key).lower() and type(value) is int and value >= 0
        )
    return 0


def numeric_token_fields(value: Any, prefix: str = "") -> dict[str, int]:
    """Collect every numeric provider field whose key denotes token usage."""
    totals: dict[str, int] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if "token" in str(key).lower() and type(child) is int and child >= 0:
                totals[path] = totals.get(path, 0) + child
            elif isinstance(child, (dict, list)):
                for nested_path, nested_value in numeric_token_fields(child, path).items():
                    totals[nested_path] = totals.get(nested_path, 0) + nested_value
    elif isinstance(value, list):
        for index, child in enumerate(value):
            for nested_path, nested_value in numeric_token_fields(child, f"{prefix}[{index}]").items():
                totals[nested_path] = totals.get(nested_path, 0) + nested_value
    return totals


def usage_block(event: dict[str, Any]) -> dict[str, Any] | None:
    message = event.get("message")
    usage: Any = None
    if isinstance(message, dict) and isinstance(message.get("usage"), dict):
        usage = message["usage"]
    elif isinstance(event.get("usage"), dict):
        usage = event["usage"]
    if not isinstance(usage, dict):
        return None

    input_tokens = usage_value(usage, "input_tokens")
    cache_read = usage_value(usage, "cache_read_input_tokens", "cached_input_tokens")
    cache_write = cache_creation_tokens(usage)
    output = usage_value(usage, "output_tokens")
    reasoning = usage_value(usage, "reasoning_tokens", "reasoning_output_tokens")
    fresh = input_tokens + cache_write
    total = fresh + cache_read + output
    reported_total = usage_value(usage, "total_tokens", "total_provider_tokens")
    return {
        "input_tokens": input_tokens,
        "cache_read_input_tokens": cache_read,
        "cache_creation_input_tokens": cache_write,
        "output_tokens": output,
        "reasoning_tokens": reasoning,
        "fresh_input_tokens": fresh,
        "cached_input_tokens": cache_read,
        "cache_write_tokens": cache_write,
        "total_provider_tokens": total,
        "reported_total_tokens": reported_total if reported_total else None,
        "raw_usage": usage,
        "raw_token_fields": numeric_token_fields(usage),
        "event_type": str(event.get("type") or "unknown"),
        "message_id": message.get("id") if isinstance(message, dict) else None,
    }


def usage_blocks(events: list[dict[str, Any]], event_type: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    seen_message_ids: set[str] = set()
    for event in events:
        if event.get("type") != event_type:
            continue
        block = usage_block(event)
        if block is None:
            continue
        message_id = block.get("message_id")
        if isinstance(message_id, str) and message_id:
            if message_id in seen_message_ids:
                continue
            seen_message_ids.add(message_id)
        blocks.append(block)
    return blocks


def sum_key(blocks: list[dict[str, Any]], key: str) -> int:
    return sum(int(block.get(key) or 0) for block in blocks)


def sum_raw_token_fields(blocks: list[dict[str, Any]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for block in blocks:
        for key, value in block.get("raw_token_fields", {}).items():
            totals[key] = totals.get(key, 0) + int(value)
    return dict(sorted(totals.items()))


def reported_totals(blocks: list[dict[str, Any]]) -> int | None:
    values = [block["reported_total_tokens"] for block in blocks if block.get("reported_total_tokens") is not None]
    return sum(values) if values else None


def build_summary(events_path: Path) -> dict[str, Any]:
    events, non_json_lines = load_events(events_path)
    assistant_blocks = usage_blocks(events, "assistant")
    result_blocks = usage_blocks(events, "result")

    warnings: list[str] = []
    if assistant_blocks:
        effective_blocks = assistant_blocks
        accounting_mode = "sum-unique-assistant-message-usage"
    elif result_blocks:
        effective_blocks = result_blocks
        accounting_mode = "result-usage-fallback-no-assistant-usage"
        warnings.append(
            "No assistant usage blocks found; result usage was used only as a fallback and may be aggregated."
        )
    else:
        effective_blocks = []
        accounting_mode = "no-usage-blocks"
        warnings.append("No Claude usage blocks found; token fields are zero and not decision-ready.")

    fresh_input_tokens = sum_key(effective_blocks, "fresh_input_tokens")
    cached_input_tokens = sum_key(effective_blocks, "cached_input_tokens")
    cache_write_tokens = sum_key(effective_blocks, "cache_write_tokens")
    output_tokens = sum_key(effective_blocks, "output_tokens")
    reasoning_tokens = sum_key(effective_blocks, "reasoning_tokens")
    total_provider_tokens = fresh_input_tokens + cached_input_tokens + output_tokens

    provider_reported_total = reported_totals(effective_blocks)
    if provider_reported_total is not None and provider_reported_total != total_provider_tokens:
        warnings.append(
            "Provider-reported total_tokens differs from the normalized component total; both values are retained."
        )

    reasoning_available = any(
        "reasoning_tokens" in block.get("raw_token_fields", {})
        or "reasoning_output_tokens" in block.get("raw_token_fields", {})
        for block in effective_blocks
    )
    provider_usage_details = {
        "runtime": "claude-code",
        "accounting_mode": accounting_mode,
        "assistant_usage_block_count": len(assistant_blocks),
        "result_usage_block_count": len(result_blocks),
        "result_usage_counted": not assistant_blocks and bool(result_blocks),
        "reasoning_tokens_available": reasoning_available,
        "canonical_components": {
            "input_tokens": sum_key(effective_blocks, "input_tokens"),
            "cache_creation_input_tokens": cache_write_tokens,
            "cache_read_input_tokens": cached_input_tokens,
            "output_tokens": output_tokens,
            "reasoning_tokens": reasoning_tokens,
        },
        "raw_token_field_totals": sum_raw_token_fields(effective_blocks),
        "result_raw_token_field_totals": sum_raw_token_fields(result_blocks),
        "provider_reported_total_tokens": provider_reported_total,
        "normalized_formula": "fresh_input_tokens + cached_input_tokens + output_tokens",
        "fresh_input_formula": "input_tokens + cache_creation_input_tokens",
    }

    event_types: dict[str, int] = {}
    for event in events:
        event_type = str(event.get("type") or "unknown")
        event_types[event_type] = event_types.get(event_type, 0) + 1

    return {
        "schema_version": 3,
        "source": "claude-code-stream-json",
        "source_artifact": str(events_path),
        "extracted_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "measurement_source": "claude-code-stream-json-assistant-usage",
        "fresh_input_tokens": fresh_input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "cache_write_tokens": cache_write_tokens,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_provider_tokens": total_provider_tokens,
        "raw_artifact_tokens": None,
        "transformed_artifact_tokens": None,
        "provider_usage_details": provider_usage_details,
        "agent_behavior": {
            "turns": event_types.get("result", 0),
            "tool_calls_observed": sum(
                1
                for event in events
                if isinstance(event.get("message"), dict)
                and event["message"].get("role") == "assistant"
                and isinstance(event["message"].get("content"), list)
                and any(
                    isinstance(item, dict) and item.get("type") == "tool_use"
                    for item in event["message"]["content"]
                )
            ),
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
    print(json.dumps({key: summary[key] for key in (
        "fresh_input_tokens", "cached_input_tokens", "cache_write_tokens",
        "output_tokens", "reasoning_tokens", "total_provider_tokens",
    )}, indent=2))
    return 1 if summary["warnings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
