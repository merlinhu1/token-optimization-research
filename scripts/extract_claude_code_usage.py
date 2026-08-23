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

try:
    from scripts.token_metrics import (
        AGENT_STEP_DEFINITION,
        WEIGHTED_TOKEN_COST_FORMULA,
        weighted_token_cost,
        weighted_token_cost_per_step,
    )
except ImportError:
    from token_metrics import (
        AGENT_STEP_DEFINITION,
        WEIGHTED_TOKEN_COST_FORMULA,
        weighted_token_cost,
        weighted_token_cost_per_step,
    )


def agent_step_type_counts(events: list[dict[str, Any]]) -> dict[str, int]:
    """Count completed agent items in a Claude Code stream.

    An item is an assistant text block or a tool invocation. thinking blocks are not items and
    tool_result blocks are the environment answering rather than the agent acting, so counting
    either would measure something other than the trajectory. ADR 0008 needs the step factor from
    every runtime; the granularity is this runtime's own, so the definition travels with the count
    and per-step figures compare replicates of one runtime rather than one runtime against another.
    """
    counts: dict[str, int] = {}
    for event in events:
        message = event.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        for block in message.get("content") or []:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type in {"text", "tool_use"}:
                counts[str(block_type)] = counts.get(str(block_type), 0) + 1
    return counts


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
    """Collect numeric *usage* fields whose key denotes token usage.

    Response-capacity metadata such as ``maxOutputTokens`` is not metered
    usage and must stay out of the diagnostic totals.
    """
    totals: dict[str, int] = {}
    non_usage_token_keys = {"maxoutputtokens", "maximumoutputtokens", "contextwindowtokens"}
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            normalized_key = "".join(character for character in str(key).lower() if character.isalnum())
            if (
                "token" in str(key).lower()
                and normalized_key not in non_usage_token_keys
                and type(child) is int
                and child >= 0
            ):
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

    input_tokens = usage.get("input_tokens")
    cache_read = usage.get("cache_read_input_tokens", usage.get("cached_input_tokens"))
    cache_write = cache_creation_tokens(usage)
    output = usage.get("output_tokens")
    reasoning = usage.get("reasoning_tokens", usage.get("reasoning_output_tokens"))
    if (
        type(input_tokens) is not int or input_tokens < 0
        or type(cache_read) is not int or cache_read < 0
        or type(cache_write) is not int or cache_write < 0
        or type(output) is not int or output < 0
        or (reasoning is not None and (type(reasoning) is not int or reasoning < 0))
    ):
        return None
    reasoning = reasoning if type(reasoning) is int else 0
    fresh = input_tokens + cache_write
    total = fresh + cache_read + output
    reported_total = usage.get("total_tokens", usage.get("total_provider_tokens"))
    if not isinstance(usage.get("cache_creation_input_tokens"), int) or not isinstance(usage.get("cache_read_input_tokens"), int):
        if cache_write == 0 and cache_read == 0:
            return None
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
        "reported_total_tokens": reported_total if type(reported_total) is int and reported_total >= 0 else None,
        "raw_usage": usage,
        "raw_token_fields": numeric_token_fields(usage),
        "raw_model_usage": event.get("modelUsage") if isinstance(event.get("modelUsage"), dict) else {},
        "raw_model_usage_token_fields": numeric_token_fields(event.get("modelUsage")),
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


def sum_raw_model_usage_token_fields(blocks: list[dict[str, Any]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for block in blocks:
        for key, value in block.get("raw_model_usage_token_fields", {}).items():
            totals[key] = totals.get(key, 0) + int(value)
    return dict(sorted(totals.items()))


def raw_usage_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "event_type": block.get("event_type"),
            "message_id": block.get("message_id"),
            "usage": block.get("raw_usage", {}),
            "model_usage": block.get("raw_model_usage", {}),
        }
        for block in blocks
    ]


def reported_totals(blocks: list[dict[str, Any]]) -> int | None:
    values = [block["reported_total_tokens"] for block in blocks if block.get("reported_total_tokens") is not None]
    return sum(values) if values else None


def build_summary(events_path: Path) -> dict[str, Any]:
    events, non_json_lines = load_events(events_path)
    assistant_blocks = usage_blocks(events, "assistant")
    result_blocks = usage_blocks(events, "result")

    warnings: list[str] = []
    assistant_has_provider_tokens = sum_key(assistant_blocks, "total_provider_tokens") > 0
    result_has_provider_tokens = sum_key(result_blocks, "total_provider_tokens") > 0
    if assistant_blocks and (assistant_has_provider_tokens or not result_has_provider_tokens):
        effective_blocks = assistant_blocks
        accounting_mode = "sum-unique-assistant-message-usage"
    elif result_blocks:
        effective_blocks = result_blocks
        accounting_mode = "result-usage-fallback-no-assistant-usage"
    else:
        effective_blocks = []
        accounting_mode = "no-usage-blocks"
        warnings.append("No Claude usage blocks found; token fields are zero and not decision-ready.")

    measurement_source = (
        "claude-code-stream-json-assistant-usage"
        if accounting_mode == "sum-unique-assistant-message-usage"
        else "claude-code-stream-json-result-usage"
    )
    if measurement_source == "claude-code-stream-json-assistant-usage" and sum_key(effective_blocks, "total_provider_tokens") == 0:
        warnings.append("Assistant usage was present but yielded zero provider tokens; treating the lane as invalid-accounting until raw assistant usage can be reconciled.")

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
        "accounting_note": (
            "Complete final result usage used because assistant blocks lacked provider token dimensions; retain result scope as provenance."
            if accounting_mode == "result-usage-fallback-no-assistant-usage"
            else ""
        ),
        "assistant_usage_block_count": len(assistant_blocks),
        "result_usage_block_count": len(result_blocks),
        "result_usage_counted": accounting_mode == "result-usage-fallback-no-assistant-usage",
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
        "raw_model_usage_token_field_totals": sum_raw_model_usage_token_fields(effective_blocks),
        "result_raw_model_usage_token_field_totals": sum_raw_model_usage_token_fields(result_blocks),
        "raw_usage_blocks": raw_usage_blocks(effective_blocks),
        "result_raw_usage_blocks": raw_usage_blocks(result_blocks),
        "provider_reported_total_tokens": provider_reported_total,
        "normalized_formula": "fresh_input_tokens + cached_input_tokens + output_tokens",
        "fresh_input_formula": "input_tokens + cache_creation_input_tokens",
    }

    agent_step_types = agent_step_type_counts(events)
    agent_steps = sum(agent_step_types.values()) or None

    event_types: dict[str, int] = {}
    for event in events:
        event_type = str(event.get("type") or "unknown")
        event_types[event_type] = event_types.get(event_type, 0) + 1

    return {
        "schema_version": 3,
        "source": "claude-code-stream-json",
        "source_artifact": str(events_path),
        "extracted_at_utc": dt.datetime.now(dt.UTC).isoformat(),
        "measurement_source": measurement_source,
        "fresh_input_tokens": fresh_input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "cache_write_tokens": cache_write_tokens,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_provider_tokens": total_provider_tokens,
        "weighted_token_cost": weighted_token_cost({
            "fresh_input_tokens": fresh_input_tokens,
            "cached_input_tokens": cached_input_tokens,
            "output_tokens": output_tokens,
        }),
        "weighted_token_cost_formula": WEIGHTED_TOKEN_COST_FORMULA,
        "agent_steps": agent_steps,
        "agent_step_definition": AGENT_STEP_DEFINITION,
        "agent_step_types": agent_step_types,
        "weighted_token_cost_per_step": weighted_token_cost_per_step({
            "fresh_input_tokens": fresh_input_tokens,
            "cached_input_tokens": cached_input_tokens,
            "output_tokens": output_tokens,
            "agent_steps": agent_steps,
        }),
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
    print(json.dumps({"weighted_token_cost": summary["weighted_token_cost"]}, indent=2))
    return 1 if summary["warnings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
