#!/usr/bin/env python3
"""Regression tests for lossless Claude Code token accounting."""

from __future__ import annotations

import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import extract_claude_code_usage
import opencode_workflow_adapter
import validate_repository


class ClaudeUsageContractTest(unittest.TestCase):
    def write_events(self, events: list[dict]) -> Path:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        with handle:
            for event in events:
                handle.write(json.dumps(event) + "\n")
        self.addCleanup(lambda: Path(handle.name).unlink(missing_ok=True))
        return Path(handle.name)

    def assistant(self, message_id: str, usage: dict) -> dict:
        return {
            "type": "assistant",
            "message": {
                "id": message_id,
                "role": "assistant",
                "usage": usage,
            },
        }

    def test_fresh_includes_cache_creation_and_preserves_nested_fields(self) -> None:
        events = [
            self.assistant(
                "a1",
                {
                    "input_tokens": 100,
                    "cache_read_input_tokens": 200,
                    "cache_creation": {
                        "ephemeral_5m_input_tokens": 30,
                        "ephemeral_1h_input_tokens": 7,
                    },
                    "output_tokens": 50,
                    "reasoning_tokens": 5,
                    "audio_input_tokens": 3,
                },
            ),
            self.assistant(
                "a2",
                {
                    "input_tokens": 10,
                    "cache_creation_input_tokens": 4,
                    "cache_read_input_tokens": 20,
                    "output_tokens": 6,
                },
            ),
            # Result usage is intentionally different and must not be added to
            # assistant usage when assistant usage is available.
            {
                "type": "result",
                "usage": {
                    "input_tokens": 9999,
                    "cache_read_input_tokens": 9999,
                    "output_tokens": 9999,
                },
            },
        ]
        summary = extract_claude_code_usage.build_summary(self.write_events(events))

        self.assertEqual(summary["fresh_input_tokens"], 151)
        self.assertEqual(summary["cached_input_tokens"], 220)
        self.assertEqual(summary["cache_write_tokens"], 41)
        self.assertEqual(summary["output_tokens"], 56)
        self.assertEqual(summary["reasoning_tokens"], 5)
        self.assertEqual(summary["total_provider_tokens"], 427)
        details = summary["provider_usage_details"]
        self.assertEqual(details["accounting_mode"], "sum-unique-assistant-message-usage")
        self.assertFalse(details["result_usage_counted"])
        self.assertEqual(details["canonical_components"]["input_tokens"], 110)
        self.assertEqual(details["canonical_components"]["cache_creation_input_tokens"], 41)
        self.assertEqual(details["canonical_components"]["cache_read_input_tokens"], 220)
        self.assertEqual(details["canonical_components"]["output_tokens"], 56)
        self.assertEqual(details["raw_token_field_totals"]["audio_input_tokens"], 3)
        self.assertEqual(details["raw_token_field_totals"]["cache_creation.ephemeral_5m_input_tokens"], 30)
        self.assertEqual(details["raw_token_field_totals"]["cache_creation.ephemeral_1h_input_tokens"], 7)
        self.assertEqual(details["result_raw_token_field_totals"]["input_tokens"], 9999)
        self.assertTrue(
            validate_repository.provider_usage_valid(
                {
                    "measurement_source": summary["measurement_source"],
                    **{
                        key: summary[key]
                        for key in validate_repository.PROVIDER_USAGE_FIELDS
                    },
                    "provider_usage_details": details,
                }
            )
        )

    def test_result_fallback_is_explicitly_warned(self) -> None:
        summary = extract_claude_code_usage.build_summary(
            self.write_events(
                [
                    self.assistant(
                        "zero-assistant",
                        {
                            "input_tokens": 0,
                            "output_tokens": 0,
                            "cache_creation_input_tokens": 0,
                            "cache_read_input_tokens": 0,
                        },
                    ),
                    {
                        "type": "result",
                        "usage": {
                            "input_tokens": 12,
                            "cache_creation_input_tokens": 8,
                            "cache_read_input_tokens": 40,
                            "output_tokens": 5,
                        },
                        "modelUsage": {
                            "gpt-5.6-sol": {
                                "inputTokens": 12,
                                "cacheReadInputTokens": 40,
                                "cacheCreationInputTokens": 8,
                                "outputTokens": 5,
                                "maxOutputTokens": 32000,
                            }
                        },
                    }
                ]
            )
        )
        self.assertEqual(summary["fresh_input_tokens"], 20)
        self.assertEqual(summary["cache_write_tokens"], 8)
        self.assertEqual(summary["total_provider_tokens"], 65)
        self.assertEqual(summary["measurement_source"], "claude-code-stream-json-result-usage")
        self.assertTrue(
            validate_repository.provider_usage_valid(
                {
                    "measurement_source": summary["measurement_source"],
                    **{
                        key: summary[key]
                        for key in validate_repository.PROVIDER_USAGE_FIELDS
                    },
                    "provider_usage_details": summary["provider_usage_details"],
                }
            )
        )
        self.assertEqual(
            summary["provider_usage_details"]["accounting_mode"],
            "result-usage-fallback-no-assistant-usage",
        )
        self.assertIn("Complete final result usage", summary["provider_usage_details"]["accounting_note"])
        self.assertEqual(
            summary["provider_usage_details"]["result_raw_model_usage_token_field_totals"]["gpt-5.6-sol.inputTokens"],
            12,
        )
        # A maximum-output budget is not observed usage and must not appear in
        # the diagnostic usage-token totals.
        self.assertNotIn(
            "gpt-5.6-sol.maxOutputTokens",
            summary["provider_usage_details"]["result_raw_model_usage_token_field_totals"],
        )
        self.assertEqual(len(summary["provider_usage_details"]["result_raw_usage_blocks"]), 1)
        self.assertFalse(summary["warnings"])

    def test_parent_cache_creation_aggregate_wins_without_double_counting_nested_breakdown(self) -> None:
        summary = extract_claude_code_usage.build_summary(
            self.write_events(
                [
                    self.assistant(
                        "a-parent",
                        {
                            "input_tokens": 1,
                            "cache_creation_input_tokens": 10,
                            "cache_creation": {"ephemeral_5m_input_tokens": 6},
                            "cache_read_input_tokens": 2,
                            "output_tokens": 3,
                        },
                    )
                ]
            )
        )
        self.assertEqual(summary["fresh_input_tokens"], 11)
        self.assertEqual(summary["cache_write_tokens"], 10)
        self.assertEqual(summary["total_provider_tokens"], 16)
        self.assertEqual(
            summary["provider_usage_details"]["raw_token_field_totals"]["cache_creation_input_tokens"],
            10,
        )
        self.assertEqual(
            summary["provider_usage_details"]["raw_token_field_totals"]["cache_creation.ephemeral_5m_input_tokens"],
            6,
        )


class OpenCodeUsageContractTest(unittest.TestCase):
    def test_last_message_write_creates_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "model-output" / "last.txt"
            opencode_workflow_adapter.write_last_message(target, "done")
            self.assertEqual(target.read_text(), "done\n")

    def test_last_message_write_retries_replaced_parent_without_provider_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "model-output" / "last.txt"
            original_write = Path.write_text
            attempts = 0

            def transient_write(path: Path, text: str, *args: object, **kwargs: object) -> int:
                nonlocal attempts
                if path == target and attempts < 3:
                    attempts += 1
                    raise FileNotFoundError("simulated mount replacement")
                return original_write(path, text, *args, **kwargs)

            with (
                mock.patch.object(Path, "write_text", new=transient_write),
                mock.patch.object(opencode_workflow_adapter.time, "sleep") as sleep,
            ):
                opencode_workflow_adapter.write_last_message(target, "recovered")
            self.assertEqual(attempts, 3)
            self.assertEqual(sleep.call_count, 3)
            self.assertEqual(target.read_text(), "recovered\n")

    def test_cache_write_is_in_fresh_and_not_added_twice(self) -> None:
        usage = opencode_workflow_adapter.step_usage({"tokens": {"input": 100, "output": 20, "reasoning": 5, "cache": {"read": 300, "write": 40}, "total": 465}})
        self.assertEqual((usage["fresh_input_tokens"], usage["cache_write_tokens"], usage["output_tokens"], usage["total_provider_tokens"]), (140, 40, 25, 465))


if __name__ == "__main__":
    raise SystemExit(unittest.main())
