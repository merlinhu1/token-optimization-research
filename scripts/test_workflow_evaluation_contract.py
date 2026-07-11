from __future__ import annotations

import copy
import hashlib
import inspect
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import audit_tool_isolation
from scripts import extract_codex_usage
from scripts import generate_workflow_qualification as qualification
from scripts import refresh_workflow_contracts as contract_refresh
from scripts import run_codescope_neutral_mcp as codescope_adapter
from scripts import run_codex_workflow_evaluation as runner
from scripts import run_codex_workflow_model_condition as model_condition_runner
from scripts import run_sequential_workflow_matrix as matrix
from scripts import validate_repository


SEQUENCE_ID = "terraform-lifecycle-sequence-v0"


def retained_protocol_path(
    sequence_id: str,
    profile_id: str,
    replicate_index: int = 1,
    model_condition_id: str = "codex-openai-gpt-5-6-luna-xhigh",
) -> Path:
    registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
    matches = [
        session
        for session in registry["sessions"]
        if session.get("task_sequence", {}).get("sequence_id") == sequence_id
        and session.get("profile", {}).get("profile_id") == profile_id
        and session.get("replicate_index") == replicate_index
        and session.get("agent", {}).get("model_condition_id") == model_condition_id
    ]
    if len(matches) != 1:
        raise AssertionError(
            f"expected one retained protocol for {sequence_id}/{profile_id}/{model_condition_id}/r{replicate_index}; "
            f"found {[session['session_id'] for session in matches]}"
        )
    path = ROOT / matches[0]["frozen_protocol"]["path"]
    if not path.is_file():
        raise AssertionError(f"retained frozen protocol is missing: {path}")
    return path


class ToolIsolationAuditTest(unittest.TestCase):
    def test_ponytail_product_authored_caveman_reference_is_not_cross_tool_use(self) -> None:
        record = {
            "setup": {
                "tool_permissions": {
                    "profile_id": "artifact-ponytail-codex-plugin-v1",
                    "allowed_token_saving_tools": ["ponytail", "ponytail-codex-plugin-v1"],
                }
            }
        }
        forbidden, allowed = audit_tool_isolation.forbidden_for(record)
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "events.jsonl"
            artifact.write_text("Ponytail may be paired with Caveman for terse prose.\n")
            self.assertEqual(audit_tool_isolation.scan_file(artifact, forbidden, allowed), [])

        control = copy.deepcopy(record)
        control["setup"]["tool_permissions"]["profile_id"] = "baseline-bare-codex"
        forbidden, allowed = audit_tool_isolation.forbidden_for(control)
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "events.jsonl"
            artifact.write_text("Caveman was invoked.\n")
            self.assertEqual(
                [hit["term"] for hit in audit_tool_isolation.scan_file(artifact, forbidden, allowed)],
                ["caveman"],
            )


class CodexUsageAccountingTest(unittest.TestCase):
    def summarize(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text("".join(json.dumps(event) + "\n" for event in events))
            return extract_codex_usage.build_summary(path)

    @staticmethod
    def thread_usage(thread_id: str, usage: dict[str, int]) -> list[dict[str, object]]:
        return [
            {"type": "thread.started", "thread_id": thread_id},
            {"type": "turn.completed", "usage": usage},
        ]

    def test_resumed_thread_uses_final_cumulative_total_instead_of_sum(self) -> None:
        first = {
            "input_tokens": 100,
            "cached_input_tokens": 80,
            "output_tokens": 10,
            "reasoning_output_tokens": 3,
        }
        final = {
            "input_tokens": 250,
            "cached_input_tokens": 200,
            "output_tokens": 20,
            "reasoning_output_tokens": 7,
        }
        summary = self.summarize(
            self.thread_usage("thread-a", first) + self.thread_usage("thread-a", final)
        )
        self.assertEqual(summary["total_provider_tokens"], 270)
        self.assertEqual(summary["fresh_input_tokens"], 50)
        self.assertEqual(summary["cached_input_tokens"], 200)
        self.assertEqual(summary["output_tokens"], 20)
        self.assertEqual(summary["reasoning_tokens"], 7)
        codex_usage = summary["codex_usage"]
        self.assertEqual(codex_usage["accounting_mode"], "final-cumulative-total-per-thread")
        self.assertEqual(len(codex_usage["usage_blocks"]), 2)
        self.assertEqual(len(codex_usage["effective_usage_blocks"]), 1)
        self.assertEqual(
            [block["usage"] for block in codex_usage["incremental_usage_blocks"]],
            [
                first,
                {
                    "cached_input_tokens": 120,
                    "input_tokens": 150,
                    "output_tokens": 10,
                    "reasoning_output_tokens": 4,
                },
            ],
        )

    def test_distinct_threads_sum_their_final_cumulative_totals(self) -> None:
        events = self.thread_usage(
            "thread-a",
            {"input_tokens": 100, "cached_input_tokens": 80, "output_tokens": 10},
        ) + self.thread_usage(
            "thread-b",
            {"input_tokens": 50, "cached_input_tokens": 40, "output_tokens": 5},
        )
        summary = self.summarize(events)
        self.assertEqual(summary["total_provider_tokens"], 165)
        self.assertEqual(summary["fresh_input_tokens"], 30)
        self.assertEqual(summary["cached_input_tokens"], 120)
        self.assertEqual(summary["output_tokens"], 15)

    def test_resumed_thread_rejects_decreasing_cumulative_counters(self) -> None:
        events = self.thread_usage(
            "thread-a",
            {"input_tokens": 100, "cached_input_tokens": 80, "output_tokens": 10},
        ) + self.thread_usage(
            "thread-a",
            {"input_tokens": 90, "cached_input_tokens": 70, "output_tokens": 9},
        )
        with self.assertRaisesRegex(ValueError, "decreased"):
            self.summarize(events)

    def test_retained_accounting_correction_covers_every_session(self) -> None:
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        audit_path = (
            ROOT
            / "sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json"
        )
        audit = json.loads(audit_path.read_text())
        rows = {row["session_id"]: row for row in audit["sessions"]}
        self.assertEqual(rows.keys(), {session["session_id"] for session in registry["sessions"]})
        self.assertEqual(audit["integrity"]["correction_required_count"], sum(row["correction_required"] for row in rows.values()))
        self.assertTrue(audit["integrity"]["all_manifests_passed"])
        self.assertTrue(audit["integrity"]["all_usage_monotonic"])
        terraform_r0 = rows["baseline-terraform-20260718-p-ca21cbff5ed5-r0"]
        self.assertEqual(
            terraform_r0["legacy_registry_usage"]["total_provider_tokens"], 31_471_786
        )
        self.assertEqual(terraform_r0["corrected_usage"]["total_provider_tokens"], 15_526_000)
        self.assertEqual(
            [
                task["corrected_incremental_usage"]["total_provider_tokens"]
                for task in terraform_r0["tasks"]
            ],
            [4_999_516, 5_946_754, 4_579_730],
        )


class ActiveCampaignArchitectureTest(unittest.TestCase):
    def test_all_lifecycle_sequences_cover_the_v0_task_mix(self) -> None:
        sequences = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
        lifecycle = [
            sequence
            for sequence in sequences
            if sequence.get("status") == "active"
            and sequence.get("sequence_contract") == "feature-refactor-review"
        ]
        self.assertEqual(len(lifecycle), 3)
        for sequence in lifecycle:
            ordered = sorted(sequence["tasks"], key=lambda task: task["order"])
            expected_classes = [
                "feature-implementation",
                "behavior-preserving-refactor",
                "code-review-correction",
            ]
            self.assertEqual([task["task_class"] for task in ordered], expected_classes)
            self.assertTrue(all(task["id"].endswith("-v0") for task in ordered))
            descriptor = runner.baseline_protocol_descriptor(sequence)
            self.assertEqual(descriptor["sequence_contract"], "feature-refactor-review")
            self.assertEqual([task["task_class"] for task in descriptor["tasks"]], expected_classes)
            review_task = ordered[2]
            self.assertEqual(review_task["review_patch_path"], "review-change.patch")
            self.assertIn("review_patch_sha256", descriptor["tasks"][2])
            self.assertNotIn("review_patch_sha256", descriptor["tasks"][0])

    def test_review_patch_is_disclosed_only_with_the_review_prompt(self) -> None:
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        review_task = sorted(sequence["tasks"], key=lambda task: task["order"])[2]
        source_dir = (ROOT / review_task["prompt_path"]).parent
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            for order in (1, 3):
                alias = runner.task_dir(project, order)
                alias.mkdir(parents=True)
                task = next(item for item in sequence["tasks"] if item["order"] == order)
                source = (ROOT / task["prompt_path"]).parent
                (alias / "agent-prompt.txt").write_text((source / "agent-prompt.txt").read_text())
                if order == 3:
                    (alias / "review-change.patch").write_bytes((source_dir / "review-change.patch").read_bytes())
            first = runner.task_prompt(sequence, "baseline-bare-codex", project, 1, first_task=True)
            review = runner.task_prompt(sequence, "baseline-bare-codex", project, 3, first_task=False)
        self.assertNotIn("## Proposed change under review", first)
        self.assertIn("## Proposed change under review", review)
        self.assertIn("diff --git", review)

    def test_refactor_qualification_separates_behavior_and_structure(self) -> None:
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        qualification = json.loads((ROOT / sequence["qualification_path"]).read_text())
        boundary = next(
            item
            for item in qualification["cumulative_boundaries"]
            if item["task_id"] == "beets-lifecycle-refactor-v0"
        )
        self.assertEqual(boundary["seeded_behavior_exit"], 0)
        self.assertNotEqual(boundary["seeded_structure_exit"], 0)
        self.assertEqual(boundary["fixed_behavior_exit"], 0)
        self.assertEqual(boundary["fixed_structure_exit"], 0)

    def test_runbook_matches_active_lifecycle_contract(self) -> None:
        runbook = (ROOT / "docs/evaluations/operations/runbook.md").read_text()
        self.assertNotIn("at least five causally related production files", runbook)
        exact_prepare = 'python3 scripts/run_sequential_workflow_matrix.py --prepare-only "$SEQUENCE_ID"'
        prepare_lines = [
            line
            for line in runbook.splitlines()
            if "scripts/run_sequential_workflow_matrix.py" in line
            and "--prepare-only" in line
            and "$SEQUENCE_ID" in line
        ]
        self.assertEqual(prepare_lines, [exact_prepare])
        self.assertNotIn("--skip-container-preflight", runbook)

    def test_runbook_does_not_offer_duplicate_baseline_commands(self) -> None:
        runbook = (ROOT / "docs/evaluations/operations/runbook.md").read_text()
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        completed = {
            session["task_sequence"]["sequence_id"]
            for session in registry["sessions"]
            if session.get("status") == "completed"
            and session.get("session_role") == "baseline"
            and session.get("interpretation", {}).get("accepted_for_objective") is True
        }
        self.assertEqual(
            completed,
            {
                "fastify-lifecycle-sequence-v0",
                "beets-lifecycle-sequence-v0",
                "terraform-lifecycle-sequence-v0",
            },
        )
        for sequence_id in completed:
            self.assertNotIn(
                f"python3 scripts/run_sequential_workflow_matrix.py {sequence_id}\n",
                runbook,
            )
        self.assertIn('--treatment-profile "$PROFILE_ID"', runbook)
        self.assertIn(
            "Non-default model-comparison baselines are tracked separately",
            runbook,
        )
        default_model_id = runner.DEFAULT_WORKFLOW_MODEL_CONDITION_ID
        comparison_model_id = "codex-openai-gpt-5-6-sol-high"
        for sequence_id in completed:
            default_replicates = sorted(
                {
                    session["replicate_index"]
                    for session in registry["sessions"]
                    if session.get("status") == "completed"
                    and session.get("session_role") == "baseline"
                    and session.get("task_sequence", {}).get("sequence_id") == sequence_id
                    and session.get("agent", {}).get("model_condition_id") == default_model_id
                    and session.get("interpretation", {}).get("accepted_for_objective") is True
                }
            )
            comparison_replicates = sorted(
                {
                    session["replicate_index"]
                    for session in registry["sessions"]
                    if session.get("status") == "completed"
                    and session.get("session_role") == "baseline"
                    and session.get("task_sequence", {}).get("sequence_id") == sequence_id
                    and session.get("agent", {}).get("model_condition_id") == comparison_model_id
                    and session.get("interpretation", {}).get("accepted_for_objective") is True
                }
            )
            self.assertIn(
                f"`{sequence_id}` ({', '.join(f'r{index}' for index in default_replicates)})",
                runbook,
            )
            self.assertIn(
                f"`{sequence_id}` under `{comparison_model_id}` "
                f"({', '.join(f'r{index}' for index in comparison_replicates)})",
                runbook,
            )

    def test_repository_surfaces_match_production_evidence_state(self) -> None:
        stale_claims = {
            "docs/evaluations/README.md": "No production result exists",
            "sources/evaluations/README.md": "There are no retained production results",
            "data/workflow-task-sequences.json": "pre-production evaluation portfolio",
            "data/repository-fixtures.json": "No production result has been recorded",
        }
        for rel, stale in stale_claims.items():
            self.assertNotIn(stale, (ROOT / rel).read_text(), rel)
        fixtures = json.loads((ROOT / "data/repository-fixtures.json").read_text())["fixtures"]
        self.assertTrue(fixtures)
        self.assertTrue(all(item["status"] == "treatment-ready" for item in fixtures), fixtures)

    def test_agent_guidance_requires_evidence_driven_document_sync(self) -> None:
        guidance = (ROOT / "AGENTS.md").read_text()
        self.assertIn("## Documentation lifecycle", guidance)
        self.assertIn("Update the machine authority first", guidance)
        self.assertIn("Regenerate `docs/evaluations/operations/runbook.md`", guidance)
        self.assertIn("Preserve frozen evidence bytes", guidance)

    def test_prompt_surfaces_require_post_action_document_sync(self) -> None:
        evaluator_prompt = (ROOT / "prompts/evaluator.md").read_text()
        protocol_skill = (ROOT / ".agents/skills/benchmark-protocol-writer.md").read_text()
        self.assertIn("After execution, follow the `AGENTS.md` documentation lifecycle", evaluator_prompt)
        self.assertIn("regenerate the workflow runbook", evaluator_prompt)
        self.assertIn("## After a run", protocol_skill)
        self.assertIn("regenerate the runbook", protocol_skill)

    def test_retired_progressive_evaluation_scaffold_is_absent(self) -> None:
        retired = (
            "docs/evaluations/progressive-repository-evaluation-plan.md",
            "docs/evaluations/changes/README.md",
            "templates/progressive-evaluation-change",
            "templates/workflow-session-record.json",
        )
        for rel in retired:
            self.assertFalse((ROOT / rel).exists(), rel)

    def test_workflow_session_schema_does_not_dispatch_on_protocol_id_suffix(self) -> None:
        schema = json.loads((ROOT / "schemas/workflow-session-record.schema.json").read_text())
        self.assertNotIn('"pattern": "-v3$"', json.dumps(schema))
        v2_rule = next(
            item
            for item in schema["allOf"]
            if item.get("if", {}).get("properties", {}).get("schema_version", {}).get("const") == 2
        )
        required = set(v2_rule["then"]["required"])
        self.assertTrue(
            {"frozen_protocol", "selected_execution", "docker_image_identity", "tool_adapter_identity"}
            <= required
        )

    def test_active_tasks_need_real_scope_not_arbitrary_file_padding(self) -> None:
        workflow = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        fixtures = json.loads((ROOT / "data/repository-fixtures.json").read_text())
        errors: list[str] = []
        with (
            mock.patch.object(
                validate_repository,
                "patch_paths",
                return_value=["beets/one_behavior_bearing_file.py"],
            ),
            mock.patch.object(
                validate_repository,
                "validate_qualification",
            ),
        ):
            validate_repository.validate_workflow_task_sequences(workflow, fixtures, errors)
        self.assertFalse(any("minimum is 5" in error for error in errors), errors)

    def test_active_concealed_paths_are_unique_to_the_controller(self) -> None:
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        qualification_record = json.loads((ROOT / sequence["qualification_path"]).read_text())
        self.assertTrue(qualification_record["fixed_snapshot_model_concealed_paths_absent"])
        for task in sequence["tasks"]:
            for path in task["model_concealed_paths"]:
                self.assertTrue(path.startswith("test/controller_hidden/"), path)
        for task_record in qualification_record["tasks"]:
            self.assertTrue(task_record["fixed_snapshot_model_concealed_absent"], task_record)

    def test_feature_verifier_checks_semantics_not_canonical_error_prose(self) -> None:
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        feature = sorted(sequence["tasks"], key=lambda task: task["order"])[0]
        hidden = next(
            (ROOT / feature["prompt_path"]).parent.glob("controller-hidden/**/*.py")
        ).read_text()
        self.assertNotIn("pytest.raises(UserError, match=", hidden)
        self.assertIn('assert "title" in message', hidden)
        self.assertIn('assert "+=" in message', hidden)

    def test_refactor_verifier_does_not_require_undisclosed_parameter_names(self) -> None:
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        refactor = sorted(sequence["tasks"], key=lambda task: task["order"])[1]
        verifier = (ROOT / refactor["verifier_command"]).read_text()
        self.assertNotIn("inspect.signature", verifier)
        self.assertNotIn('"fixed_values" in params', verifier)

    def test_current_production_portfolio_has_three_lanes(self) -> None:
        profiles = json.loads((ROOT / "data/evaluation-profiles.json").read_text())["profiles"]
        shortlisted = [profile["id"] for profile in profiles if profile.get("status") == "screening-shortlist"]
        corrected = [
            "terminal-tokenjuice-codex-hook-v1",
            "terminal-rtk-codex-instructions-v1",
            "terminal-snip-codex-hook-v1",
            "retrieval-graphify-codex-skill-v1",
            "retrieval-codegraph-codex-mcp-v1",
            "retrieval-jcodemunch-codex-mcp-v2",
            "integrated-leanctx-codex-hybrid-v1",
            "retrieval-cartog-codex-product-v2",
            "codescope-codex-product-v1",
            "swarmvault-codex-product-v1",
            "retrieval-serena-codex-mcp-v1",
            "retrieval-sigmap-codex-live-v1",
            "integrated-token-savior-codex-product-v2",
            "artifact-ponytail-codex-plugin-v1",
            "behavior-caveman-codex-skill-v1",
        ]
        self.assertEqual(
            set(shortlisted),
            {
                "headroom-default-codex",
                *corrected,
            },
        )
        for profile_id in shortlisted:
            runner.assert_profile_runnable(profile_id)

        fixtures = json.loads((ROOT / "data/repository-fixtures.json").read_text())["fixtures"]
        active = [fixture for fixture in fixtures if fixture.get("evaluation_use") == "primary-objective"]
        self.assertEqual(
            [fixture["id"] for fixture in active],
            ["medium-fastify-fastify", "medium-beetbox-beets", "large-hashicorp-terraform"],
        )
        for fixture in active:
            self.assertEqual(fixture["candidate_profiles"], ["baseline-bare-codex", *corrected])

        medium = json.loads((ROOT / "data/medium-project-candidates.json").read_text())
        medium_active = [
            candidate["id"]
            for candidate in medium["candidates"]
            if candidate.get("selection_status") in {"primary-fixture", "production-fixture"}
        ]
        self.assertEqual(medium_active, ["medium-fastify-fastify", "medium-beetbox-beets"])
        large = json.loads((ROOT / "data/large-project-candidates.json").read_text())
        self.assertEqual(
            [candidate["id"] for candidate in large["candidates"] if candidate.get("selection_status") == "production-fixture"],
            ["large-hashicorp-terraform"],
        )

    def test_new_treatment_adapters_preserve_declared_boundaries(self) -> None:
        runner.assert_profile_runnable("terminal-headroom")
        self.assertIs(
            runner.fixture.active_tool_config({}, "headroom-default-codex"),
            runner.fixture.TOOL_CONFIGS["headroom"],
        )
        self.assertIs(
            runner.fixture.active_tool_config({}, "terminal-headroom"),
            runner.fixture.TOOL_CONFIGS["headroom-proxy-only"],
        )
        proxy_only = runner.fixture.TOOL_CONFIGS["headroom-proxy-only"]
        wrapper_args = proxy_only["codex_wrapper"]["args"]
        self.assertEqual(proxy_only["lane_name"], "terminal-headroom")
        for flag in ("--no-context-tool", "--no-mcp", "--no-tokensave", "--no-serena"):
            self.assertIn(flag, wrapper_args)
        self.assertNotIn("--no-proxy", wrapper_args)
        self.assertIn("--port", wrapper_args)
        self.assertIn("{tool_port}", wrapper_args)
        self.assertTrue({"headroom_retrieve", "rtk", "tokensave", "serena"}.issubset(proxy_only["allowed_terms"]))

        cartog = runner.fixture.TOOL_CONFIGS["cartog-codex-product-v2"]
        self.assertTrue(cartog["mcp_config_via_host_integration"])
        self.assertEqual(cartog["mcp_args"], ["serve", "--watch"])
        self.assertEqual(cartog["warmup"]["kind"], "official-init-and-structural-index")
        self.assertNotIn("CARTOG_AUTO_INIT", cartog["env"])
        self.assertEqual(cartog["diff_exclude_paths"], [".cartog", ".cartog.toml", "AGENTS.md"])
        self.assertNotIn("AGENTS.md", cartog["warmup"]["cleanup_paths"])
        install_commands = cartog["host_integration"]["install_commands"]
        self.assertIn(
            ["{tool_data_dir}/bin/cartog", "ide", "--client", "codex", "--yes"],
            install_commands,
        )
        self.assertIn(
            "{tool_data_dir}/cartog-codex-product-installation.json",
            cartog["host_integration"]["required_files"],
        )
        self.assertIn("{repo}/AGENTS.md", cartog["host_integration"]["required_files"])
        self.assertIn("{codex_home}/config.toml", cartog["host_integration"]["required_files"])
        self.assertIn("scripts/install_cartog_codex_product.py", " ".join(cartog["mounts"]))

        codescope = runner.fixture.TOOL_CONFIGS["codescope"]
        self.assertEqual(codescope["mcp_command"], "python3")
        self.assertEqual(codescope["default_tool_state"], "cold-auto-index")
        self.assertEqual(
            codescope["initialize_instructions_policy"],
            "strip-mandatory-uptake-text",
        )
        self.assertIn("--codescope-bin", codescope["mcp_args"])
        self.assertEqual(
            runner.fixture.CODESCOPE_NEUTRAL_MCP.read_bytes(),
            runner.fixture.CODESCOPE_NEUTRAL_MCP_SOURCE.read_bytes(),
        )
        self.assertTrue({str(runner.fixture.CODESCOPE_BIN), str(runner.fixture.CODESCOPE_SURREAL_BIN)}.issubset(codescope["mounts"]))
        self.assertEqual(codescope["diff_exclude_paths"], [".fastembed_cache", ".codescope"])
        self.assertEqual(
            runner.treatment_diff_exclude_paths(codescope),
            (".fastembed_cache", ".codescope"),
        )

        graphify = runner.fixture.TOOL_CONFIGS["graphify"]
        self.assertEqual(runner.treatment_diff_exclude_paths(graphify), ("graphify-out",))

        initialize = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2025-06-18",
                "instructions": "ALWAYS prefer CodeScope and follow strictly",
                "serverInfo": {"name": "codescope", "version": "0.8.12"},
            },
        }
        sanitized = json.loads(codescope_adapter.sanitize_response((json.dumps(initialize) + "\n").encode()))
        self.assertNotIn("instructions", sanitized["result"])
        self.assertEqual(sanitized["result"]["serverInfo"], initialize["result"]["serverInfo"])

        swarmvault = runner.fixture.TOOL_CONFIGS["swarmvault"]
        self.assertEqual(swarmvault["mcp_server"], "swarmvault")
        self.assertEqual(swarmvault["default_tool_state"], "warm-index")
        self.assertEqual(swarmvault["warmup"]["kind"], "knowledge-graph-build")
        self.assertIn("init --lite", swarmvault["warmup"]["command"][-1])
        self.assertIn(" ingest {repo}", swarmvault["warmup"]["command"][-1])
        self.assertIn("--max-files 500", swarmvault["warmup"]["command"][-1])
        self.assertIn(" compile", swarmvault["warmup"]["command"][-1])
        self.assertNotIn("install-agent-rules", " ".join(swarmvault["warmup"]["command"]))
        self.assertEqual(runner.artifact_profile_label("codescope-owner"), "codescope")
        self.assertEqual(runner.artifact_profile_label("swarmvault-owner"), "swarmvault")
        self.assertNotEqual(
            runner.canonical_treatment_session_id("fastify-fastify", "codescope-owner", 1),
            runner.canonical_treatment_session_id("fastify-fastify", "swarmvault-owner", 1),
        )

    def test_ineligible_historical_profiles_are_not_runnable(self) -> None:
        historical = {
            "terminal-tokenjuice", "terminal-rtk", "terminal-snip",
            "retrieval-jcodemunch-mcp", "retrieval-leanctx", "retrieval-codegraph",
            "retrieval-cartog", "retrieval-cartog-mcp-v1", "codescope-owner", "swarmvault-owner",
            "retrieval-serena", "retrieval-graphify", "retrieval-sigmap",
            "integrated-token-savior", "stack-tokenjuice-jcodemunch-mcp",
        }
        for profile_id in historical:
            with self.assertRaisesRegex(ValueError, "historical-profile"):
                runner.assert_profile_runnable(profile_id)

    def test_future_candidate_profiles_fail_closed_without_parity_and_qualification(self) -> None:
        unexecuted_profile_id = "integrated-token-savior-codex-product-v2"
        profile_doc = json.loads((ROOT / "data/evaluation-profiles.json").read_text())
        fixture_doc = json.loads((ROOT / "data/repository-fixtures.json").read_text())
        sequence_doc = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        parity_doc = json.loads(
            (ROOT / "sources/evaluations/audits/official-integration-parity-20260718.json").read_text()
        )
        qualification_docs = [
            json.loads(path.read_text())
            for path in sorted(
                (ROOT / "sources/evaluations/audits").glob("corrected-integration-qualification-*.json")
            )
        ]
        protocol_docs = {
            path.relative_to(ROOT).as_posix(): {
                "document": json.loads(path.read_text()),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in (ROOT / "sources/evaluations/protocols").glob("*.json")
        }
        executed_protocol_paths = validate_repository.executed_protocol_paths_from_registry(
            json.loads((ROOT / "data/workflow-sessions.json").read_text())
        )
        future_candidate_executed_protocol_paths = {
            path
            for path in executed_protocol_paths
            if protocol_docs[path]["document"]["selected_execution"]["descriptor"]["selected_profile"]["profile_id"]
            != unexecuted_profile_id
        }

        errors: list[str] = []
        validate_repository.validate_candidate_profile_launch_readiness(
            profile_doc,
            fixture_doc,
            sequence_doc,
            parity_doc,
            qualification_docs,
            protocol_docs,
            errors,
            executed_protocol_paths=future_candidate_executed_protocol_paths,
        )
        self.assertEqual(errors, [])

        missing_approval = copy.deepcopy(parity_doc)
        missing_approval["corrected_contracts"]["approved_profile_ids"].remove(
            unexecuted_profile_id
        )
        errors = []
        validate_repository.validate_candidate_profile_launch_readiness(
            profile_doc,
            fixture_doc,
            sequence_doc,
            missing_approval,
            qualification_docs,
            protocol_docs,
            errors,
            executed_protocol_paths=future_candidate_executed_protocol_paths,
        )
        self.assertTrue(any("parity-approved profile set" in error for error in errors), errors)

        missing_lane_receipts = copy.deepcopy(qualification_docs)
        for receipt in missing_lane_receipts:
            receipt["lanes"] = [
                lane
                for lane in receipt["lanes"]
            if not (
                lane["sequence_id"] == "fastify-lifecycle-sequence-v0"
                and lane["profile_id"] == unexecuted_profile_id
            )
        ]
        errors = []
        validate_repository.validate_candidate_profile_launch_readiness(
            profile_doc,
            fixture_doc,
            sequence_doc,
            parity_doc,
            missing_lane_receipts,
            protocol_docs,
            errors,
            executed_protocol_paths=future_candidate_executed_protocol_paths,
        )
        self.assertTrue(any("missing matching provider-free qualification" in error for error in errors), errors)

        empty_mcp_tools = copy.deepcopy(qualification_docs)
        for receipt in empty_mcp_tools:
            for lane in receipt["lanes"]:
                if lane["sequence_id"] == "fastify-lifecycle-sequence-v0" and lane["profile_id"] == unexecuted_profile_id:
                    lane["mcp_handshake"]["tool_count"] = 0
                    lane["mcp_handshake"]["tool_names"] = []
        errors = []
        validate_repository.validate_candidate_profile_launch_readiness(
            profile_doc,
            fixture_doc,
            sequence_doc,
            parity_doc,
            empty_mcp_tools,
            protocol_docs,
            errors,
            executed_protocol_paths=future_candidate_executed_protocol_paths,
        )
        self.assertTrue(any("non-empty MCP tools/list proof" in error for error in errors), errors)

    def test_provider_launch_rechecks_candidate_readiness_gate(self) -> None:
        args = runner.argparse.Namespace(prepare_only=False, protocol=None)
        with mock.patch.object(
            runner.repository_validation,
            "current_candidate_profile_launch_readiness_errors",
            return_value=["missing qualification"],
            create=True,
        ):
            with self.assertRaisesRegex(ValueError, "provider launch readiness gate failed"):
                runner.validate_protocol_for_run(
                    runner.load_sequence("fastify-lifecycle-sequence-v0"),
                    "retrieval-cartog-codex-product-v2",
                    args,
                )

    def test_corrected_tokenjuice_profile_binds_official_integration(self) -> None:
        profile = "terminal-tokenjuice-codex-hook-v1"
        cfg = runner.fixture.active_tool_config({}, profile)
        self.assertEqual(runner.SUPPORTED_WORKFLOW_TOOL_PROFILES[profile], "tokenjuice-codex-hook-v1")
        self.assertEqual(cfg["host_integration"]["install_commands"], [["tokenjuice", "install", "codex"]])
        self.assertTrue(cfg["codex_features"]["hooks"])

    def test_corrected_rtk_and_snip_profiles_bind_official_codex_integrations(self) -> None:
        rtk_profile = "terminal-rtk-codex-instructions-v1"
        rtk_cfg = runner.fixture.active_tool_config({}, rtk_profile)
        assert rtk_cfg is not None
        self.assertEqual(runner.SUPPORTED_WORKFLOW_TOOL_PROFILES[rtk_profile], "rtk-codex-instructions-v1")
        self.assertEqual(rtk_cfg["host_integration"]["install_commands"], [["rtk", "init", "--global", "--codex"]])
        self.assertEqual(
            set(rtk_cfg["host_integration"]["required_files"]),
            {"{codex_home}/AGENTS.md", "{codex_home}/RTK.md"},
        )
        self.assertNotIn("prompt_instructions_command", rtk_cfg)

        snip_profile = "terminal-snip-codex-hook-v1"
        snip_cfg = runner.fixture.active_tool_config({}, snip_profile)
        assert snip_cfg is not None
        self.assertEqual(runner.SUPPORTED_WORKFLOW_TOOL_PROFILES[snip_profile], "snip-codex-hook-v1")
        self.assertEqual(snip_cfg["host_integration"]["install_commands"], [["snip", "init", "--agent", "codex"]])
        self.assertTrue(snip_cfg["host_integration"]["home_dot_codex_alias"])
        self.assertTrue(snip_cfg["codex_features"]["hooks"])
        self.assertIn("{codex_home}/hooks.json", snip_cfg["host_integration"]["required_files"])
        self.assertEqual(runner.fixture.codex_hook_args(snip_cfg), [])

    def test_home_dot_codex_alias_targets_lane_private_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp) / "codex-home"
            codex_home.mkdir()
            alias = runner.fixture.prepare_home_dot_codex_alias(codex_home)
            self.assertTrue(alias.is_symlink())
            self.assertEqual(alias.resolve(), codex_home.resolve())

    def test_corrected_graphify_codegraph_and_leanctx_profiles_bind_full_codex_integrations(self) -> None:
        graphify_profile = "retrieval-graphify-codex-skill-v1"
        graphify_cfg = runner.fixture.active_tool_config({}, graphify_profile)
        assert graphify_cfg is not None
        self.assertEqual(runner.SUPPORTED_WORKFLOW_TOOL_PROFILES[graphify_profile], "graphify-codex-skill-v1")
        self.assertEqual(
            graphify_cfg["host_integration"]["install_commands"][-1],
            ["{tool_data_dir}/venv/bin/graphify", "install", "--platform", "codex"],
        )
        self.assertTrue(graphify_cfg["codex_features"]["hooks"])
        self.assertTrue(graphify_cfg["codex_features"]["multi_agent"])
        self.assertIn("graphify codex install", graphify_cfg["warmup"]["command"][-1])
        self.assertNotIn("mcp_server", graphify_cfg)

        codegraph_profile = "retrieval-codegraph-codex-mcp-v1"
        codegraph_cfg = runner.fixture.active_tool_config({}, codegraph_profile)
        assert codegraph_cfg is not None
        self.assertEqual(runner.SUPPORTED_WORKFLOW_TOOL_PROFILES[codegraph_profile], "codegraph-codex-mcp-v1")
        self.assertEqual(
            codegraph_cfg["host_integration"]["install_commands"][-1],
            ["{tool_data_dir}/bin/codegraph", "install", "--target", "codex", "--location", "global", "--yes"],
        )
        self.assertNotIn("--no-watch", codegraph_cfg["mcp_args"])
        self.assertTrue(codegraph_cfg["mcp_handshake"]["required"])
        self.assertEqual(codegraph_cfg["warmup"]["command"], ["{tool_data_dir}/bin/codegraph", "init", "{repo}"])

        leanctx_profile = "integrated-leanctx-codex-hybrid-v1"
        leanctx_cfg = runner.fixture.active_tool_config({}, leanctx_profile)
        assert leanctx_cfg is not None
        self.assertEqual(runner.SUPPORTED_WORKFLOW_TOOL_PROFILES[leanctx_profile], "leanctx-codex-hybrid-v1")
        self.assertEqual(leanctx_cfg["host_integration"]["install_commands"], [["/opt/data/bin/lean-ctx", "init", "--agent", "codex"]])
        self.assertEqual(leanctx_cfg["host_integration"]["verify_commands"], [["/opt/data/bin/lean-ctx", "--version"]])
        self.assertIn("{codex_home}/hooks.json", leanctx_cfg["host_integration"]["required_files"])
        self.assertIn("{repo}/AGENTS.md", leanctx_cfg["host_integration"]["required_files"])
        self.assertTrue(leanctx_cfg["mcp_handshake"]["required"])
        self.assertEqual(leanctx_cfg["warmup"]["command"], ["/opt/data/bin/lean-ctx", "index", "build", "{repo}"])

    def test_codex_config_renders_all_declared_boolean_features(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp)
            runner.fixture.write_codex_config(codex_home, {}, "retrieval-graphify-codex-skill-v1")
            config = (codex_home / "config.toml").read_text()
        self.assertIn("hooks = true", config)
        self.assertIn("multi_agent = true", config)

    def test_cartog_profile_defers_mcp_config_to_official_installer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            codex_home = Path(tmp)
            runner.fixture.write_codex_config(codex_home, {}, "retrieval-cartog-codex-product-v2")
            config = (codex_home / "config.toml").read_text()
        self.assertNotIn("[mcp_servers.cartog", config)

    def test_unproven_treatment_results_and_protocols_are_deleted_not_relabelled(self) -> None:
        receipt = json.loads(
            (ROOT / "sources/evaluations/audits/unproven-treatment-result-deletions-20260718.json").read_text()
        )
        sessions = json.loads((ROOT / "data/workflow-sessions.json").read_text())["sessions"]
        active_ids = {row["session_id"] for row in sessions}
        self.assertEqual(receipt["policy"]["baseline_relabeling"], "forbidden")
        self.assertEqual(len(receipt["profiles"]), 6)
        for deleted in receipt["profiles"]:
            self.assertTrue(set(deleted["deleted_session_ids"]).isdisjoint(active_ids))
            for relative in deleted["deleted_protocol_paths"] + deleted["deleted_comparison_paths"] + deleted["deleted_bundle_roots"]:
                self.assertFalse((ROOT / relative).exists(), relative)

    def test_invalid_cartog_results_are_deleted_not_relabelled(self) -> None:
        receipt = json.loads(
            (ROOT / "sources/evaluations/audits/invalid-cartog-result-deletions-20260720.json").read_text()
        )
        sessions = json.loads((ROOT / "data/workflow-sessions.json").read_text())["sessions"]
        active_ids = {row["session_id"] for row in sessions}
        self.assertEqual(receipt["profile_id"], "retrieval-cartog-mcp-v1")
        self.assertEqual(receipt["disposition"], "invalid-treatment-configuration")
        self.assertEqual(receipt["baseline_relabeling"], "forbidden")
        self.assertEqual(receipt["replacement_profile_id"], "retrieval-cartog-codex-product-v2")
        self.assertEqual(len(receipt["deleted_session_ids"]), 6)
        self.assertTrue(set(receipt["deleted_session_ids"]).isdisjoint(active_ids))
        for relative in (
            receipt["deleted_protocol_paths"]
            + receipt["deleted_comparison_paths"]
            + receipt["deleted_bundle_roots"]
        ):
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_graphify_identity_path_renders_lane_private_tool_data_dir(self) -> None:
        cfg = runner.fixture.TOOL_CONFIGS["graphify-codex-skill-v1"]
        lane_path = runner._lane_path(cfg)
        expected = runner.fixture.tool_data_dir(ROOT / ".identity-codex-home", cfg) / "bin"
        self.assertIn(str(expected), lane_path.split(":"))

    def test_codegraph_binary_identity_is_generated_by_host_integration(self) -> None:
        identity = runner.tool_adapter_identity("retrieval-codegraph-codex-mcp-v1")
        self.assertEqual(identity["binary_identity"]["kind"], "generated-by-host-integration")

    def test_replacements_for_unproven_profiles_require_assignment_proof_and_product_parity(self) -> None:
        expected = {
            "retrieval-cartog-codex-product-v2": "cartog-codex-product-v2",
            "codescope-codex-product-v1": "codescope-codex-product-v1",
            "swarmvault-codex-product-v1": "swarmvault-codex-product-v1",
            "retrieval-serena-codex-mcp-v1": "serena-codex-mcp-v1",
            "retrieval-sigmap-codex-live-v1": "sigmap-codex-live-v1",
            "integrated-token-savior-mcp-v1": "token-savior-mcp-v1",
        }
        for profile_id, tool_id in expected.items():
            self.assertEqual(runner.SUPPORTED_WORKFLOW_TOOL_PROFILES[profile_id], tool_id)
            cfg = runner.fixture.active_tool_config({}, profile_id)
            assert cfg is not None
            self.assertTrue(cfg["mcp_handshake"]["required"], profile_id)

        codescope = runner.fixture.active_tool_config({}, "codescope-codex-product-v1")
        assert codescope is not None
        warmup = " ".join(codescope["warmup"]["command"])
        self.assertIn("codescope start", warmup)
        self.assertIn("codescope init --agent codex", warmup)
        self.assertIn("codescope stop", warmup)
        self.assertEqual(codescope["mcp_command"], "/bin/bash")
        self.assertIn("codescope mcp", codescope["mcp_args"][-1])
        self.assertIn("codescope stop", codescope["mcp_args"][-1])

        swarmvault = runner.fixture.active_tool_config({}, "swarmvault-codex-product-v1")
        assert swarmvault is not None
        swarmvault_warmup = " ".join(swarmvault["warmup"]["command"][-1:])
        self.assertIn(" install --agent codex --hook", swarmvault_warmup)
        self.assertTrue(swarmvault["codex_features"]["hooks"])

        serena = runner.fixture.active_tool_config({}, "retrieval-serena-codex-mcp-v1")
        assert serena is not None
        self.assertIn("setup", serena["host_integration"]["install_commands"][0])
        self.assertIn("codex", serena["host_integration"]["install_commands"][0])
        self.assertIn("--project-from-cwd", serena["mcp_args"])
        self.assertIn("--context=codex", serena["mcp_args"])

        sigmap = runner.fixture.active_tool_config({}, "retrieval-sigmap-codex-live-v1")
        assert sigmap is not None
        self.assertIn("--watch", sigmap["mcp_args"][-1])
        self.assertIn("--mcp", sigmap["mcp_args"][-1])

        token_savior = runner.fixture.active_tool_config({}, "integrated-token-savior-mcp-v1")
        assert token_savior is not None
        self.assertEqual(token_savior["env"]["TOKEN_SAVIOR_CLIENT"], "codex")

    def test_token_savior_product_guided_codex_successor_installs_guidance_and_hooks(self) -> None:
        profile_id = "integrated-token-savior-codex-product-v2"
        self.assertEqual(runner.SUPPORTED_WORKFLOW_TOOL_PROFILES[profile_id], "token-savior-codex-product-v2")
        cfg = runner.fixture.active_tool_config({}, profile_id)
        assert cfg is not None
        self.assertEqual(cfg["env"]["TOKEN_SAVIOR_CLIENT"], "codex")
        self.assertEqual(cfg["env"]["TOKEN_SAVIOR_PROFILE"], "optimized")
        self.assertEqual(cfg["env"]["TS_CAPTURE_DISABLED"], "0")
        self.assertEqual(cfg["env"]["TS_BASH_COMPACT"], "1")
        self.assertEqual(cfg["env"]["TS_BASH_REWRITE"], "1")
        self.assertTrue(cfg["codex_features"]["hooks"])
        self.assertTrue(cfg["codex_hook_bypass_trust"])
        self.assertTrue(cfg["mcp_handshake"]["required"])
        self.assertIn("AGENTS.md", cfg["diff_exclude_paths"])
        required = cfg["host_integration"]["required_files"]
        self.assertIn("{repo}/AGENTS.md", required)
        self.assertIn("{codex_home}/hooks.json", required)
        self.assertIn("{tool_data_dir}/codex-product-installation.json", required)
        self.assertIn("{tool_data_dir}/codex-hook-probe.json", required)
        self.assertEqual(cfg["host_integration"]["install_commands"], [])
        installs = [" ".join(command) for command in cfg["host_integration"]["controller_install_commands"]]
        self.assertTrue(any("install_token_savior_codex_product.py" in command for command in installs))
        self.assertTrue(any("probe_token_savior_codex_hooks.py" in command for command in installs))
        self.assertIn('backend="host"', inspect.getsource(runner.fixture.prepare_profile_integration))
        self.assertEqual(
            runner.tool_adapter_identity("integrated-token-savior-mcp-v1")["tool_manifest_sha256"],
            runner.LEGACY_TOOL_MANIFEST_SHA256,
        )
        self.assertEqual(
            runner.tool_adapter_identity(profile_id)["tool_manifest_sha256"],
            hashlib.sha256((ROOT / "scripts/run_codex_fixture_evaluation.py").read_bytes()).hexdigest(),
        )

        profiles = json.loads((ROOT / "data/evaluation-profiles.json").read_text())["profiles"]
        successor = next(item for item in profiles if item["id"] == profile_id)
        bounded = next(item for item in profiles if item["id"] == "integrated-token-savior-mcp-v1")
        self.assertEqual(successor["status"], "screening-shortlist")
        self.assertIn("product-authored-codex-guidance", successor["enabled_surfaces"])
        self.assertEqual(bounded["status"], "screening-ablation")
        self.assertEqual(bounded["superseded_by"], profile_id)

        qualification = json.loads(
            (
                ROOT
                / "sources/evaluations/audits/corrected-integration-qualification-token-savior-codex-product-v2-20260719.json"
            ).read_text()
        )
        self.assertEqual(qualification["profiles"], [profile_id])
        self.assertEqual(qualification["provider_calls"], 0)
        self.assertEqual(len(qualification["lanes"]), 3)
        for lane in qualification["lanes"]:
            self.assertTrue(lane["prepared"])
            self.assertTrue(lane["host_integration"]["passed"])
            self.assertEqual(lane["host_integration"]["controller_install_exit_codes"], [0, 0])
            self.assertTrue(lane["mcp_handshake"]["passed"])
            protocol = ROOT / lane["protocol_path"]
            self.assertEqual(lane["protocol_sha256"], hashlib.sha256(protocol.read_bytes()).hexdigest())

    def test_token_savior_codex_product_installer_preserves_existing_agents_and_emits_current_hooks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            codex_home = root / "codex-home"
            receipt = root / "receipt.json"
            repo.mkdir()
            (repo / "AGENTS.md").write_text("# Existing project guidance\n\nKeep me.\n")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/install_token_savior_codex_product.py"),
                    "--source-root",
                    "/opt/data/tool-candidates/token-savior",
                    "--expected-commit",
                    "ff42ef14cc972dad5470e0ca8101e4501e00600f",
                    "--codex-home",
                    str(codex_home),
                    "--repo",
                    str(repo),
                    "--receipt",
                    str(receipt),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            agents = (repo / "AGENTS.md").read_text()
            product_guidance = Path("/opt/data/tool-candidates/token-savior/CLAUDE.md").read_text().rstrip()
            self.assertTrue(agents.startswith("# Existing project guidance\n\nKeep me.\n"))
            self.assertIn(product_guidance, agents)
            hooks = json.loads((codex_home / "hooks.json").read_text())
            self.assertEqual(set(hooks["hooks"]), {"PreToolUse", "PostToolUse"})
            self.assertEqual(hooks["hooks"]["PreToolUse"][0]["matcher"], "Bash")
            self.assertIn("bash_rewriter_hook.py", hooks["hooks"]["PreToolUse"][0]["hooks"][0]["command"])
            self.assertIn("tool_capture_hook.py", hooks["hooks"]["PostToolUse"][0]["hooks"][0]["command"])
            payload = json.loads(receipt.read_text())
            self.assertFalse(payload["evaluator_authored_guidance"])
            self.assertTrue(payload["host_adapter_authored_by_evaluator"])
            self.assertEqual(payload["source_commit"], "ff42ef14cc972dad5470e0ca8101e4501e00600f")

            probe_receipt = root / "hook-probe.json"
            hook_probe = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/probe_token_savior_codex_hooks.py"),
                    "--source-root",
                    "/opt/data/tool-candidates/token-savior",
                    "--repo",
                    str(repo),
                    "--state-dir",
                    str(root / "hook-state"),
                    "--receipt",
                    str(probe_receipt),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(hook_probe.returncode, 0, hook_probe.stderr)
            probe = json.loads(probe_receipt.read_text())
            self.assertEqual(probe["provider_calls"], 0)
            self.assertTrue(probe["pre_tool_use"]["passed"])
            self.assertIn("--porcelain=v2", probe["pre_tool_use"]["rewritten_command"])
            self.assertTrue(probe["post_tool_use"]["passed"])
            self.assertIn("[token-savior:compact]", probe["post_tool_use"]["additional_context"])

    def test_mcp_handshake_runs_after_profile_workspace_warmup(self) -> None:
        workflow_source = inspect.getsource(runner.run_one)
        self.assertLess(
            workflow_source.index("fixture.prepare_profile_workspace("),
            workflow_source.index("fixture.probe_mcp_handshake("),
        )
        fixture_source = inspect.getsource(runner.fixture.main)
        self.assertLess(
            fixture_source.index("prepare_profile_workspace("),
            fixture_source.index("probe_mcp_handshake("),
        )

    def test_mcp_probe_encodes_dash_prefixed_server_arguments(self) -> None:
        source = inspect.getsource(runner.fixture.probe_mcp_handshake)
        self.assertIn('command.append(f"--arg={arg}")', source)
        self.assertNotIn('command.extend(["--arg", arg])', source)

    def test_mcp_probe_requires_at_least_one_advertised_tool(self) -> None:
        server_source = """import json,sys
for line in sys.stdin:
    message=json.loads(line)
    if message.get('method')=='initialize':
        print(json.dumps({'jsonrpc':'2.0','id':message['id'],'result':{'protocolVersion':'2025-06-18','serverInfo':{'name':'fixture','version':'1'},'capabilities':{}}}),flush=True)
    elif message.get('method')=='tools/list':
        print(json.dumps({'jsonrpc':'2.0','id':message['id'],'result':{'tools':[]}}),flush=True)
"""
        with tempfile.TemporaryDirectory() as tmp:
            server = Path(tmp) / "empty_mcp.py"
            server.write_text(server_source)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/probe_mcp_stdio.py"),
                    "--command",
                    sys.executable,
                    "--arg",
                    str(server),
                    "--timeout",
                    "2",
                ],
                text=True,
                capture_output=True,
                timeout=10,
                check=False,
            )
        self.assertEqual(proc.returncode, 1)
        receipt = json.loads(proc.stdout)
        self.assertIn("tools/list advertised no tools", receipt["errors"])

    def test_official_integration_audit_matches_session_dispositions(self) -> None:
        audit = json.loads(
            (ROOT / "sources/evaluations/audits/official-integration-parity-20260718.json").read_text()
        )
        sessions = json.loads((ROOT / "data/workflow-sessions.json").read_text())["sessions"]
        by_profile = {}
        for session in sessions:
            by_profile.setdefault(session["profile"]["profile_id"], []).append(session)
        deletion_receipts = [
            json.loads(path.read_text())
            for path in (ROOT / "sources/evaluations/audits").glob("*deletion*.json")
            if "profiles" in json.loads(path.read_text())
        ]
        deleted_by_profile = {
            row["profile_id"]: row
            for receipt in deletion_receipts
            for row in receipt["profiles"]
        }
        expected_validity = {
            "unverified-treatment-assignment": "unverified-treatment-assignment",
        }
        for item in audit["profiles"]:
            retained = by_profile.get(item["profile_id"], [])
            if item.get("active_corpus_action") == "deleted-under-owner-authorized-receipt":
                self.assertEqual(item["session_ids"], [])
                self.assertFalse(item["objective_eligible"])
                self.assertNotIn(item["profile_id"], by_profile)
                deleted = deleted_by_profile[item["profile_id"]]
                self.assertEqual(sorted(item["deleted_session_ids"]), sorted(deleted["deleted_session_ids"]))
                for relative in deleted["deleted_protocol_paths"] + deleted["deleted_comparison_paths"] + deleted["deleted_bundle_roots"]:
                    self.assertFalse((ROOT / relative).exists(), relative)
                continue
            self.assertEqual(sorted(item["session_ids"]), sorted(row["session_id"] for row in retained))
            self.assertEqual(
                item["objective_eligible"],
                all(row["interpretation"]["accepted_for_objective"] for row in retained),
            )
            if item["disposition"] in expected_validity:
                self.assertTrue(
                    all(
                        row["interpretation"]["evaluation_validity"]
                        == expected_validity[item["disposition"]]
                        for row in retained
                    )
                )

    def test_ineligible_treatment_disposition_preserves_execution_only(self) -> None:
        for validity in ("invalid-treatment-configuration", "unverified-treatment-assignment"):
            session = {
                "status": "excluded",
                "interpretation": {
                    "evaluation_validity": validity,
                    "accepted_for_execution": True,
                    "accepted_for_objective": False,
                    "primary_objective_hard_baseline": False,
                    "usable_for_primary_objective_token_comparison": False,
                    "comparison_baseline_session_id": "",
                    "invalidity_reasons": ["official integration assignment was not proven"],
                },
            }
            errors: list[str] = []
            validate_repository.validate_invalid_treatment_disposition(session, "session", errors)
            self.assertEqual(errors, [])

    def test_task_delta_can_exclude_treatment_owned_cache_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            run_dir = root / "run"
            repo.mkdir()
            run_dir.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Fixture Test"], cwd=repo, check=True)
            source = repo / "source.txt"
            source.write_text("before\n")
            subprocess.run(["git", "add", "source.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
            source.write_text("after\n")
            cache = repo / ".cartog"
            cache.mkdir()
            (cache / "cartog.db").write_bytes(b"treatment cache")

            delta = runner.capture_task_delta(repo, run_dir, 1, (".cartog",))
            text = delta.read_text()
            self.assertIn("source.txt", text)
            self.assertNotIn(".cartog", text)
            self.assertNotIn("cartog.db", text)

    def test_evidence_bundle_sources_exclude_controller_answer_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            (run_dir / "tasks/task-01/controller-hidden").mkdir(parents=True)
            (run_dir / "tasks/task-01/seed-regression.patch").write_text("answer patch\n")
            (run_dir / "tasks/task-01/controller-hidden/hidden_test.py").write_text("answer test\n")
            (run_dir / "task-prompts").mkdir()
            (run_dir / "task-prompts/task-01.md").write_text("model-visible prompt\n")
            (run_dir / "codex-events.jsonl").write_text("{}\n")
            (run_dir / "composite-seed.diff").write_text("answer composite\n")

            paths = {path.relative_to(run_dir).as_posix() for path in runner.evidence_source_files(run_dir)}
            self.assertIn("task-prompts/task-01.md", paths)
            self.assertIn("codex-events.jsonl", paths)
            self.assertNotIn("composite-seed.diff", paths)
            self.assertFalse(any(path.startswith("tasks/") for path in paths))

    def test_validator_does_not_hardcode_active_sequence_ids(self) -> None:
        workflow = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        fixtures = json.loads((ROOT / "data/repository-fixtures.json").read_text())
        workflow = copy.deepcopy(workflow)
        workflow["sequences"][0]["id"] = "replacement-lifecycle-sequence-v0"
        errors: list[str] = []
        validate_repository.validate_workflow_task_sequences(workflow, fixtures, errors)
        self.assertFalse(
            any("active workflow sequences must be exactly" in error for error in errors),
            errors,
        )

    def test_protocol_ids_are_derived_for_new_sequences(self) -> None:
        sequence = copy.deepcopy(runner.load_sequence(SEQUENCE_ID))
        sequence["id"] = "replacement-lifecycle-sequence-v0"
        protocol_id = contract_refresh.protocol_id(sequence, "baseline-bare-codex")
        self.assertRegex(
            protocol_id,
            r"^replacement-lifecycle-sequence-v0-baseline-bare-codex-[a-f0-9]{12}$",
        )

    def test_protocol_id_changes_when_frozen_controller_provenance_changes(self) -> None:
        sequence = runner.load_sequence(SEQUENCE_ID)
        original = contract_refresh.protocol_id(sequence, "baseline-bare-codex")
        changed_descriptor = runner.baseline_protocol_descriptor(sequence)
        changed_descriptor["validator_sha256"] = "0" * 64
        with mock.patch.object(
            runner,
            "baseline_protocol_descriptor",
            return_value=changed_descriptor,
        ):
            changed = contract_refresh.protocol_id(sequence, "baseline-bare-codex")
        self.assertNotEqual(original, changed)

    def test_protocol_compatibility_ignores_only_noncausal_provenance_hashes(self) -> None:
        sequence = runner.load_sequence(SEQUENCE_ID)
        current = runner.baseline_protocol_descriptor(sequence)
        provenance_only = copy.deepcopy(current)
        provenance_only["runner_sha256"] = "0" * 64
        provenance_only["validator_sha256"] = "1" * 64
        self.assertTrue(
            runner.baseline_protocol_descriptor_compatible(provenance_only, current)
        )
        causal_change = copy.deepcopy(provenance_only)
        causal_change["tasks"][0]["prompt_sha256"] = "2" * 64
        self.assertFalse(
            runner.baseline_protocol_descriptor_compatible(causal_change, current)
        )

    def test_protocol_writer_refuses_to_overwrite_different_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "protocol.json"
            contract_refresh.write_json(path, {"value": 1})
            contract_refresh.write_json(path, {"value": 1})
            with self.assertRaises(FileExistsError):
                contract_refresh.write_json(path, {"value": 2})

    def test_registry_lifecycle_matches_record_presence(self) -> None:
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        sessions = registry["sessions"]
        self.assertIn(registry["production_status"], {"pre-production", "production"})
        if registry["production_status"] == "pre-production":
            self.assertEqual(sessions, [])
        else:
            self.assertTrue(sessions)
            self.assertTrue(all(session.get("schema_version") == 2 for session in sessions))

    def test_protocol_lookup_rejects_unknown_sequence(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown or non-active workflow sequence"):
            matrix.find_protocol(
                ROOT,
                "missing-lifecycle-sequence-v0",
                "baseline-bare-codex",
            )

    def test_current_treatment_protocol_remains_discoverable_for_later_replicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            protocol_dir = root / "sources/evaluations/protocols"
            protocol_dir.mkdir(parents=True)
            sequence = {
                "id": "unit-sequence",
                "status": "active",
                "qualification_path": "qualification.json",
            }
            (root / "data/workflow-task-sequences.json").write_text(
                json.dumps({"sequences": [sequence]})
            )
            protocol_rel = "sources/evaluations/protocols/unit.json"
            (root / "data/workflow-sessions.json").write_text(
                json.dumps(
                    {
                        "sessions": [
                            {
                                "status": "completed",
                                "interpretation": {"accepted_for_execution": True},
                                "frozen_protocol": {"path": protocol_rel},
                            }
                        ]
                    }
                )
            )
            protocol = {
                "status": "frozen-ready-not-run",
                "task_fixture": {
                    "sequence_id": "unit-sequence",
                    "qualification_path": "qualification.json",
                },
                "baseline_pool": {
                    "protocol_fingerprint": "unit-fingerprint",
                    "descriptor": {"unit": "baseline"},
                },
                "selected_execution": {
                    "descriptor": {
                        "selected_profile": {"profile_id": "unit-treatment"}
                    },
                    "descriptor_sha256": "unit-exec-hash",
                },
            }
            (root / protocol_rel).write_text(json.dumps(protocol))
            legacy_protocol = copy.deepcopy(protocol)
            legacy_protocol["baseline_pool"]["descriptor"] = {"unit": "legacy-baseline"}
            (protocol_dir / "legacy-compatible.json").write_text(json.dumps(legacy_protocol))
            with (
                mock.patch.object(
                    matrix.workflow,
                    "baseline_protocol_fingerprint",
                    return_value="unit-fingerprint",
                ),
                mock.patch.object(
                    matrix.workflow,
                    "baseline_protocol_descriptor",
                    return_value={"unit": "baseline"},
                ),
                mock.patch.object(
                    matrix.workflow,
                    "baseline_protocol_descriptor_compatible",
                    return_value=True,
                ),
                mock.patch.object(
                    matrix.workflow,
                    "execution_condition_descriptor",
                    return_value={
                        "selected_profile": {
                            "profile_id": "unit-treatment"
                        }
                    },
                ),
                mock.patch.object(
                    matrix.workflow,
                    "_json_hash",
                    return_value="unit-exec-hash",
                ),
            ):
                self.assertEqual(
                    matrix.find_protocol(
                        root,
                        "unit-sequence",
                        "unit-treatment",
                    ),
                    root / protocol_rel,
                )

    def test_current_protocols_declare_strict_schema_version(self) -> None:
        for sequence_id in runner.active_sequence_ids():
            path = retained_protocol_path(sequence_id, "baseline-bare-codex")
            protocol = json.loads(path.read_text())
            self.assertEqual(protocol.get("protocol_schema_version"), 3, path.name)
            sequence = runner.load_sequence(sequence_id)
            qualification = json.loads((ROOT / sequence["qualification_path"]).read_text())
            self.assertGreaterEqual(protocol["frozen_at"], qualification["qualified_on"])
            self.assertEqual(protocol["frozen_at"], sequence["protocol_freeze_date"])


class SeedDeliveryContractTest(unittest.TestCase):
    def create_repo(self, root: Path, content: str = "base\n") -> tuple[Path, Path]:
        repo = root / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture Test"], cwd=repo, check=True)
        source = repo / "value.txt"
        source.write_text(content)
        subprocess.run(["git", "add", "value.txt"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
        return repo, source

    def create_seed_patch(self, repo: Path, patch: Path) -> None:
        patch.write_text(subprocess.run(["git", "diff", "--full-index", "--binary"], cwd=repo, check=True, text=True, capture_output=True).stdout)
        subprocess.run(["git", "reset", "--hard", "-q", "HEAD"], cwd=repo, check=True)

    def test_qualification_reset_discards_tracked_verifier_side_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, source = self.create_repo(Path(tmp))
            fixed_head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=repo, check=True, text=True, capture_output=True
            ).stdout.strip()
            source.write_text("verifier changed tracked source\n")
            qualification.reset_tracked_checkout(repo, fixed_head)
            self.assertEqual(source.read_text(), "base\n")
            self.assertEqual(
                subprocess.run(
                    ["git", "status", "--porcelain", "--untracked-files=no"],
                    cwd=repo,
                    check=True,
                    text=True,
                    capture_output=True,
                ).stdout,
                "",
            )

    def test_qualification_detects_concealed_paths_present_in_fixed_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            checkout = Path(tmp)
            collision = checkout / "test/controller_hidden/collision.py"
            collision.parent.mkdir(parents=True)
            collision.write_text("fixed upstream test\n")
            sequence = {
                "tasks": [
                    {
                        "model_concealed_paths": [
                            "test/controller_hidden/collision.py",
                            "test/controller_hidden/absent.py",
                        ]
                    }
                ]
            }
            self.assertEqual(
                qualification.concealed_path_collisions(checkout, sequence),
                ["test/controller_hidden/collision.py"],
            )

    def test_terraform_concealed_collisions_are_byte_exact_controller_copies(self) -> None:
        sequence = runner.load_sequence("terraform-lifecycle-sequence-v0")
        qualification_record = json.loads((ROOT / sequence["qualification_path"]).read_text())
        audit = qualification_record["fixed_snapshot_concealed_path_collision_audit"]
        self.assertEqual(len(audit), 1)
        self.assertTrue(all(record["byte_exact"] is True for record in audit), audit)

    def test_active_qualifications_prove_composite_broken_start(self) -> None:
        sequences = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
        for sequence in sequences:
            if sequence.get("status") != "active":
                continue
            qualification = json.loads((ROOT / sequence["qualification_path"]).read_text())
            self.assertTrue(qualification["composite_seed_merge_zero"])
            self.assertTrue(qualification["composite_seeded_verifiers_nonzero"])
            self.assertEqual(
                set(qualification["composite_seed_verifier_exits"].values()),
                {1},
                "seeded tasks must fail acceptance, not collection or infrastructure",
            )
            self.assertTrue(qualification["full_fixed_cumulative_verifier_zero"])
            self.assertTrue(qualification["fixed_snapshot_model_concealed_paths_safe"])
            self.assertTrue(qualification["composite_seed_diff_sha256"])

    def test_composite_seed_merge_preserves_independent_regressions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, source = self.create_repo(root, "first\nmiddle\nlast\n")
            patches = []
            for order, content in enumerate(("FIRST\nmiddle\nlast\n", "first\nmiddle\nLAST\n"), start=1):
                source.write_text(content)
                patch = root / f"seed-{order}.patch"
                self.create_seed_patch(repo, patch)
                patches.append(patch)
            runner.apply_composite_seed_patches(repo, patches, root / "scratch", root / "merge.json")
            self.assertEqual(source.read_text(), "FIRST\nmiddle\nLAST\n")

    def test_composite_seed_merge_includes_added_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, _ = self.create_repo(root)
            added = repo / "added.txt"
            added.write_text("regression\n")
            subprocess.run(["git", "add", "-N", "added.txt"], cwd=repo, check=True)
            patch = root / "added.patch"
            self.create_seed_patch(repo, patch)
            self.assertFalse(added.exists())
            runner.apply_composite_seed_patches(repo, [patch], root / "scratch", root / "merge.json")
            self.assertEqual(added.read_text(), "regression\n")
            self.assertEqual(json.loads((root / "merge.json").read_text())["patches"][0]["merged_paths"], ["added.txt"])

    def test_conflicted_composite_seed_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, source = self.create_repo(root)
            patches = []
            for order, content in enumerate(("first\n", "second\n"), start=1):
                source.write_text(content)
                patch = root / f"seed-{order}.patch"
                self.create_seed_patch(repo, patch)
                patches.append(patch)
            with self.assertRaisesRegex(RuntimeError, "composite seed conflict"):
                runner.apply_composite_seed_patches(repo, patches, root / "scratch", root / "merge.json")


class VerifierContractTest(unittest.TestCase):
    def test_materialize_task_prompt_recreates_cleaned_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prompt_dir = Path(tmp) / "removed-by-setup" / "task-prompts"
            prompt_path = runner.materialize_task_prompt(prompt_dir, 1, "Repair it.\n")
            self.assertEqual(prompt_path.read_text(), "Repair it.\n")
            self.assertEqual(prompt_path, prompt_dir / "task-01.md")

    def test_final_verifier_runs_every_task_without_short_circuiting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            script = runner.write_verifier({"tasks": [{"order": 1}, {"order": 2}, {"order": 3}]}, Path(tmp), Path(tmp) / "tasks").read_text()
        self.assertNotIn("set -e", script)
        self.assertEqual(script.count("task_status=$?"), 3)
        self.assertEqual(script.count(runner.TASK_VERIFIER_RESULT_PREFIX), 3)
        self.assertGreater(script.index('exit "$status"'), script.rfind(runner.TASK_VERIFIER_RESULT_PREFIX))

    def test_warm_lane_contract_preseeds_all_regressions_and_verifies_once(self) -> None:
        contract = runner.warm_lane_contract({"tasks": [{"order": 1}, {"order": 2}]})
        self.assertEqual(contract["seed_delivery_mode"], "preseeded-composite")
        self.assertTrue(contract["future_seed_regressions_visible"])
        self.assertEqual(contract["controller_verification"], "final-only")

    def test_task_checkpoint_stops_only_on_operational_invalidity(self) -> None:
        self.assertTrue(runner.task_checkpoint_allows_continue(codex_exit_code=0, thread_id="thread", verifier_integrity_passed=True))
        self.assertFalse(runner.task_checkpoint_allows_continue(codex_exit_code=1, thread_id="thread", verifier_integrity_passed=True))

    def test_known_malformed_tool_call_is_retryable_once_with_a_thread(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events = Path(tmp) / "events.jsonl"
            events.write_text("\n".join([
                json.dumps({"type": "thread.started", "thread_id": "thread-1"}),
                json.dumps({"type": "turn.failed", "error": {"message": "failed to parse function arguments: EOF while parsing an object at line 3 column 30072"}}),
            ]) + "\n")
            self.assertEqual(runner.extract_thread_id(events), "thread-1")
            self.assertTrue(runner.retryable_codex_operational_failure(events))

    def test_ordinary_task_failure_is_not_an_operational_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events = Path(tmp) / "events.jsonl"
            events.write_text(json.dumps({"type": "turn.failed", "error": {"message": "task failed"}}) + "\n")
            self.assertFalse(runner.retryable_codex_operational_failure(events))

    def test_codex_task_resumes_once_after_malformed_tool_call(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt = root / "task-01.md"
            prompt.write_text("Repair the task.\n")
            events = root / "task-01-codex-events.jsonl"
            calls = 0
            timeouts: list[int] = []

            def fake_backend(*args: object, **kwargs: object) -> mock.Mock:
                nonlocal calls
                calls += 1
                attempt_timeout = kwargs["timeout"]
                self.assertIsInstance(attempt_timeout, int)
                timeouts.append(attempt_timeout)  # type: ignore[arg-type]
                output = Path(str(kwargs["stdout_path"]))
                if calls == 1:
                    output.write_text("\n".join([
                        json.dumps({"type": "thread.started", "thread_id": "thread-1"}),
                        json.dumps({"type": "turn.failed", "usage": {"input_tokens": 2}, "error": {"message": "failed to parse function arguments: EOF while parsing an object"}}),
                    ]) + "\n")
                    return mock.Mock(returncode=1)
                output.write_text(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}}) + "\n")
                return mock.Mock(returncode=0)

            patches = [
                mock.patch.object(runner.fixture, "active_tool_config", return_value=None),
                mock.patch.object(runner.fixture, "codex_env", return_value={}),
                mock.patch.object(runner.fixture, "tool_env_for_record", return_value={}),
                mock.patch.object(runner.fixture, "codex_model_args", return_value=[]),
                mock.patch.object(runner, "model_mounts_for_record", return_value=[]),
                mock.patch.object(runner.fixture, "run_backend", side_effect=fake_backend),
                mock.patch.object(runner.time, "monotonic", side_effect=[0, 50]),
            ]
            with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6]:
                code, thread = runner.run_codex_task(
                    {"target": {"repository_path": "."}},
                    "baseline-bare-codex",
                    root / "codex-home",
                    root,
                    "image",
                    prompt,
                    events,
                    root / "last-message.txt",
                    timeout=60,
                    thread_id=None,
                )
            self.assertEqual((code, thread, calls), (0, "thread-1", 2))
            self.assertEqual(timeouts, [60, 10])
            self.assertIn("turn.failed", events.read_text())
            self.assertIn("turn.completed", events.read_text())
            combined_events = [json.loads(line) for line in events.read_text().splitlines()]
            usage_blocks = runner.extract_codex_usage.usage_blocks(combined_events)
            self.assertEqual([block["usage"]["input_tokens"] for block in usage_blocks], [2, 1])
            self.assertTrue((root / "task-01-operational-retry-01.md").is_file())

    def test_task_prompts_never_claim_per_task_verification_or_seed_injection(self) -> None:
        sequence = {"id": "unit", "tasks": [{"id": "first", "order": 1}, {"id": "second", "order": 2}]}
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            for order in (1, 2):
                task_dir = runner.task_dir(project, order)
                task_dir.mkdir(parents=True)
                (task_dir / "agent-prompt.txt").write_text("Ticket text\n")
            prompt = runner.task_prompt(sequence, "baseline-bare-codex", project, 1, first_task=True) + runner.task_prompt(sequence, "baseline-bare-codex", project, 2, first_task=False)
        self.assertIn("composite broken start", prompt)
        self.assertIn("concealed verification only after the final task prompt", prompt)
        for forbidden in ("previous task verifier passed", "injected only the current regression", "until this verifier passes"):
            self.assertNotIn(forbidden, prompt.lower())

    def test_generated_prompts_require_cumulative_validation(self) -> None:
        sequence = {"id": "unit", "tasks": [{"id": "first", "order": 1}, {"id": "second", "order": 2}]}
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            for order in (1, 2):
                task_dir = runner.task_dir(project, order)
                task_dir.mkdir(parents=True)
                (task_dir / "agent-prompt.txt").write_text("Ticket text\n")
            prompt = runner.task_prompt(sequence, "baseline-bare-codex", project, 2, first_task=False)
        self.assertIn("Preserve all previously repaired behavior", prompt)
        self.assertIn("Do not stop after syntax checks", prompt)

    def test_active_prompts_name_acceptance_critical_public_contracts(self) -> None:
        cases = {
            "beets-lifecycle-feature-v0": ["field+=value", "field-=value", "UserError"],
            "fastify-lifecycle-feature-v0": ["request.mediaType", "FastifyRequest.mediaType", "application/json"],
            "terraform-lifecycle-feature-v0": ["deferred", "partial response", "data-source callbacks"],
            "terraform-lifecycle-refactor-v0": ["StateStoreProviderRequirement", "exact-version validation", "structural contract"],
        }
        for task_id, required in cases.items():
            task = next(
                task
                for sequence_id in runner.active_sequence_ids()
                for task in runner.load_sequence(sequence_id)["tasks"]
                if task["id"] == task_id
            )
            prompt = (ROOT / task["prompt_path"]).read_text()
            for text in required:
                self.assertIn(text, prompt, task_id)

    def test_all_active_prompts_explain_validation_without_inaccessible_verifier_claims(self) -> None:
        for sequence_id in runner.active_sequence_ids():
            for task in runner.load_sequence(sequence_id)["tasks"]:
                prompt = (ROOT / task["prompt_path"]).read_text()
                self.assertRegex(prompt.lower(), r"validation|run (?:the )?focused.*tests", task["id"])
                self.assertNotIn("Use the fixture verifier", prompt, task["id"])
                self.assertNotIn("seeded with the regression", prompt, task["id"])

    def test_schema_requires_composite_v0_delivery(self) -> None:
        schema = json.loads((ROOT / "schemas/workflow-session-record.schema.json").read_text())
        prompt = schema["properties"]["task_sequence"]["properties"]["prompt_delivery"]["properties"]
        self.assertEqual(prompt["seed_delivery_mode"]["const"], "preseeded-composite")
        self.assertEqual(prompt["controller_verification"]["const"], "final-only")

    def test_functional_task_count_uses_per_task_verifier_outcomes(self) -> None:
        checkpoints = [{"order": 1, "accepted": True}, {"order": 2, "accepted": False}]
        self.assertEqual(runner.functional_task_count(task_checkpoints=checkpoints), 1)

    def test_structured_verifier_results_preserve_partial_correctness(self) -> None:
        sequence = {
            "tasks": [
                {"id": "first-task", "order": 1},
                {"id": "second-task", "order": 2},
                {"id": "third-task", "order": 3},
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "final-verifier-output.txt"
            output.write_text(
                "\n".join(
                    [
                        f"{runner.TASK_VERIFIER_RESULT_PREFIX}\t1\tfirst-task\t1",
                        f"{runner.TASK_VERIFIER_RESULT_PREFIX}\t2\tsecond-task\t0",
                        f"{runner.TASK_VERIFIER_RESULT_PREFIX}\t3\tthird-task\t1",
                    ]
                )
                + "\n"
            )
            results = runner.parse_task_verifier_results(sequence, output)
        self.assertEqual([item["verifier_passed"] for item in results], [False, True, False])
        checkpoints = [
            {"task_id": item["task_id"], "order": item["order"], "accepted": None}
            for item in results
        ]
        applied = runner.apply_task_verifier_results(checkpoints, results)
        self.assertEqual(runner.functional_task_count(task_checkpoints=applied), 1)

    def test_missing_structured_verifier_outcome_fails_closed(self) -> None:
        sequence = {
            "tasks": [
                {"id": "first-task", "order": 1},
                {"id": "second-task", "order": 2},
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "final-verifier-output.txt"
            output.write_text(
                f"{runner.TASK_VERIFIER_RESULT_PREFIX}\t1\tfirst-task\t0\n"
            )
            with self.assertRaisesRegex(ValueError, "missing structured verifier outcomes"):
                runner.parse_task_verifier_results(sequence, output)

    def test_structured_record_contract_rejects_hidden_or_inconsistent_task_outcomes(self) -> None:
        session = {
            "schema_version": 2,
            "session_id": "structured-unit",
            "task_sequence": {"task_ids": ["first-task", "second-task"]},
            "per_task_results": [
                {
                    "task_id": "first-task",
                    "task_alias": "task-01",
                    "order": 1,
                    "agent_attempted": True,
                    "codex_exit_code": 0,
                    "controller_verification": "passed",
                    "verifier_exit_code": 0,
                    "verifier_passed": True,
                    "accepted": True,
                    "operational_retry_count": 0,
                },
                {
                    "task_id": "second-task",
                    "task_alias": "task-02",
                    "order": 2,
                    "agent_attempted": False,
                    "codex_exit_code": None,
                    "controller_verification": "failed",
                    "verifier_exit_code": 1,
                    "verifier_passed": False,
                    "accepted": False,
                    "operational_retry_count": 0,
                },
            ],
            "software_quality": {
                "tasks_attempted": 1,
                "tasks_passed": 1,
                "final_verifier_passed": False,
                "functional_verifier_passed": False,
            },
            "cumulative_token_usage": {
                "measurement_source": "unit",
                "total_provider_tokens": 1,
                "accounting_basis": "provider-reported tokens",
            },
            "execution_integrity": {
                "verifier_integrity_passed": True,
                "tool_isolation_audit_passed": True,
                "external_retrieval_hits": [],
                "pass_through_tool_command_hits": [],
            },
        }
        errors: list[str] = []
        validate_repository.validate_structured_task_outcomes(session, "structured-unit", errors)
        self.assertEqual(errors, [])

        malformed = copy.deepcopy(session)
        malformed["per_task_results"][1] = {}
        malformed["software_quality"]["tasks_passed"] = 2
        errors = []
        validate_repository.validate_structured_task_outcomes(malformed, "structured-unit", errors)
        self.assertTrue(any("exact task coverage" in error for error in errors))
        self.assertTrue(any("tasks_passed" in error for error in errors))

    def test_structured_record_contract_distinguishes_prior_schema(self) -> None:
        prior = {"schema_version": 1}
        current = {"schema_version": 2}
        self.assertFalse(validate_repository.requires_structured_task_contract(prior))
        self.assertTrue(validate_repository.requires_structured_task_contract(current))

    def test_unattempted_tasks_remain_structured_before_final_verification(self) -> None:
        tasks = [
            {"id": "first-task", "order": 1, "task_class": "feature-implementation"},
            {"id": "second-task", "order": 2, "task_class": "behavior-preserving-refactor"},
            {"id": "third-task", "order": 3, "task_class": "code-review-correction"},
        ]
        completed = runner.complete_task_checkpoints(
            tasks,
            [
                {
                    "task_id": "first-task",
                    "order": 1,
                    "agent_attempted": True,
                    "codex_exit_code": 1,
                }
            ],
        )
        self.assertEqual([item["agent_attempted"] for item in completed], [True, False, False])
        self.assertIsNone(completed[1]["codex_exit_code"])
        self.assertEqual(completed[1]["controller_verification"], "deferred-to-final")

    def test_framework_uses_lean_token_only_decision_fields(self) -> None:
        schema = json.loads((ROOT / "schemas/workflow-session-record.schema.json").read_text())
        token_schema = schema["properties"]["cumulative_token_usage"]
        token_fields = token_schema["properties"]
        self.assertNotIn("estimated_cost_usd", token_fields)
        self.assertNotIn("pricing_basis", token_fields)
        self.assertFalse(token_schema["additionalProperties"])
        strict_branch = next(
            branch for branch in schema["allOf"]
            if branch.get("if", {}).get("properties", {}).get("schema_version", {}).get("const") == 2
        )
        self.assertIn(
            "accounting_basis",
            strict_branch["then"]["properties"]["cumulative_token_usage"]["required"],
        )
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        self.assertEqual(registry["primary_metric"], "cumulative provider-reported workflow tokens")
        for session in registry["sessions"]:
            self.assertNotIn("estimated_cost_usd", session["cumulative_token_usage"])
            self.assertNotIn("pricing_basis", session["cumulative_token_usage"])
            self.assertEqual(
                session["baseline_pool"].get("identity_policy"),
                "frozen-protocol-and-replicate; execution date is metadata only",
                session["session_id"],
            )
        for rel in ("AGENTS.md", "data/evaluation-profiles.json"):
            self.assertNotIn("provider-billed", (ROOT / rel).read_text(), rel)
        events = [
            {
                "type": "turn.completed",
                "usage": {
                    "input_tokens": 10,
                    "cached_input_tokens": 2,
                    "output_tokens": 3,
                },
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text("\n".join(json.dumps(item) for item in events) + "\n")
            usage = runner.extract_codex_usage.build_summary(path)
        self.assertNotIn("estimated_cost_usd", usage)

    def test_active_evaluation_run_contract_is_token_only(self) -> None:
        schema = json.loads((ROOT / "schemas/evaluation-run-record.schema.json").read_text())
        template = json.loads((ROOT / "templates/evaluation-run-record.json").read_text())
        token_requirements = schema["properties"]["token_usage"]["required"]
        self.assertNotIn("estimated_cost_usd", token_requirements)
        self.assertNotIn("estimated_cost_usd", template["token_usage"])
        self.assertNotIn("pricing_basis", template["token_usage"])
        self.assertIn("provider-reported", template["agent"]["usage_accounting"])
        self.assertRegex(template["evaluation_id"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def test_reporting_only_runner_hash_does_not_split_comparison_pool(self) -> None:
        sequence = runner.load_sequence(SEQUENCE_ID)
        with mock.patch.object(runner, "_self_hash", return_value="a" * 64):
            first = runner.baseline_protocol_fingerprint(sequence)
        with mock.patch.object(runner, "_self_hash", return_value="b" * 64):
            second = runner.baseline_protocol_fingerprint(sequence)
        self.assertEqual(first, second)

    def test_model_facing_prompt_change_splits_comparison_identity(self) -> None:
        sequence = runner.load_sequence(SEQUENCE_ID)
        original = runner.baseline_protocol_fingerprint(sequence)
        with mock.patch.object(runner, "profile_prompt_guidance", return_value="materially changed guidance\n"):
            changed = runner.baseline_protocol_fingerprint(sequence)
        self.assertNotEqual(original, changed)

    def test_active_task_prompts_include_solution_and_validation_recipes(self) -> None:
        required_by_task = {
            "fastify-lifecycle-feature-v0": ["lib/handle-request.js", "request.mediaType", "app.inject"],
            "fastify-lifecycle-refactor-v0": ["lib/content-type.js", "LruMap", "ContentType.cache"],
            "fastify-lifecycle-review-v0": ["fastify.js", "FST_ERR_MAX_PARAM_LENGTH", "414"],
            "beets-lifecycle-feature-v0": ["beets/ui/commands/modify.py", "field+=value", "test/ui/commands/test_modify.py"],
            "beets-lifecycle-refactor-v0": ["beets/dbcore/db.py", "LazyDict(UserDict)", "test/dbcore/test_db.py"],
            "beets-lifecycle-review-v0": ["beetsplug/ftintitle.py", "albumartist", "test/plugins/test_ftintitle.py"],
            "terraform-lifecycle-feature-v0": ["internal/terraform/policy.go", "GetDeferredResourceInstanceValue", "Context2(Plan|Apply)_PolicyCallback"],
            "terraform-lifecycle-refactor-v0": ["internal/configs/state_migrate_file.go", "StateStoreProviderRequirement", "StateMigration|StateStoreProvider|Migrate"],
            "terraform-lifecycle-review-v0": ["internal/cloud/backend_tfPolicyEvaluation.go", "listTFPolicyOutcomes", "policy-summary"],
        }
        for sequence_id in runner.active_sequence_ids():
            sequence = runner.load_sequence(sequence_id)
            for index, task in enumerate(sorted(sequence["tasks"], key=lambda item: int(item["order"]))):
                source = (ROOT / task["prompt_path"]).read_text()
                self.assertIn("## Implementation recipe", source, task["id"])
                self.assertIn("## Validation recipe", source, task["id"])
                self.assertIn("## Stop condition", source, task["id"])
                for snippet in required_by_task[task["id"]]:
                    self.assertIn(snippet, source, task["id"])
                rendered = runner.render_task_prompt(
                    sequence,
                    "baseline-bare-codex",
                    int(task["order"]),
                    source,
                    first_task=index == 0,
                )
                self.assertIn("## Implementation recipe", rendered, task["id"])
                self.assertIn("## Validation recipe", rendered, task["id"])
                self.assertIn("## Stop condition", rendered, task["id"])

    def test_execution_integrity_preserves_pass_through_command_hits(self) -> None:
        hits = [{"tool": "lowfat", "command": "unknown-command"}]
        integrity = runner.execution_integrity_record(
            {"leakage_controls": {"verifier_integrity_passed": True}},
            0,
            {
                "external_retrieval_hits": [],
                "pass_through_tool_command_hits": hits,
            },
        )
        self.assertEqual(integrity["pass_through_tool_command_hits"], hits)

    def test_fixture_taxonomy_supports_compact_lifecycle_workflow(self) -> None:
        self.assertTrue(
            {"feature-implementation", "behavior-preserving-refactor", "code-review"}.issubset(
                validate_repository.FIXTURE_TASK_CLASSES
            )
        )

    def test_lowfat_estimands_are_explicit_and_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "historical preferred direct-use"):
            runner.assert_profile_runnable("terminal-lowfat")
        with self.assertRaisesRegex(ValueError, "native shell integration"):
            runner.assert_profile_runnable("terminal-lowfat-shell-integrated-v0.8.0")



class ActiveAcceptanceContractTest(unittest.TestCase):
    def test_invalid_fixture_disposition_must_be_excluded_from_comparison(self) -> None:
        session = {
            "status": "failed",
            "interpretation": {
                "evaluation_validity": "invalid-fixture",
                "accepted_for_execution": False,
                "accepted_for_objective": False,
                "primary_objective_hard_baseline": True,
                "usable_for_primary_objective_token_comparison": True,
            },
        }
        errors: list[str] = []
        validate_repository.validate_invalid_fixture_disposition(
            session,
            "invalid-session",
            errors,
        )
        self.assertTrue(errors)

    def test_excluded_invalid_fixture_disposition_is_valid(self) -> None:
        session = {
            "status": "excluded",
            "interpretation": {
                "evaluation_validity": "invalid-fixture",
                "accepted_for_execution": False,
                "accepted_for_objective": False,
                "primary_objective_hard_baseline": False,
                "usable_for_primary_objective_token_comparison": False,
                "invalidity_reasons": ["verifier contract mismatch"],
            },
        }
        errors: list[str] = []
        validate_repository.validate_invalid_fixture_disposition(
            session,
            "invalid-session",
            errors,
        )
        self.assertEqual(errors, [])

    def test_active_qualification_records_match_task_assets(self) -> None:
        for sequence_id in runner.active_sequence_ids():
            sequence = runner.load_sequence(sequence_id)
            self.assertEqual(sequence["acceptance_design"], "behavioral")
            qualification = json.loads((ROOT / sequence["qualification_path"]).read_text())
            records = {item["task_id"]: item for item in qualification["tasks"]}
            for task in sequence["tasks"]:
                patch = ROOT / Path(task["prompt_path"]).parent / "seed-regression.patch"
                changed = validate_repository.patch_paths(patch)
                production = [path for path in changed if validate_repository.is_production_path(path)]
                self.assertGreaterEqual(len(set(production)), 1, task["id"])
                self.assertEqual(records[task["id"]]["production_files"], production)
                self.assertEqual(records[task["id"]]["model_concealed_paths"], sorted(task["model_concealed_paths"]))
                self.assertEqual(records[task["id"]]["omitted_expected_model_concealed_paths"], [])
                self.assertIs(records[task["id"]]["model_concealed_absent"], True)

    def test_expected_concealment_omission_is_rejected(self) -> None:
        task = {
            "upstream_test_paths": ["test/behavior.py"],
            "compatibility_rebased_test_paths": ["test/types.py"],
            "model_concealed_paths": ["test/behavior.py"],
        }
        self.assertEqual(runner.omitted_expected_concealment(task), ["test/types.py"])


class ManifestAndProtocolContractTest(unittest.TestCase):
    def frozen_protocol_doc(
        self,
        protocol_path: Path,
        seq: dict,
        profile_id: str,
        *,
        timeout: int = 3600,
        docker_image: str = runner.DEFAULT_DOCKER_IMAGE,
    ) -> dict:
        descriptor = runner.baseline_protocol_descriptor(seq)
        fingerprint = runner.baseline_protocol_fingerprint(seq)
        selected = runner.execution_condition_descriptor(seq, profile_id, timeout_seconds_per_task=timeout, docker_image=docker_image)
        command = (
            f"python3 scripts/run_codex_workflow_evaluation.py --sequence-id {seq['id']} "
            f"--profile-id {profile_id} --replicate-index 0 --timeout-per-task {timeout} "
            f"--protocol {protocol_path} --docker-image {docker_image}"
        )
        return {
            "protocol_schema_version": 3,
            "protocol_id": "unit-production-v3",
            "status": "frozen-ready-not-run",
            "task_fixture": {
                "fixture_id": seq["fixture_id"],
                "sequence_id": seq["id"],
                "snapshot": seq["initial_snapshot"]["commit"],
                "timeout_seconds_per_task": timeout,
                "qualification_path": seq["qualification_path"],
                "qualification_sha256": runner._protocol_file_hash(ROOT / seq["qualification_path"]),
            },
            "baseline_pool": {
                "protocol_version": runner.BASELINE_POOL_PROTOCOL_VERSION,
                "protocol_fingerprint": fingerprint,
                "descriptor": descriptor,
            },
            "selected_execution": {
                "descriptor_sha256": runner._json_hash(selected),
                "descriptor": selected,
            },
            "baseline": {
                "profile_id": "baseline-bare-codex",
                "provider": "openai",
                "model": runner.DEFAULT_WORKFLOW_MODEL,
                "reasoning_effort": runner.DEFAULT_WORKFLOW_REASONING_EFFORT,
                "command": command if profile_id == "baseline-bare-codex" else "baseline command",
            },
            "treatment": {
                "profile_id": "" if profile_id == "baseline-bare-codex" else profile_id,
                "provider": "openai",
                "model": runner.DEFAULT_WORKFLOW_MODEL,
                "reasoning_effort": runner.DEFAULT_WORKFLOW_REASONING_EFFORT,
                "command": command if profile_id != "baseline-bare-codex" else "",
            },
        }

    def test_manifest_digest_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            root = Path(tmp)
            for name in ("run.json", "changes.diff", "evidence.jsonl.gz"):
                (root / name).write_text(name)
            (root / "manifest.sha256").write_text("0" * 64 + "  run.json\n")
            errors: list[str] = []
            validate_repository.validate_compact_manifest(root, "test", errors)
        self.assertTrue(any("manifest" in error for error in errors))

    def test_active_default_is_gpt_5_6_luna_xhigh(self) -> None:
        self.assertEqual(runner.DEFAULT_WORKFLOW_MODEL_CONDITION_ID, "codex-openai-gpt-5-6-luna-xhigh")
        self.assertEqual(runner.DEFAULT_WORKFLOW_MODEL, "gpt-5.6-luna")
        self.assertEqual(runner.DEFAULT_WORKFLOW_REASONING_EFFORT, "xhigh")
        registry = json.loads((ROOT / "data/evaluation-agent-runtimes.json").read_text())
        active = [item for item in registry["model_conditions"] if item["status"] == "active-default"]
        self.assertEqual([item["id"] for item in active], ["codex-openai-gpt-5-6-luna-xhigh"])

    def test_active_sequences_are_the_three_current_production_lanes(self) -> None:
        self.assertEqual(
            runner.active_sequence_ids(),
            [
                "fastify-lifecycle-sequence-v0",
                "beets-lifecycle-sequence-v0",
                "terraform-lifecycle-sequence-v0",
            ],
        )
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        self.assertEqual(
            [task["id"] for task in sequence["tasks"]],
            [
                "beets-lifecycle-feature-v0",
                "beets-lifecycle-refactor-v0",
                "beets-lifecycle-review-v0",
            ],
        )
        self.assertEqual([task["order"] for task in sequence["tasks"]], [1, 2, 3])

    def test_active_sequences_bind_current_qualifications(self) -> None:
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        self.assertRegex(
            Path(sequence["qualification_path"]).name,
            r"^qualification-lifecycle-v0(?:-[a-z0-9-]+)?\.json$",
        )

    def test_current_protocol_fingerprint_matches_runner(self) -> None:
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        protocol_path = matrix.find_protocol(
            ROOT,
            "beets-lifecycle-sequence-v0",
            "baseline-bare-codex",
        )
        protocol = json.loads(protocol_path.read_text())
        expected = runner.baseline_protocol_fingerprint(sequence)
        self.assertEqual(protocol["baseline_pool"]["protocol_fingerprint"], expected)
        self.assertEqual(
            protocol["baseline_pool"]["descriptor"]["tasks"],
            runner.baseline_protocol_descriptor(sequence)["tasks"],
        )

    def test_existing_pool_record_blocks_duplicate_provider_sample(self) -> None:
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        sequence = runner.load_sequence("fastify-lifecycle-sequence-v0")
        retained = next(
            session
            for session in registry["sessions"]
            if session.get("task_sequence", {}).get("sequence_id") == sequence["id"]
            and session.get("profile", {}).get("profile_id") == "baseline-bare-codex"
            and session.get("replicate_index") == 0
        )
        with mock.patch.object(
            runner,
            "baseline_protocol_fingerprint",
            return_value=retained["baseline_pool"]["protocol_fingerprint"],
        ):
            with self.assertRaisesRegex(ValueError, "already occupied"):
                runner.assert_pool_slot_available(
                    registry,
                    sequence,
                    "baseline-bare-codex",
                    0,
                )

    def test_protocol_is_required_before_setup_for_paid_run(self) -> None:
        seq = runner.load_sequence(SEQUENCE_ID)
        args = mock.Mock(protocol=None, prepare_only=False, no_provider=False)
        with self.assertRaisesRegex(ValueError, "--protocol is required"):
            runner.validate_protocol_for_run(seq, "baseline-bare-codex", args)

    def test_protocol_is_required_for_no_provider_prepare_only(self) -> None:
        seq = runner.load_sequence(SEQUENCE_ID)
        args = mock.Mock(protocol=None, prepare_only=True, no_provider=True)
        with self.assertRaisesRegex(ValueError, "--protocol is required"):
            runner.validate_protocol_for_run(seq, "baseline-bare-codex", args)

    def test_protocol_timeout_mismatch_rejects(self) -> None:
        seq = runner.load_sequence(SEQUENCE_ID)
        args = mock.Mock(
            protocol=str(retained_protocol_path(SEQUENCE_ID, "baseline-bare-codex").relative_to(ROOT)),
            prepare_only=False,
            no_provider=False,
            timeout_per_task=1,
            docker_image=runner.DEFAULT_DOCKER_IMAGE,
        )
        with self.assertRaisesRegex(ValueError, "timeout"):
            runner.validate_protocol_for_run(seq, "baseline-bare-codex", args)

    def test_protocol_docker_image_mismatch_rejects(self) -> None:
        seq = runner.load_sequence(SEQUENCE_ID)
        args = mock.Mock(
            protocol=str(retained_protocol_path(SEQUENCE_ID, "baseline-bare-codex").relative_to(ROOT)),
            prepare_only=True,
            no_provider=True,
            timeout_per_task=3600,
            docker_image="synthetic:latest",
        )
        with self.assertRaisesRegex(RuntimeError, "docker image inspect failed"):
            runner.validate_protocol_for_run(seq, "baseline-bare-codex", args)

    def test_baseline_protocol_cannot_validate_treatment(self) -> None:
        seq = runner.load_sequence(SEQUENCE_ID)
        args = mock.Mock(
            protocol=str(retained_protocol_path(SEQUENCE_ID, "baseline-bare-codex").relative_to(ROOT)),
            prepare_only=True,
            no_provider=True,
            timeout_per_task=3600,
            docker_image=runner.DEFAULT_DOCKER_IMAGE,
        )
        with self.assertRaisesRegex(ValueError, "selected_execution|treatment_profile_id"):
            runner.validate_protocol_for_run(seq, "terminal-tokenjuice-codex-hook-v1", args)

    def test_same_docker_tag_different_image_id_rejects(self) -> None:
        seq = runner.load_sequence(SEQUENCE_ID)
        image_a = {"image_ref": runner.DEFAULT_DOCKER_IMAGE, "image_id": "sha256:" + "1" * 64, "repo_digests": [], "repo_tags": [runner.DEFAULT_DOCKER_IMAGE]}
        image_b = {"image_ref": runner.DEFAULT_DOCKER_IMAGE, "image_id": "sha256:" + "2" * 64, "repo_digests": [], "repo_tags": [runner.DEFAULT_DOCKER_IMAGE]}
        with tempfile.TemporaryDirectory() as tmp:
            protocol_path = Path(tmp) / "protocol.json"
            with mock.patch.object(runner, "docker_image_identity", return_value=image_a):
                protocol_path.write_text(json.dumps(self.frozen_protocol_doc(protocol_path, seq, "baseline-bare-codex"), indent=2) + "\n")
            args = mock.Mock(protocol=str(protocol_path), prepare_only=True, no_provider=True, timeout_per_task=3600, docker_image=runner.DEFAULT_DOCKER_IMAGE)
            with mock.patch.object(runner, "docker_image_identity", return_value=image_b):
                with self.assertRaisesRegex(ValueError, "descriptor|selected_execution|protocol_fingerprint"):
                    runner.validate_protocol_for_run(seq, "baseline-bare-codex", args)

    def test_treatment_executable_identity_mismatch_rejects(self) -> None:
        seq = runner.load_sequence(SEQUENCE_ID)
        image = {"image_ref": runner.DEFAULT_DOCKER_IMAGE, "image_id": "sha256:" + "1" * 64, "repo_digests": [], "repo_tags": [runner.DEFAULT_DOCKER_IMAGE]}
        binary_a = {"executable_token": "codegraph", "resolved_path": "/tmp/codegraph", "realpath": "/tmp/codegraph", "sha256": "a" * 64, "metadata": {}, "version": {"captured": True, "output": "codegraph 1"}}
        binary_b = {"executable_token": "codegraph", "resolved_path": "/tmp/codegraph", "realpath": "/tmp/codegraph", "sha256": "b" * 64, "metadata": {}, "version": {"captured": True, "output": "codegraph 2"}}
        with tempfile.TemporaryDirectory() as tmp:
            protocol_path = Path(tmp) / "protocol.json"
            with mock.patch.object(runner, "docker_image_identity", return_value=image), mock.patch.object(runner, "executable_identity", return_value=binary_a):
                protocol_path.write_text(json.dumps(self.frozen_protocol_doc(protocol_path, seq, "terminal-tokenjuice-codex-hook-v1"), indent=2) + "\n")
            args = mock.Mock(protocol=str(protocol_path), prepare_only=True, no_provider=True, timeout_per_task=3600, docker_image=runner.DEFAULT_DOCKER_IMAGE)
            with mock.patch.object(runner, "docker_image_identity", return_value=image), mock.patch.object(runner, "executable_identity", return_value=binary_b):
                with self.assertRaisesRegex(ValueError, "selected_execution"):
                    runner.validate_protocol_for_run(seq, "terminal-tokenjuice-codex-hook-v1", args)

    def test_unresolved_treatment_executable_rejects_identity(self) -> None:
        profile_id = "unit-missing-tool-profile"
        tool_id = "unit-missing-tool"
        profile = {
            "session_role": "individual_tool_treatment",
            "profile_type": "individual_tool",
            "component_ids": [tool_id],
            "enabled_surfaces": ["terminal/tool-output-compaction"],
            "disabled_overlaps": [],
            "allowed_terms": [tool_id],
            "tool_state": "available",
            "tool_use_policy": "optional",
            "tool_id": tool_id,
        }
        cfg = {
            "display_name": "Missing Tool",
            "mcp_command": "definitely-not-present-token-optimization-test",
            "mcp_args": ["--serve"],
            "mounts": [],
        }
        with mock.patch.dict(runner.PROFILE_META, {profile_id: profile}), mock.patch.dict(runner.fixture.TOOL_CONFIGS, {tool_id: cfg}):
            with self.assertRaisesRegex(FileNotFoundError, "not resolvable"):
                runner.tool_adapter_identity(profile_id)

    def test_registry_not_updated_when_finalization_fails(self) -> None:
        with mock.patch.object(runner, "remove_ephemeral_homes"), \
            mock.patch.object(runner, "write_evidence_bundle", side_effect=RuntimeError("finalize failed")), \
            mock.patch.object(runner, "update_registry") as update_registry:
            with self.assertRaisesRegex(RuntimeError, "finalize failed"):
                runner.write_evidence_bundle(Path("/tmp/nonexistent"))
            update_registry.assert_not_called()

    def production_v3_fixture(self, root: Path) -> tuple[dict, Path]:
        run_dir = root / "session"
        run_dir.mkdir()
        docker_identity = {
            "image_ref": "codex-eval:unit",
            "image_id": "sha256:" + "1" * 64,
            "repo_digests": ["codex-eval@sha256:" + "2" * 64],
            "repo_tags": ["codex-eval:unit"],
        }
        tool_identity = {
            "tool_id": "unit-tool",
            "tool_manifest": "unit",
            "tool_config": {},
            "binary_identity": {
                "executable_token": "unit-tool",
                "resolved_path": "/tmp/unit-tool",
                "realpath": "/tmp/unit-tool",
                "sha256": "3" * 64,
                "metadata": {"size": 1, "mode": "-rwxr-xr-x", "uid": 1, "gid": 1, "mtime_ns": 1},
                "version": {"command": ["/tmp/unit-tool", "--version"], "captured": True, "exit_code": 0, "output": "unit 1", "truncated": False},
            },
            "source_identity": [],
        }
        descriptor = {
            "version": "execution-condition-v1",
            "sequence_id": "unit-sequence",
            "execution_role": "individual_tool_treatment",
            "selected_profile": {"profile_id": "unit-profile"},
            "tool_adapter": json.loads(json.dumps(tool_identity)),
            "runtime": {"docker_image": "codex-eval:unit", "docker_image_identity": json.loads(json.dumps(docker_identity))},
        }
        selected = {"descriptor_sha256": validate_repository.canonical_json_hash(descriptor), "descriptor": descriptor}
        protocol = {
            "protocol_id": "unit-production-v3",
            "baseline_pool": {"protocol_version": "baseline-pool-v1", "protocol_fingerprint": "abcdef123456"},
            "selected_execution": selected,
        }
        protocol_path = root / "protocol.json"
        protocol_path.write_text(json.dumps(protocol, sort_keys=True) + "\n")
        frozen_protocol = {
            "protocol_id": protocol["protocol_id"],
            "path": str(protocol_path.relative_to(ROOT)),
            "sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        }
        session = {
            "schema_version": 1,
            "session_id": "unit-production-session",
            "record_type": "workflow_session",
            "evidence_type": "workflow-simulation",
            "study_id": "unit-study",
            "experiment_group_id": "unit-group",
            "objective": "individual_tool_effectiveness",
            "evidence_stage": "reproduction",
            "status": "failed",
            "session_role": "individual_tool_treatment",
            "replicate_index": 0,
            "frozen_protocol": frozen_protocol,
            "baseline_pool": {
                "protocol_version": "baseline-pool-v1",
                "protocol_fingerprint": "abcdef123456",
                "identity_policy": "frozen-protocol-and-replicate; execution date is metadata only",
            },
            "selected_execution": selected,
            "docker_image_identity": json.loads(json.dumps(docker_identity)),
            "tool_adapter_identity": json.loads(json.dumps(tool_identity)),
            "date": "2026-07-11",
            "target": {"fixture_id": "unit-fixture", "fixture_scale": "medium-project", "project_id": "unit", "repository_path": "tmp/repo", "initial_snapshot": {}},
            "task_sequence": {
                "sequence_id": "unit-sequence",
                "task_ids": ["task-1"],
                "reset_policy": "reset",
                "prompt_delivery": {
                    "mode": "sequential-one-task-at-a-time",
                    "future_tasks_visible": False,
                    "future_prompts_materialized_lazily": True,
                    "seed_delivery_mode": "preseeded-composite",
                    "future_seed_regressions_visible": True,
                    "controller_verification": "final-only",
                },
                "leakage_controls": {
                    "seed_origin_concealed": True,
                    "seed_patches_model_visible": False,
                    "git_baseline_true_root_at_lane_start": True,
                    "fixed_snapshot_objects_model_visible": False,
                    "pre_seed_reflog_entries_visible": False,
                    "concealment_verification_passed": True,
                    "task_directories_model_visible": False,
                    "verifier_assets_model_visible": False,
                    "verifier_integrity_passed": True,
                },
            },
            "profile": {
                "profile_id": "unit-profile",
                "profile_type": "individual_tool",
                "enabled_surfaces": ["terminal/tool-output-compaction"],
                "disabled_overlaps": [],
                "component_ids": ["unit-tool"],
            },
            "agent": {
                "runtime_id": "unit-runtime",
                "model_condition_id": "unit-model",
                "name": "Codex CLI",
                "version": "unit",
                "model": "gpt-unit",
                "provider": "openai",
                "reasoning_effort": "medium",
                "temperature": None,
                "max_turns": None,
                "time_budget_seconds": 1,
            },
            "state_policy": {"reset_before_session": [], "persist_between_tasks": []},
            "cumulative_token_usage": {"measurement_source": "unit", "total_provider_tokens": None, "accounting_basis": "unit-test provider usage"},
            "per_task_results": [],
            "software_quality": {"functional_verifier_passed": False, "quality_review_status": "not-reviewed", "quality_score": None, "critical_failures": []},
            "state_observations": {},
            "operational_reproducibility": {},
            "artifacts": {
                "artifact_contract": "compact-v1-four-files",
                "run_record": str((run_dir / "run.json").relative_to(ROOT)),
                "final_diff": str((run_dir / "changes.diff").relative_to(ROOT)),
                "evidence_bundle": str((run_dir / "evidence.jsonl.gz").relative_to(ROOT)),
                "manifest": str((run_dir / "manifest.sha256").relative_to(ROOT)),
            },
            "interpretation": {"accepted_for_execution": False, "accepted_for_objective": False, "claim_status": "failed", "exclusion_reason": "unit"},
        }
        run_payload = {key: session[key] for key in ("frozen_protocol", "baseline_pool", "selected_execution", "docker_image_identity", "tool_adapter_identity")}
        (run_dir / "run.json").write_text(json.dumps(run_payload, indent=2) + "\n")
        (run_dir / "changes.diff").write_text("")
        (run_dir / "evidence.jsonl.gz").write_text("")
        runner.write_manifest(run_dir)
        return session, protocol_path

    def production_v3_errors(self, session: dict) -> list[str]:
        errors: list[str] = []
        validate_repository.validate_workflow_sessions(
            {"schema_version": 1, "primary_metric": "cumulative provider-reported workflow tokens", "sessions": [session]},
            {"unit-sequence"},
            {"fixtures": [{"id": "unit-fixture"}]},
            {
                "unit-profile": {
                    "profile_type": "individual_tool",
                    "enabled_surfaces": ["terminal/tool-output-compaction"],
                    "disabled_overlaps": [],
                    "components": [{"component_id": "unit-tool"}],
                }
            },
            {"unit-runtime"},
            {"unit-model"},
            errors,
        )
        return errors

    def test_production_v3_identity_record_accepts_matching_payload(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            self.assertEqual(self.production_v3_errors(session), [])

    def test_production_v3_lean_record_does_not_require_optional_operational_metrics(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            session.pop("state_observations")
            session.pop("operational_reproducibility")
            session["execution_integrity"] = {
                "verifier_integrity_passed": True,
                "tool_isolation_audit_passed": True,
                "external_retrieval_hits": [],
                "pass_through_tool_command_hits": [],
            }
            self.assertEqual(self.production_v3_errors(session), [])

    def test_objective_acceptance_rejects_failed_execution_integrity(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            session.update(schema_version=2, status="completed")
            session["cumulative_token_usage"].update(
                measurement_source="codex-jsonl-usage-events",
                total_provider_tokens=1,
            )
            session["per_task_results"] = [{
                "task_id": "task-1",
                "task_alias": "task-01",
                "order": 1,
                "agent_attempted": True,
                "codex_exit_code": 0,
                "controller_verification": "passed",
                "verifier_exit_code": 0,
                "verifier_passed": True,
                "accepted": True,
                "operational_retry_count": 0,
            }]
            session["software_quality"].update(
                tasks_attempted=1,
                tasks_passed=1,
                final_verifier_passed=True,
                functional_verifier_passed=True,
                quality_review_status="reviewed",
                quality_score=4,
            )
            session["execution_integrity"] = {
                "verifier_integrity_passed": True,
                "tool_isolation_audit_passed": False,
                "external_retrieval_hits": ["unit retrieval"],
                "pass_through_tool_command_hits": [],
            }
            session["interpretation"].update(
                accepted_for_execution=True,
                accepted_for_objective=True,
            )
            errors = self.production_v3_errors(session)
            self.assertTrue(any("clean execution integrity" in error for error in errors), errors)

    def test_token_objective_accepts_unreviewed_verifier_failure(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            session.update(schema_version=2, status="completed")
            session["cumulative_token_usage"].update(
                measurement_source="codex-jsonl-usage-events",
                total_provider_tokens=1000,
            )
            session["per_task_results"] = [{
                "task_id": "task-1",
                "task_alias": "task-01",
                "order": 1,
                "agent_attempted": True,
                "codex_exit_code": 0,
                "controller_verification": "failed",
                "verifier_exit_code": 1,
                "verifier_passed": False,
                "accepted": False,
                "operational_retry_count": 0,
            }]
            session["software_quality"].update(
                tasks_attempted=1,
                tasks_passed=0,
                final_verifier_passed=False,
                functional_verifier_passed=False,
                quality_review_status="not-reviewed",
                quality_score=None,
                critical_failures=["sampled model output failed verification"],
            )
            session["execution_integrity"] = {
                "verifier_integrity_passed": True,
                "tool_isolation_audit_passed": True,
                "external_retrieval_hits": [],
                "pass_through_tool_command_hits": [],
            }
            session["interpretation"].update(
                accepted_for_execution=True,
                accepted_for_objective=True,
                claim_status="token-accounting-eligible",
                exclusion_reason="",
            )
            self.assertEqual(self.production_v3_errors(session), [])

    def test_production_v3_protocol_hash_tamper_rejects(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            session["frozen_protocol"]["sha256"] = "0" * 64
            self.assertTrue(any("frozen protocol sha256" in error for error in self.production_v3_errors(session)))

    def test_production_v3_selected_descriptor_hash_tamper_rejects(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            session["selected_execution"]["descriptor_sha256"] = "0" * 64
            self.assertTrue(any("descriptor_sha256" in error for error in self.production_v3_errors(session)))

    def test_production_v3_selected_descriptor_tamper_rejects(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            session["selected_execution"]["descriptor"]["runtime"]["docker_image"] = "changed"
            session["selected_execution"]["descriptor_sha256"] = validate_repository.canonical_json_hash(session["selected_execution"]["descriptor"])
            self.assertTrue(any("selected_execution does not match frozen protocol" in error for error in self.production_v3_errors(session)))

    def test_production_v3_docker_image_id_tamper_rejects(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            session["docker_image_identity"]["image_id"] = "sha256:" + "4" * 64
            self.assertTrue(any("Docker image identity does not match selected_execution descriptor" in error for error in self.production_v3_errors(session)))

    def test_production_v3_treatment_executable_hash_tamper_rejects(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            session["tool_adapter_identity"]["binary_identity"]["sha256"] = "4" * 64
            self.assertTrue(any("treatment tool identity does not match selected_execution descriptor" in error for error in self.production_v3_errors(session)))

    def test_production_v3_run_json_identity_tamper_rejects(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            run_path = ROOT / session["artifacts"]["run_record"]
            payload = json.loads(run_path.read_text())
            payload["docker_image_identity"]["image_id"] = "sha256:" + "4" * 64
            run_path.write_text(json.dumps(payload, indent=2) + "\n")
            runner.write_manifest(run_path.parent)
            self.assertTrue(any("run.json docker_image_identity does not match registry session" in error for error in self.production_v3_errors(session)))


class ModelConditionLauncherContractTest(unittest.TestCase):
    def test_registered_gpt55_high_condition_is_selectable(self) -> None:
        condition = model_condition_runner.registered_condition(
            "codex-openai-gpt-5-5-high", "gpt-5.5", "high"
        )
        self.assertEqual(condition["status"], "historical-inactive")
        identity = model_condition_runner.launcher_identity()
        self.assertRegex(identity["sha256"], r"^[a-f0-9]{64}$")

    def test_registered_gpt56_sol_high_condition_is_selectable(self) -> None:
        condition = model_condition_runner.registered_condition(
            "codex-openai-gpt-5-6-sol-high", "gpt-5.6-sol", "high"
        )
        self.assertEqual(condition["status"], "active-model-comparison")

    def test_registered_model_condition_protocols_validate(self) -> None:
        errors: list[str] = []
        validate_repository.validate_frozen_protocol_bindings(errors)
        sol_protocol_errors = [
            error for error in errors
            if any(protocol_id in error for protocol_id in (
                "beets-lifecycle-sequence-v0-baseline-bare-codex-b76903081a2d",
                "fastify-lifecycle-sequence-v0-baseline-bare-codex-3f3ce79ce469",
                "terraform-lifecycle-sequence-v0-baseline-bare-codex-8bba1cd949b1",
            ))
        ]
        self.assertEqual(sol_protocol_errors, [])

    def test_unregistered_override_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            model_condition_runner.registered_condition("missing", "gpt-missing", "high")


class MatrixLifecycleContractTest(unittest.TestCase):
    def test_lane_command_propagates_replicate_index_explicitly(self) -> None:
        cmd = matrix.workflow_lane_command(
            sequence_id="fastify-lifecycle-sequence-v0",
            profile_id="behavior-caveman",
            protocol=Path("sources/evaluations/protocols/caveman.json"),
            replicate_index=1,
            runner_args=["--timeout-per-task", "30"],
        )
        self.assertEqual(cmd[cmd.index("--replicate-index") + 1], "1")
        self.assertEqual(
            cmd[cmd.index("--timeout-per-task") : cmd.index("--timeout-per-task") + 2],
            ["--timeout-per-task", "30"],
        )

    def test_lane_command_uses_registered_model_condition_launcher(self) -> None:
        cmd = matrix.workflow_lane_command(
            sequence_id="fastify-lifecycle-sequence-v0",
            profile_id="baseline-bare-codex",
            protocol=Path("sources/evaluations/protocols/sol.json"),
            replicate_index=2,
            runner_args=[],
            model_condition={
                "id": "codex-openai-gpt-5-6-sol-high",
                "model": "gpt-5.6-sol",
                "reasoning_effort": "high",
            },
        )
        self.assertEqual(cmd[1], "scripts/run_codex_workflow_model_condition.py")
        self.assertEqual(cmd[cmd.index("--workflow-model-condition-id") + 1], "codex-openai-gpt-5-6-sol-high")
        self.assertEqual(cmd[cmd.index("--workflow-model") + 1], "gpt-5.6-sol")
        self.assertEqual(cmd[cmd.index("--workflow-reasoning-effort") + 1], "high")

    def test_matrix_model_condition_arguments_must_be_complete(self) -> None:
        args = matrix.parse_args([
            "--workflow-model-condition-id", "codex-openai-gpt-5-6-sol-high",
        ])
        with self.assertRaises(SystemExit):
            matrix.selected_model_condition(args)

    def test_missing_protected_control_plane_test_is_restored_before_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protected = root / "scripts/test_workflow_evaluation_contract.py"
            protected.parent.mkdir(parents=True)
            protected.write_text("protected\n")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", str(protected.relative_to(root))], cwd=root, check=True)
            subprocess.run(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture"],
                cwd=root,
                check=True,
            )
            protected.unlink()
            matrix.restore_protected_control_plane_files(root)
            self.assertEqual(protected.read_text(), "protected\n")

    def test_controller_refreshes_generated_runbook_before_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "scripts/update_workflow_runbook.py"
            script.parent.mkdir(parents=True)
            script.write_text("from pathlib import Path\nPath('refreshed').write_text('yes')\n")
            matrix.refresh_generated_runbook(root)
            self.assertEqual((root / "refreshed").read_text(), "yes")

    def test_prepare_only_summary_cannot_claim_objective_acceptance(self) -> None:
        self.assertIsNone(
            matrix.matrix_acceptance_state(
                prepare_only=True,
                execution_passed=True,
                awaiting_quality_review=False,
            )
        )
        self.assertTrue(
            matrix.matrix_acceptance_state(
                prepare_only=False,
                execution_passed=True,
                awaiting_quality_review=False,
            )
        )
        self.assertTrue(
            matrix.matrix_acceptance_state(
                prepare_only=False,
                execution_passed=True,
                awaiting_quality_review=True,
            )
        )
        self.assertEqual(
            matrix.matrix_exit_code(
                prepare_only=True,
                execution_passed=True,
                awaiting_quality_review=False,
                accepted=None,
            ),
            0,
        )
        self.assertEqual(
            matrix.matrix_exit_code(
                prepare_only=True,
                execution_passed=False,
                awaiting_quality_review=False,
                accepted=None,
            ),
            1,
        )

    def test_failed_lane_cannot_publish(self) -> None:
        self.assertFalse(matrix.publication_allowed(False, [{"exit_code": 1}]))
        self.assertFalse(matrix.publication_allowed(True, [{"exit_code": 0}]))
        self.assertTrue(matrix.publication_allowed(False, [{"exit_code": 0}]))

    def test_completed_sessions_merge_even_when_a_sibling_lane_fails(self) -> None:
        results = [
            {"exit_code": 0, "produced_session_ids": ["successful-session"]},
            {"exit_code": 1, "produced_session_ids": ["hard-baseline-session"]},
        ]
        self.assertTrue(matrix.artifact_merge_allowed(False, results))
        self.assertFalse(matrix.artifact_merge_allowed(True, results))
        self.assertFalse(matrix.publication_allowed(False, results))

    def test_missing_baseline_collapses_treatments_to_one_baseline_lane(self) -> None:
        jobs = matrix.plan_workflow_jobs(
            [SEQUENCE_ID],
            ["terminal-rtk", "terminal-codegraph"],
            baseline_state=lambda _sequence: "missing",
            profile_state=lambda _sequence, _profile: "missing",
        )
        self.assertEqual(jobs, [(SEQUENCE_ID, "baseline-bare-codex")])

    def test_superseded_hard_baseline_is_not_reused_after_contract_change(self) -> None:
        sequence = runner.load_sequence("fastify-lifecycle-sequence-v0")
        registry = {
            "sessions": [{
                "session_id": "superseded-hard-baseline",
                "replicate_index": 0,
                "baseline_pool": {"protocol_fingerprint": "superseded"},
                "task_sequence": {"sequence_id": sequence["id"]},
                "profile": {"profile_id": "baseline-bare-codex"},
            }]
        }
        baseline = matrix.find_baseline_record(registry, sequence, 0)
        self.assertIsNone(baseline)

    def test_quality_rejected_green_baseline_is_reusable_as_primary_hard_evidence(self) -> None:
        session = {
            "interpretation": {
                "accepted_for_objective": False,
                "primary_objective_hard_baseline": True,
                "usable_for_primary_objective_token_comparison": True,
                "operationally_completed": True,
                "agent_declared_task_completion_count": 5,
            },
            "software_quality": {
                "tasks_attempted": 5,
                "quality_review_status": "reviewed",
                "final_verifier_passed": True,
                "quality_score": 3,
            },
            "cumulative_token_usage": {"total_provider_tokens": 1000},
        }
        with mock.patch.object(matrix, "compact_artifacts_intact", return_value=True):
            self.assertTrue(matrix.hard_baseline_usable(session))
            self.assertEqual(matrix.baseline_reuse_state(session), "reusable")

    def test_invalid_fixture_run_is_never_reusable_as_a_hard_baseline(self) -> None:
        session = {
            "interpretation": {
                "accepted_for_objective": False,
                "primary_objective_hard_baseline": True,
                "usable_for_primary_objective_token_comparison": True,
                "operationally_completed": True,
                "agent_declared_task_completion_count": 3,
                "evaluation_validity": "invalid-fixture",
            },
            "software_quality": {
                "tasks_attempted": 3,
                "quality_review_status": "reviewed",
                "final_verifier_passed": False,
                "quality_score": 4,
            },
            "cumulative_token_usage": {"total_provider_tokens": 26417006},
        }
        with mock.patch.object(matrix, "compact_artifacts_intact", return_value=True):
            self.assertFalse(matrix.hard_baseline_usable(session))

    def test_rejected_replicate_is_occupied_and_not_planned_again(self) -> None:
        sequence = {"id": "unit-sequence"}
        rejected = {
            "schema_version": 2,
            "status": "excluded",
            "replicate_index": 0,
            "session_role": "baseline",
            "baseline_pool": {"protocol_fingerprint": "unit-fingerprint"},
            "task_sequence": {"sequence_id": "unit-sequence"},
            "profile": {"profile_id": "baseline-bare-codex"},
            "interpretation": {
                "accepted_for_execution": False,
                "accepted_for_objective": False,
                "evaluation_validity": "invalid-fixture",
            },
        }
        registry = {"sessions": [rejected]}
        with mock.patch.object(
            matrix.workflow,
            "baseline_protocol_fingerprint",
            return_value="unit-fingerprint",
        ):
            self.assertEqual(
                matrix.baseline_campaign_state(registry, sequence, 0),
                "occupied",
            )
        with self.assertRaisesRegex(ValueError, "occupied"):
            matrix.plan_workflow_jobs(
                ["unit-sequence"],
                [],
                baseline_state=lambda _sequence: "occupied",
                profile_state=lambda _sequence, _profile: "missing",
            )

    def test_unreviewed_operational_baseline_is_hard_reusable(self) -> None:
        session = {
            "interpretation": {
                "accepted_for_objective": True,
                "primary_objective_hard_baseline": True,
                "usable_for_primary_objective_token_comparison": True,
                "operationally_completed": True,
                "agent_declared_task_completion_count": 5,
            },
            "software_quality": {
                "tasks_attempted": 5,
                "quality_review_status": "not-reviewed",
                "final_verifier_passed": False,
                "quality_score": None,
            },
            "cumulative_token_usage": {"total_provider_tokens": 1000},
        }
        with mock.patch.object(matrix, "compact_artifacts_intact", return_value=True):
            self.assertTrue(matrix.hard_baseline_usable(session))

    def test_primary_token_comparison_is_not_quality_gated(self) -> None:
        sequence = runner.load_sequence("fastify-lifecycle-sequence-v0")
        baseline = {
            "session_id": "hard-baseline",
            "study_id": "study",
            "cumulative_token_usage": {"total_provider_tokens": 1000},
            "software_quality": {"tasks_agent_claimed_complete": 3, "tasks_passed": 3},
        }
        treatment = {
            "session_id": "treatment",
            "study_id": "phase-3-stack-study",
            "objective": "stack_effectiveness",
            "experiment_group_id": "group",
            "cumulative_token_usage": {"total_provider_tokens": 900},
            "software_quality": {"tasks_agent_claimed_complete": 3, "tasks_passed": 1},
        }
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(matrix, "ROOT", Path(tmp)):
            path = matrix.write_hard_baseline_comparison(sequence, baseline, treatment, "terminal-rtk", 0)
            comparison = json.loads(path.read_text())
        self.assertFalse(comparison["correctness_improved"])
        self.assertEqual(comparison["study_id"], "phase-3-stack-study")
        self.assertEqual(comparison["objective"], "stack_effectiveness")
        self.assertTrue(comparison["token_efficiency_improved"])
        self.assertTrue(comparison["primary_token_objective_improved"])
        self.assertNotIn("treatment_outperforms_baseline", comparison)
        self.assertNotIn("eligible_for_hard_lane_ranking", comparison)
        self.assertEqual(comparison["delta_total_provider_tokens"], -100)

    def test_artifact_symlink_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            checkout = Path(tmp) / "checkout"
            outside = Path(tmp) / "outside"
            outside.mkdir()
            (outside / "run.json").write_text("{}")
            rel = matrix.WORKFLOW_ARTIFACT_ROOT / "session"
            (checkout / rel.parent).mkdir(parents=True)
            (checkout / rel).symlink_to(outside, target_is_directory=True)
            session = {"artifacts": {"root": str(rel)}}
            with self.assertRaisesRegex(ValueError, "escapes lane checkout"):
                matrix.copy_artifacts_for_sessions(checkout, [session])

    def test_full_qualification_freshness_is_shared(self) -> None:
        sequence = runner.load_sequence(SEQUENCE_ID)
        current, qualification = runner.qualification_is_current(sequence)
        self.assertTrue(current)
        self.assertEqual(
            (current, qualification),
            validate_repository.qualification_is_current(sequence),
        )



class CorrectionContractTest(unittest.TestCase):
    def test_production_guidance_preserves_author_surfaces_without_forcing_use(self) -> None:
        guidance = (ROOT / "AGENTS.md").read_text()
        evaluator = (ROOT / "prompts/evaluator.md").read_text()
        parity = (ROOT / "docs/papers/official-integration-parity-audit.md").read_text()
        self.assertIn("every tool-author-recommended normal integration surface", guidance)
        self.assertIn("never adding evaluator-authored steering, quotas, or forced calls", evaluator)
        self.assertIn("Product-authored guidance is part of normal installation", parity)

    def test_solution_directed_task_assistance_is_distinct_from_tool_steering(self) -> None:
        for path in (
            "AGENTS.md",
            "docs/evaluations/design/framework.md",
            "docs/evaluations/design/token-and-quality-policy.md",
            ".agents/skills/benchmark-protocol-writer.md",
        ):
            text = (ROOT / path).read_text()
            self.assertIn("Solution-directed task assistance", text, path)
            self.assertIn("must not require or prefer treatment-tool invocation", text, path)

    def test_deleted_codegraph_generation_is_superseded_by_canonical_v1(self) -> None:
        deletion = json.loads((ROOT / "sources/evaluations/audits/invalid-codegraph-v1-result-deletion-20260719.json").read_text())
        qualification = json.loads((ROOT / "sources/evaluations/audits/corrected-integration-qualification-codegraph-20260719.json").read_text())
        sessions = json.loads((ROOT / "data/workflow-sessions.json").read_text())["sessions"]
        deleted_ids = {sid for row in deletion["profiles"] for sid in row["deleted_session_ids"]}
        deleted_protocols = {path for row in deletion["profiles"] for path in row["deleted_protocol_paths"]}
        current_qualification = {
            (lane["sequence_id"], lane["protocol_path"], lane["protocol_sha256"])
            for lane in qualification["lanes"]
        }
        for session in sessions:
            if session["session_id"] not in deleted_ids:
                continue
            self.assertEqual(session["profile"]["profile_id"], "retrieval-codegraph-codex-mcp-v1")
            self.assertNotIn(session["frozen_protocol"]["path"], deleted_protocols)
            self.assertIn(
                (
                    session["task_sequence"]["sequence_id"],
                    session["frozen_protocol"]["path"],
                    session["frozen_protocol"]["sha256"],
                ),
                current_qualification,
            )
        self.assertEqual(qualification["profiles"], ["retrieval-codegraph-codex-mcp-v1"])
        self.assertTrue(deleted_protocols.isdisjoint({lane["protocol_path"] for lane in qualification["lanes"]}))
        runner.assert_profile_runnable("retrieval-codegraph-codex-mcp-v1")

    def test_incomplete_jcodemunch_result_is_deleted(self) -> None:
        receipt = json.loads((ROOT / "sources/evaluations/audits/invalid-jcodemunch-direct-v1-result-deletion-20260719.json").read_text())
        sessions = json.loads((ROOT / "data/workflow-sessions.json").read_text())["sessions"]
        deleted = {sid for row in receipt["profiles"] for sid in row["deleted_session_ids"]}
        self.assertTrue(deleted.isdisjoint({s["session_id"] for s in sessions}))
        self.assertNotIn("retrieval-jcodemunch-mcp-direct-v1", runner.SUPPORTED_WORKFLOW_TOOL_PROFILES)
        for row in receipt["profiles"]:
            for key in ("deleted_paths", "deleted_protocol_paths", "deleted_comparison_paths", "deleted_bundle_roots"):
                for path in row.get(key, []):
                    self.assertFalse((ROOT / path).exists(), path)

    def test_guide_faithful_jcodemunch_successor_installs_native_codex_guidance(self) -> None:
        profile_id = "retrieval-jcodemunch-codex-mcp-v2"
        self.assertEqual(runner.SUPPORTED_WORKFLOW_TOOL_PROFILES[profile_id], "jcodemunch-codex-mcp-v2")
        cfg = runner.fixture.active_tool_config({}, profile_id)
        assert cfg is not None
        self.assertEqual(cfg["mcp_args"], [])
        self.assertIn("{codex_home}/AGENTS.md", cfg["host_integration"]["required_files"])
        self.assertTrue(cfg["mcp_handshake"]["required"])
        profiles = {p["id"]: p for p in json.loads((ROOT / "data/evaluation-profiles.json").read_text())["profiles"]}
        self.assertEqual(profiles[profile_id]["status"], "screening-shortlist")
        fixtures = json.loads((ROOT / "data/repository-fixtures.json").read_text())["fixtures"]
        self.assertTrue(all(profile_id in fixture["candidate_profiles"] for fixture in fixtures))

    def test_jcodemunch_guidance_installer_copies_product_authored_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / "codex"
            receipt = Path(temp) / "receipt.json"
            proc = subprocess.run([
                sys.executable, str(ROOT / "scripts/install_jcodemunch_codex_guidance.py"),
                "--source-root", "/opt/data/tool-candidates/jcodemunch-mcp",
                "--expected-commit", "fbc14e40c7057ebc6d718fb48083d30522afe15f",
                "--codex-home", str(home), "--receipt", str(receipt),
            ], text=True, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(receipt.read_text())
            self.assertFalse(payload["evaluator_authored_guidance"])
            guidance = (home / "AGENTS.md").read_text()
            self.assertIn("jcodemunch_guide", guidance)
            self.assertIn("Test files when running tests", guidance)

    def test_jcodemunch_successor_has_current_provider_free_qualification(self) -> None:
        receipt = json.loads((ROOT / "sources/evaluations/audits/corrected-integration-qualification-jcodemunch-codex-mcp-v2-20260719.json").read_text())
        self.assertEqual(receipt["profiles"], ["retrieval-jcodemunch-codex-mcp-v2"])
        self.assertEqual(receipt["provider_calls"], 0)
        self.assertEqual(len(receipt["lanes"]), 3)
        for lane in receipt["lanes"]:
            protocol = ROOT / lane["protocol_path"]
            self.assertEqual(lane["protocol_sha256"], hashlib.sha256(protocol.read_bytes()).hexdigest())
            self.assertTrue(lane["host_integration"]["passed"])
            self.assertEqual(lane["tool_warmup_exit_code"], 0)
            self.assertTrue(lane["mcp_handshake"]["passed"])
            self.assertIn("jcodemunch_guide", lane["mcp_handshake"]["tool_names"])

    def test_incomplete_ponytail_and_caveman_results_are_deleted(self) -> None:
        receipt = json.loads((ROOT / "sources/evaluations/audits/invalid-ponytail-caveman-result-deletion-20260719.json").read_text())
        sessions = json.loads((ROOT / "data/workflow-sessions.json").read_text())["sessions"]
        deleted = {sid for row in receipt["profiles"] for sid in row["deleted_session_ids"]}
        self.assertEqual(len(deleted), 6)
        self.assertTrue(deleted.isdisjoint({s["session_id"] for s in sessions}))
        for profile in ("artifact-ponytail", "behavior-caveman"):
            with self.assertRaisesRegex(ValueError, "invalid-profile"):
                runner.assert_profile_runnable(profile)
        for row in receipt["profiles"]:
            for key in ("deleted_paths", "deleted_protocol_paths", "deleted_comparison_paths", "deleted_bundle_roots"):
                for path in row.get(key, []):
                    self.assertFalse((ROOT / path).exists(), path)

    def test_guide_faithful_ponytail_and_caveman_successors_are_native(self) -> None:
        pony = runner.fixture.active_tool_config({}, "artifact-ponytail-codex-plugin-v1")
        cave = runner.fixture.active_tool_config({}, "behavior-caveman-codex-skill-v1")
        self.assertTrue(pony["surface"].startswith("codex-plugin/"))
        self.assertTrue(pony["codex_features"]["hooks"])
        self.assertTrue(any(path.endswith("ponytail-hook-trust.json") for path in pony["host_integration"]["required_files"]))
        self.assertTrue(cave["surface"].startswith("codex-project-skills+"))
        self.assertEqual(cave["session_activation"], "/caveman")
        self.assertEqual(len(cave["host_integration"]["required_files"]), 7)
        self.assertNotIn("prompt_instructions_command", pony)
        self.assertNotIn("prompt_instructions_command", cave)

    def test_repository_local_integration_helpers_use_portable_descriptor_paths(self) -> None:
        pony = runner.fixture.active_tool_config({}, "artifact-ponytail-codex-plugin-v1")
        jcodemunch = runner.fixture.active_tool_config({}, "retrieval-jcodemunch-codex-mcp-v2")
        assert pony is not None
        assert jcodemunch is not None
        expected = {
            "{repository_root}/scripts/prepare_pinned_codex_marketplace.py",
            "{repository_root}/scripts/trust_codex_plugin_hooks.py",
        }
        self.assertTrue(expected.issubset(set(pony["mounts"])))
        self.assertIn(
            "{repository_root}/scripts/install_jcodemunch_codex_guidance.py",
            jcodemunch["mounts"],
        )
        for profile_id in (
            "artifact-ponytail-codex-plugin-v1",
            "retrieval-jcodemunch-codex-mcp-v2",
        ):
            identity = runner.tool_adapter_identity(profile_id)
            local_paths = {
                row["path"]
                for row in identity["source_identity"]
                if row["path"].startswith("{repository_root}/")
            }
            self.assertTrue(local_paths, profile_id)

    def test_corrected_profile_artifact_labels_are_explicit_and_collision_free(self) -> None:
        expected = {
            "artifact-ponytail-codex-plugin-v1": "ponytail",
            "behavior-caveman-codex-skill-v1": "caveman",
            "retrieval-jcodemunch-codex-mcp-v2": "jcodemunch",
        }
        labels = {
            profile_id: runner.artifact_profile_label(profile_id)
            for profile_id in expected
        }
        self.assertEqual(labels, expected)
        self.assertEqual(len(set(labels.values())), len(labels))

    def test_generated_host_integration_identity_is_valid(self) -> None:
        identity = {
            "id": "generated-profile",
            "source_roots": [],
            "binary_identity": {
                "kind": "generated-by-host-integration",
                "command_template": "generated-command",
                "install_commands": [["installer", "--yes"]],
                "install_contract_sha256": "a" * 64,
            },
        }
        errors: list[str] = []
        validate_repository.validate_tool_adapter_identity(identity, copy.deepcopy(identity), "generated-profile", "session-generated", errors)
        self.assertEqual(errors, [])

    def test_controller_refreshes_cumulative_usage_audit_before_validation(self) -> None:
        source = (ROOT / "scripts/run_sequential_workflow_matrix.py").read_text()
        audit = source.index("scripts/audit_codex_cumulative_usage.py")
        validate = source.index("scripts/validate_repository.py", audit)
        self.assertLess(audit, validate)

if __name__ == "__main__":
    unittest.main()
