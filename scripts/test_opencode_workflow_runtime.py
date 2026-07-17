from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import extract_opencode_usage
from scripts import opencode_workflow_adapter as adapter
from scripts import run_codex_fixture_evaluation as fixture
from scripts import run_codex_workflow_evaluation as runner
from scripts import run_sequential_workflow_matrix as matrix
from scripts import validate_repository as repository_validation
from scripts import workflow_model_condition_runtime as condition_runtime


def jwt(claims: dict[str, object]) -> str:
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return f"header.{payload}.signature"


def step_event(
    session: str,
    part_id: str,
    *,
    fresh: int,
    cached: int,
    cache_write: int,
    output: int,
    reasoning: int,
) -> dict[str, object]:
    return {
        "type": "step_finish",
        "sessionID": session,
        "part": {
            "id": part_id,
            "type": "step-finish",
            "tokens": {
                "input": fresh,
                "output": output,
                "reasoning": reasoning,
                "cache": {"read": cached, "write": cache_write},
                "total": fresh + cached + cache_write + output + reasoning,
            },
        },
    }


class OpenCodeWorkflowAdapterTest(unittest.TestCase):
    def test_runtime_environment_disables_auxiliary_network_and_binds_denied_shell(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env, _ = adapter._runtime_env(Path(tmp))
        config = json.loads(env["OPENCODE_CONFIG_CONTENT"])
        self.assertEqual(env["OPENCODE_DISABLE_MODELS_FETCH"], "1")
        self.assertEqual(config["shell"], "/usr/local/bin/eval-network-denied-shell")

    def test_binary_hash_is_enforced_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            binary = Path(td) / "opencode"
            binary.write_bytes(b"pinned-opencode-binary")
            expected = hashlib.sha256(binary.read_bytes()).hexdigest()
            self.assertEqual(adapter.verify_binary_sha256(binary, expected), expected)
            with self.assertRaisesRegex(ValueError, "OpenCode binary SHA-256 mismatch"):
                adapter.verify_binary_sha256(binary, "0" * 64)

    def test_parses_first_and_resume_codex_exec_shapes(self) -> None:
        first = adapter.parse_codex_exec_args(
            [
                "exec", "--model", "gpt-5.6-sol", "--config", 'model_reasoning_effort="high"',
                "--strict-config", "--config", 'web_search="disabled"', "--json", "--color", "never",
                "--disable", "hooks", "--ignore-rules", "--cd", "/workspace/repo",
                "--output-last-message", "/workspace/output.txt", "-",
            ]
        )
        self.assertEqual(first.model, "openai/gpt-5.6-sol")
        self.assertEqual(first.variant, "high")
        self.assertEqual(first.directory, Path("/workspace/repo"))
        self.assertIsNone(first.session_id)
        self.assertTrue(first.prompt_from_stdin)

        resumed = adapter.parse_codex_exec_args(
            [
                "exec", "resume", "--model", "gpt-5.6-sol", "-c", 'model_reasoning_effort="high"',
                "--json", "--output-last-message", "/workspace/output.txt", "ses_123", "-",
            ]
        )
        self.assertEqual(
            adapter.build_opencode_command(Path("/opt/opencode"), resumed, "continue task"),
            [
                "/opt/opencode", "run", "--format", "json", "--model", "openai/gpt-5.6-sol",
                "--variant", "high", "--auto", "--pure", "--session", "ses_123", "continue task",
            ],
        )

    def test_auth_translation_is_private_and_preserves_rotated_auth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "codex-auth.json"
            source.write_text(json.dumps({"tokens": {
                "access_token": jwt({"exp": 2_000_000_000, "chatgpt_account_id": "acct"}),
                "refresh_token": "refresh-secret",
            }}))
            summary = adapter.ensure_opencode_auth(source, root / "xdg-data")
            target = root / "xdg-data/opencode/auth.json"
            self.assertEqual(summary, {"provider": "openai", "auth_type": "oauth", "created": True})
            self.assertEqual(oct(target.stat().st_mode & 0o777), "0o600")
            auth = json.loads(target.read_text())["openai"]
            self.assertEqual(auth["accountId"], "acct")
            self.assertNotIn("refresh-secret", json.dumps(summary))
            target.write_text(json.dumps({"openai": {"type": "oauth", "refresh": "rotated"}}))
            self.assertFalse(adapter.ensure_opencode_auth(source, root / "xdg-data")["created"])
            self.assertEqual(json.loads(target.read_text())["openai"]["refresh"], "rotated")

    def test_normalizes_and_persists_incremental_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "usage.json"
            event = step_event("ses_1", "part_1", fresh=10, cached=7, cache_write=1, output=2, reasoning=3)
            first = adapter.normalize_events(
                [event, event, {"type": "text", "sessionID": "ses_1", "part": {"text": "done"}}],
                requested_session_id=None,
                state_path=state,
            )
            self.assertEqual(first.last_text, "done")
            self.assertEqual(first.usage, {
                "fresh_input_tokens": 10, "cached_input_tokens": 7, "cache_write_tokens": 1,
                "output_tokens": 5, "reasoning_tokens": 3, "total_provider_tokens": 23,
            })
            self.assertEqual(first.normalized_events[0], {"type": "thread.started", "thread_id": "ses_1"})
            second = adapter.normalize_events(
                [step_event("ses_1", "part_2", fresh=4, cached=5, cache_write=0, output=1, reasoning=1)],
                requested_session_id="ses_1",
                state_path=state,
            )
            self.assertEqual(second.usage, {
                "fresh_input_tokens": 14, "cached_input_tokens": 12, "cache_write_tokens": 1,
                "output_tokens": 7, "reasoning_tokens": 4, "total_provider_tokens": 34,
            })
            self.assertEqual(second.normalized_events[-1]["usage"]["input_tokens"], 27)

    def test_fails_closed_on_missing_session_usage_and_bad_total(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "usage.json"
            with self.assertRaisesRegex(ValueError, "session"):
                adapter.normalize_events([], requested_session_id=None, state_path=state)
            with self.assertRaisesRegex(ValueError, "usage"):
                adapter.normalize_events(
                    [{"type": "text", "sessionID": "ses_1", "part": {"text": "x"}}],
                    requested_session_id=None,
                    state_path=state,
                )
            bad = step_event("ses_1", "part_bad", fresh=1, cached=0, cache_write=0, output=1, reasoning=1)
            bad["part"]["tokens"]["total"] = 99  # type: ignore[index]
            with self.assertRaisesRegex(ValueError, "total"):
                adapter.normalize_events([bad], requested_session_id=None, state_path=state)


class OpenCodeUsageAccountingTest(unittest.TestCase):
    def test_extracts_unique_provider_comparable_step_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            first = {"type": "opencode.event", "event": step_event("ses_1", "part_1", fresh=10, cached=7, cache_write=1, output=2, reasoning=3)}
            second = {"type": "opencode.event", "event": step_event("ses_1", "part_2", fresh=4, cached=5, cache_write=0, output=1, reasoning=1)}
            path.write_text("\n".join(json.dumps(item) for item in [first, first, second]) + "\n")
            summary = extract_opencode_usage.build_summary(path)
        self.assertEqual(summary["measurement_source"], "opencode-jsonl-step-finish-usage")
        self.assertEqual(
            [summary[key] for key in (
                "fresh_input_tokens", "cached_input_tokens", "cache_write_tokens",
                "output_tokens", "reasoning_tokens", "total_provider_tokens",
            )],
            [14, 12, 1, 7, 4, 34],
        )
        self.assertEqual(summary["opencode_usage"]["unique_step_finish_parts"], 2)
        self.assertEqual(summary["warnings"], [])

    def test_missing_usage_fails_closed_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text(json.dumps({"type": "thread.started", "thread_id": "ses_1"}) + "\n")
            summary = extract_opencode_usage.build_summary(path)
        self.assertIsNone(summary["total_provider_tokens"])
        self.assertTrue(summary["warnings"])


class OpenCodeWorkflowIntegrationContractTest(unittest.TestCase):
    PROFILE_ID = "runtime-opencode-codex-product-v1"
    CONDITION_ID = "opencode-openai-gpt-5-6-sol-high"

    def test_profile_binds_replacement_runtime_and_isolated_adapter(self) -> None:
        self.assertEqual(runner.SUPPORTED_WORKFLOW_TOOL_PROFILES[self.PROFILE_ID], "opencode-codex-product-v1")
        meta = runner.PROFILE_META[self.PROFILE_ID]
        self.assertEqual(meta["session_role"], "replacement_runtime")
        cfg = fixture.active_tool_config({}, self.PROFILE_ID)
        assert cfg is not None
        self.assertEqual(cfg["codex_wrapper"]["command"], "/usr/bin/python3")
        self.assertIn("/opt/data/tool-candidates/opencode-adapter/opencode_workflow_adapter.py", cfg["codex_wrapper"]["args"])
        expected_hash = "7c4d91c84d2bfdeabb59257e3490c5e5acb08f2aacb3e42f3ddc296a1c3f1aca"
        self.assertEqual(cfg["expected_executable_sha256"], expected_hash)
        self.assertIn("--expected-opencode-sha256", cfg["codex_wrapper"]["args"])
        self.assertIn(expected_hash, cfg["codex_wrapper"]["args"])
        self.assertEqual(cfg["default_tool_state"], "native-runtime")
        self.assertEqual(cfg["preflight_command"][-1], "--probe")
        self.assertEqual(meta["tool_use_policy"], "none")

    def test_registry_binds_opencode_runtime_and_sol_high_condition(self) -> None:
        registry = json.loads((ROOT / "data/evaluation-agent-runtimes.json").read_text())
        runtime = next(item for item in registry["agent_runtimes"] if item["id"] == "opencode-cli")
        self.assertEqual(runtime["usage_extractor"], "scripts/extract_opencode_usage.py")
        condition = next(item for item in registry["model_conditions"] if item["id"] == self.CONDITION_ID)
        self.assertEqual(condition["runtime_id"], "opencode-cli")
        self.assertEqual(condition["model"], "gpt-5.6-sol")
        self.assertEqual(condition["reasoning_effort"], "high")

    def test_execution_descriptor_and_run_record_bind_selected_runtime(self) -> None:
        sequence = runner.load_sequence("fastify-lifecycle-sequence-v0")
        descriptor = runner.execution_condition_descriptor(sequence, self.PROFILE_ID)
        self.assertEqual(descriptor["agent_condition"]["runtime_id"], "opencode-cli")
        self.assertEqual(descriptor["agent_condition"]["runtime_version_condition"], "captured-at-run-and-bound-to-record")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = runner.base_record("session", sequence, self.PROFILE_ID, root / "project", root / "run")
        self.assertEqual(record["agent"]["runtime_id"], "opencode-cli")

    def test_runtime_profile_uses_opencode_accounting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events = Path(tmp) / "events.jsonl"
            events.write_text(json.dumps({
                "type": "opencode.event",
                "event": step_event("ses", "part", fresh=1, cached=2, cache_write=3, output=4, reasoning=5),
            }) + "\n")
            summary = runner.build_provider_usage(self.PROFILE_ID, events)
        self.assertEqual(summary["measurement_source"], "opencode-jsonl-step-finish-usage")
        self.assertEqual(summary["total_provider_tokens"], 15)
        self.assertTrue(repository_validation.provider_usage_valid(summary))
        self.assertIn("replacement_runtime", repository_validation.WORKFLOW_SESSION_ROLES)

    def test_model_condition_pair_uses_codex_baseline_and_opencode_treatment(self) -> None:
        selected, baseline = condition_runtime.resolve_condition_pair(ROOT, self.CONDITION_ID)
        self.assertEqual(selected["runtime_id"], "opencode-cli")
        self.assertEqual(baseline["id"], "codex-openai-gpt-5-6-sol-high")
        self.assertEqual(baseline["runtime_id"], "codex-cli")
        self.assertEqual(selected["provider"], baseline["provider"])
        self.assertEqual(selected["model"], baseline["model"])
        self.assertEqual(selected["reasoning_effort"], baseline["reasoning_effort"])

    def test_matrix_routes_opencode_condition_to_opencode_launcher(self) -> None:
        args = argparse.Namespace(
            workflow_model_condition_id=self.CONDITION_ID,
            workflow_model="gpt-5.6-sol",
            workflow_reasoning_effort="high",
        )
        condition = matrix.selected_model_condition(args, configure=False)
        assert condition is not None
        self.assertEqual(condition["runtime_id"], "opencode-cli")
        command = matrix.workflow_lane_command(
            sequence_id="fastify-lifecycle-sequence-v0",
            profile_id=self.PROFILE_ID,
            protocol=Path("protocol.json"),
            replicate_index=0,
            runner_args=[],
            model_condition=condition,
        )
        self.assertEqual(command[1], "scripts/run_opencode_workflow_model_condition.py")

    def test_matrix_dry_run_resolves_published_codex_baselines_after_runtime_binding(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "scripts/run_sequential_workflow_matrix.py",
                "fastify-lifecycle-sequence-v0",
                "beets-lifecycle-sequence-v0",
                "terraform-lifecycle-sequence-v0",
                "--replicate-index",
                "0",
                "--max-parallel",
                "1",
                "--workflow-model-condition-id",
                self.CONDITION_ID,
                "--workflow-model",
                "gpt-5.6-sol",
                "--workflow-reasoning-effort",
                "high",
                "--treatment-profile",
                self.PROFILE_ID,
                "--dry-run",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        plan = json.loads(proc.stdout)
        self.assertEqual(len(plan["jobs"]), 3)

    def test_runtime_profile_prompt_is_native_runtime_not_token_tool_guidance(self) -> None:
        guidance = runner.profile_prompt_guidance(self.PROFILE_ID)
        self.assertIn("OpenCode", guidance)
        self.assertIn("native shell", guidance)
        self.assertNotIn("token-saving treatment", guidance)


if __name__ == "__main__":
    unittest.main()
