from __future__ import annotations

import argparse
import concurrent.futures
import copy
import gzip
import hashlib
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from unittest import mock

import jsonschema

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


@contextmanager
def published_unoccupied_probe_worktree():
    """Yield published bytes without mutable paid-attempt receipts, then remove them safely."""
    temp = tempfile.TemporaryDirectory(prefix="workflow-paid-gate-probe-")
    probe = Path(temp.name) / "repo"
    subprocess.run(
        ["git", "worktree", "add", "--quiet", "--detach", str(probe), "HEAD"],
        cwd=ROOT,
        check=True,
    )
    registry_path = probe / "data/workflow-sessions.json"
    registry = json.loads(registry_path.read_text())
    current_sequences = {
        "fastify-lifecycle-sequence-v0",
        "beets-lifecycle-sequence-v0",
        "terraform-lifecycle-sequence-v0",
    }
    removed = [
        session
        for session in registry.get("sessions", [])
        if session.get("task_sequence", {}).get("sequence_id") in current_sequences
        and session.get("profile", {}).get("profile_id") == "baseline-bare-codex"
        and session.get("replicate_index") in {1, 2}
        and str(session.get("session_id", "")).startswith("baseline-")
    ]
    removed_ids = {session["session_id"] for session in removed}
    registry["sessions"] = [
        session for session in registry.get("sessions", [])
        if session.get("session_id") not in removed_ids
    ]
    registry_path.write_text(json.dumps(registry, indent=2) + "\n")
    for session in removed:
        artifact_root = session.get("artifacts", {}).get("root")
        if isinstance(artifact_root, str):
            shutil.rmtree(probe / artifact_root, ignore_errors=True)
    shutil.rmtree(
        probe / "sources/evaluations/audits/current-low-complexity-baseline-r1-r2-attempts",
        ignore_errors=True,
    )
    try:
        yield probe
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(probe)],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        temp.cleanup()


def current_protocol_path(sequence_id: str, profile_id: str = "baseline-bare-codex") -> Path:
    sequence = runner.load_sequence(sequence_id)
    gate = sequence["mistake_gate"]
    matches = []
    for path in (ROOT / "sources/evaluations/protocols").glob("*.json"):
        protocol = json.loads(path.read_text())
        if (
            protocol.get("status") == "frozen-ready-not-run"
            and protocol.get("task_fixture", {}).get("sequence_id") == sequence_id
            and protocol.get("task_fixture", {}).get("qualification_path") == sequence["qualification_path"]
            and protocol.get("baseline", {}).get("profile_id") == profile_id
            and protocol.get("baseline", {}).get("model_condition_id") == gate["designated_model_condition"]
        ):
            matches.append(path)
    if len(matches) != 1:
        raise AssertionError((sequence_id, profile_id, matches))
    return matches[0]


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
        self.assertEqual(summary["cache_write_tokens"], 0)
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

    def test_retained_accounting_correction_covers_its_historical_scope(self) -> None:
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        audit_path = (
            ROOT
            / "sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json"
        )
        audit = json.loads(audit_path.read_text())
        rows = {row["session_id"]: row for row in audit["sessions"]}
        sessions = {session["session_id"]: session for session in registry["sessions"]}
        self.assertTrue(rows.keys() <= sessions.keys())
        for session_id in sessions.keys() - rows.keys():
            usage = sessions[session_id]["cumulative_token_usage"]
            self.assertEqual(usage["measurement_source"], "codex-jsonl-usage-events")
            self.assertIs(type(usage["cache_write_tokens"]), int)
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
        sequences = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
        sequence = next(item for item in sequences if item.get("status") == "active")
        gate = sequence["mistake_gate"]
        exact_prepare = (
            'python3 scripts/run_sequential_workflow_matrix.py "$SEQUENCE_ID" '
            f'--workflow-model-condition-id {gate["designated_model_condition"]} '
            f'--workflow-model {gate["model"]} --workflow-reasoning-effort {gate["reasoning_effort"]} --prepare-only'
        )
        prepare_lines = [
            line
            for line in runbook.splitlines()
            if "scripts/run_sequential_workflow_matrix.py" in line
            and "--prepare-only" in line
            and "$SEQUENCE_ID" in line
        ]
        self.assertEqual(prepare_lines, [exact_prepare])
        self.assertNotIn("--skip-container-preflight", runbook)

    def test_runbook_offers_baselines_only_for_unoccupied_current_pools(self) -> None:
        runbook = (ROOT / "docs/evaluations/operations/runbook.md").read_text()
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        current_ready: set[str] = set()
        historical_default_groups: dict[tuple[str, str], set[int]] = {}
        for sequence_id in runner.active_sequence_ids():
            sequence = runner.load_sequence(sequence_id)
            current_protocol = json.loads(current_protocol_path(sequence_id).read_text())
            current_pool = current_protocol["baseline_pool"]["protocol_fingerprint"]
            gate = sequence["mistake_gate"]
            model_condition_id = gate["designated_model_condition"]
            matching = [
                session
                for session in registry["sessions"]
                if session.get("status") == "completed"
                and session.get("session_role") == "baseline"
                and session.get("task_sequence", {}).get("sequence_id") == sequence_id
                and session.get("agent", {}).get("model_condition_id") == model_condition_id
                and session.get("baseline_pool", {}).get("protocol_fingerprint") == current_pool
                and session.get("interpretation", {}).get("accepted_for_objective") is True
            ]
            flags = (
                f"--workflow-model-condition-id {model_condition_id} "
                f"--workflow-model {gate['model']} --workflow-reasoning-effort {gate['reasoning_effort']}"
            )
            baseline_command = f"python3 scripts/run_sequential_workflow_matrix.py {sequence_id} {flags}\n"
            pilot_allowed, _pilot_reason = runner.baseline_v2_pilot_run_gate(sequence, ROOT)
            if matching:
                current_ready.add(sequence_id)
                self.assertNotIn(baseline_command, runbook)
            elif pilot_allowed:
                self.assertIn(baseline_command, runbook)
            else:
                self.assertNotIn(baseline_command, runbook)

        for session in registry["sessions"]:
            if (
                session.get("status") == "completed"
                and session.get("session_role") == "baseline"
                and session.get("agent", {}).get("model_condition_id") == runner.DEFAULT_WORKFLOW_MODEL_CONDITION_ID
                and session.get("interpretation", {}).get("accepted_for_objective") is True
            ):
                key = (
                    session["task_sequence"]["sequence_id"],
                    session["baseline_pool"]["protocol_fingerprint"],
                )
                if key[0] not in current_ready:
                    historical_default_groups.setdefault(key, set()).add(session["replicate_index"])
        for (sequence_id, pool), replicates in historical_default_groups.items():
            self.assertIn(
                f"`{sequence_id}` pool `{pool}` "
                f"({', '.join(f'r{index}' for index in sorted(replicates))})",
                runbook,
            )

        treatment_ready = {
            sequence_id
            for sequence_id in current_ready
            if runner.baseline_v2_treatment_gate(runner.load_sequence(sequence_id), ROOT)[0]
        }
        if treatment_ready:
            self.assertIn('scripts/refresh_workflow_contracts.py --sequence-id "$SEQUENCE_ID"', runbook)
            self.assertIn('--treatment-profile "$PROFILE_ID"', runbook)
            self.assertIn('--workflow-model-condition-id codex-openai-gpt-5-6-sol-high', runbook)
            self.assertIn('--dry-run', runbook)
            self.assertIn('no paid treatment command is published', runbook)
        else:
            self.assertNotIn('--treatment-profile "$PROFILE_ID"', runbook)
        self.assertIn(
            "Non-default model-comparison baselines are tracked separately",
            runbook,
        )

    def test_model_comparison_baseline_pools_are_rendered_separately(self) -> None:
        runbook = (ROOT / "docs/evaluations/operations/runbook.md").read_text()
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        grouped: dict[tuple[str, str], set[int]] = {}
        for session in registry["sessions"]:
            if (
                session.get("status") == "completed"
                and session.get("session_role") == "baseline"
                and session.get("agent", {}).get("model_condition_id") == "codex-openai-gpt-5-6-sol-high"
                and session.get("interpretation", {}).get("accepted_for_objective") is True
            ):
                key = (
                    session["task_sequence"]["sequence_id"],
                    session["baseline_pool"]["protocol_fingerprint"],
                )
                grouped.setdefault(key, set()).add(session["replicate_index"])
        sequences = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        current_pools = set()
        for sequence in sequences["sequences"]:
            if sequence.get("task_family_generation") not in {"baseline-v2", "baseline-v3", "baseline-v4"}:
                continue
            protocol, _document = runner.current_baseline_v2_protocol(
                sequence,
                sequence.get("mistake_gate", {}),
                ROOT,
            )
            current_pools.add((sequence["id"], protocol["baseline_pool_fingerprint"]))
        self.assertGreaterEqual(len(grouped), 6)
        for (sequence_id, pool), replicates in grouped.items():
            rendered = (
                f"`{sequence_id}` under `codex-openai-gpt-5-6-sol-high` pool `{pool}` "
                f"({', '.join(f'r{index}' for index in sorted(replicates))})"
            )
            if (sequence_id, pool) in current_pools:
                self.assertNotIn(rendered, runbook)
            else:
                self.assertIn(rendered, runbook)

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

    def test_schema_rejects_unpaired_accepted_treatment(self) -> None:
        schema = json.loads((ROOT / "schemas/workflow-session-record.schema.json").read_text())
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        treatment = copy.deepcopy(
            next(
                session
                for session in registry["sessions"]
                if session.get("schema_version") == 2
                and session.get("session_role") != "baseline"
                and session.get("interpretation", {}).get("accepted_for_objective") is True
                and session.get("interpretation", {}).get("comparison_baseline_session_id")
            )
        )
        jsonschema.Draft202012Validator(schema).validate(treatment)
        treatment["interpretation"]["comparison_baseline_session_id"] = ""
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schema).validate(treatment)

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
        prompt = (ROOT / feature["prompt_path"]).read_text()
        verifier = (ROOT / feature["verifier_command"]).read_text()
        self.assertEqual(feature["model_concealed_paths"], [])
        self.assertIn("escaped_sep", prompt)
        self.assertIn("escaped_sep", verifier)
        self.assertIn("test/util/test_functemplate.py", verifier)
        self.assertNotIn("read_text", verifier)

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
        workflow_source = inspect.getsource(runner._run_one_locked)
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
        sequence = runner.load_sequence("fastify-lifecycle-sequence-v0")
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
        provenance_only["qualification_generator_sha256"] = "2" * 64
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
            path = current_protocol_path(sequence_id)
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

    def test_terraform_v2_uses_visible_focused_tests_without_concealed_collisions(self) -> None:
        sequence = runner.load_sequence("terraform-lifecycle-sequence-v0")
        qualification_record = json.loads((ROOT / sequence["qualification_path"]).read_text())
        self.assertEqual(qualification_record["fixed_snapshot_concealed_path_collision_audit"], [])
        self.assertTrue(qualification_record["fixed_snapshot_model_concealed_paths_absent"])
        for task in sequence["tasks"]:
            self.assertEqual(task["model_concealed_paths"], [])
            verifier = (ROOT / task["verifier_command"]).read_text()
            for anchor in task["model_visible_validation_anchors"]:
                self.assertIn(anchor, verifier)

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

    def test_v4_task_verifiers_resolve_project_repo_without_caller_environment(self) -> None:
        document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        v4_tasks = [
            task
            for sequence in document["sequences"]
            if sequence.get("task_family_generation") == "baseline-v4"
            for task in sequence["tasks"]
        ]
        self.assertEqual(len(v4_tasks), 6)
        for task in v4_tasks:
            verifier = (ROOT / task["verifier_command"]).read_text()
            self.assertIn('PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"', verifier)
            self.assertIn('cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"', verifier)
            self.assertNotIn("WORKFLOW_REPO is required", verifier)

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
                output.write_text("\n".join([
                    json.dumps({"type": "thread.started", "thread_id": "thread-1"}),
                    json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}}),
                ]) + "\n")
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
                code, thread, continuity_error = runner.run_codex_task(
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
            self.assertIsNone(continuity_error)
            self.assertEqual(timeouts, [60, 10])
            self.assertIn("turn.failed", events.read_text())
            self.assertIn("turn.completed", events.read_text())
            combined_events = [json.loads(line) for line in events.read_text().splitlines()]
            usage_blocks = runner.extract_codex_usage.usage_blocks(combined_events)
            self.assertEqual([block["usage"]["input_tokens"] for block in usage_blocks], [2, 1])
            self.assertTrue((root / "task-01-operational-retry-01.md").is_file())

    def test_current_replication_turn_budget_disables_operational_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt = root / "task-01.md"
            prompt.write_text("Repair the task.\n")
            events = root / "task-01-codex-events.jsonl"
            calls = 0

            def fake_backend(*args: object, **kwargs: object) -> mock.Mock:
                nonlocal calls
                calls += 1
                Path(str(kwargs["stdout_path"])).write_text("\n".join([
                    json.dumps({"type": "thread.started", "thread_id": "thread-1"}),
                    json.dumps({"type": "turn.failed", "error": {"message": "failed to parse function arguments: EOF while parsing an object"}}),
                ]) + "\n")
                return mock.Mock(returncode=1)

            with (
                mock.patch.object(runner.fixture, "active_tool_config", return_value=None),
                mock.patch.object(runner.fixture, "codex_env", return_value={}),
                mock.patch.object(runner.fixture, "tool_env_for_record", return_value={}),
                mock.patch.object(runner.fixture, "codex_model_args", return_value=[]),
                mock.patch.object(runner, "model_mounts_for_record", return_value=[]),
                mock.patch.object(runner.fixture, "run_backend", side_effect=fake_backend),
                mock.patch.object(runner.time, "monotonic", side_effect=[0, 1]),
            ):
                code, thread, continuity_error = runner.run_codex_task(
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
                    operational_retries=0,
                )
            self.assertEqual((code, thread, calls), (1, "thread-1", 1))
            self.assertIsNone(continuity_error)
            self.assertFalse((root / "task-01-operational-retry-01.md").exists())

    def test_codex_resume_rejects_mismatched_thread_started_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prompt = root / "task-02.md"
            prompt.write_text("Continue the task.\n")
            events = root / "task-02-codex-events.jsonl"

            def fake_backend(*args: object, **kwargs: object) -> mock.Mock:
                Path(str(kwargs["stdout_path"])).write_text("\n".join([
                    json.dumps({"type": "thread.started", "thread_id": "thread-B"}),
                    json.dumps({"type": "turn.completed", "usage": {"input_tokens": 1}}),
                ]) + "\n")
                return mock.Mock(returncode=0)

            with (
                mock.patch.object(runner.fixture, "active_tool_config", return_value=None),
                mock.patch.object(runner.fixture, "codex_env", return_value={}),
                mock.patch.object(runner.fixture, "tool_env_for_record", return_value={}),
                mock.patch.object(runner.fixture, "codex_model_args", return_value=[]),
                mock.patch.object(runner, "model_mounts_for_record", return_value=[]),
                mock.patch.object(runner.fixture, "run_backend", side_effect=fake_backend),
                mock.patch.object(runner.time, "monotonic", side_effect=[0, 1]),
            ):
                code, thread, continuity_error = runner.run_codex_task(
                    {"target": {"repository_path": "."}},
                    "baseline-bare-codex",
                    root / "codex-home",
                    root,
                    "image",
                    prompt,
                    events,
                    root / "last-message.txt",
                    timeout=60,
                    thread_id="thread-A",
                )
            self.assertEqual(code, runner.THREAD_CONTINUITY_FAILURE_EXIT_CODE)
            self.assertEqual(thread, "thread-A")
            self.assertIsInstance(continuity_error, dict)
            assert isinstance(continuity_error, dict)
            self.assertEqual(continuity_error["expected_thread_id"], "thread-A")
            self.assertEqual(continuity_error["observed_thread_ids"], ["thread-B"])

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
            "beets-lifecycle-feature-v0": ["extra_special_chars", "escaped_sep", "functemplate.py"],
            "fastify-lifecycle-feature-v0": ["request.mediaType", "kRequestContentType", "application/json"],
            "terraform-lifecycle-feature-v0": ["Deferred: isDeferred", "baseline_v3_deferred_test.go", "socket"],
            "terraform-lifecycle-refactor-v0": ["StateStoreProviderRequirement", "providerreqs.Requirements", "NamedType"],
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
            "fastify-lifecycle-feature-v0": ["lib/request.js", "request.mediaType", "ContentType.from"],
            "fastify-lifecycle-refactor-v0": ["lib/content-type.js", "LruMap", "ContentType.cache"],
            "fastify-lifecycle-review-v0": ["fastify.js", "FST_ERR_MAX_PARAM_LENGTH", "414"],
            "beets-lifecycle-feature-v0": ["beets/util/functemplate.py", "extra_special_chars", "test/util/test_functemplate.py"],
            "beets-lifecycle-refactor-v0": ["beets/dbcore/db.py", "return iter(self._all_keys)", "type(iter(value)).__name__"],
            "beets-lifecycle-review-v0": ["beetsplug/ftintitle.py", "feat_tokens", "test/plugins/test_ftintitle.py"],
            "terraform-lifecycle-feature-v0": ["internal/policy/callback/server.go", "Deferred: isDeferred", "baseline_v3_deferred_test.go"],
            "terraform-lifecycle-refactor-v0": ["internal/configs/state_migrate_file.go", "providerreqs.Requirements", "baseline_v3_requirement_type_test.go"],
            "terraform-lifecycle-review-v0": ["internal/addrs/checkable.go", 'getCheckableName("var"', "baseline_v3_checkable_test.go"],
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
        protocol_path = current_protocol_path("beets-lifecycle-sequence-v0")
        protocol = json.loads(protocol_path.read_text())
        descriptor = protocol["baseline_pool"]["descriptor"]
        expected = runner.baseline_protocol_fingerprint_from_descriptor(descriptor)
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

    def test_canonical_baseline_lookup_rejects_mislabeled_profile_and_selected_role(self) -> None:
        sequence = {
            "id": "unit-sequence",
            "task_family_generation": "baseline-v2",
            "mistake_gate": {},
        }
        identity = {"protocol_id": "canonical", "path": "protocols/canonical.json", "sha256": "a" * 64}
        selected = {
            "descriptor_sha256": "b" * 64,
            "descriptor": {
                "execution_role": "baseline",
                "selected_profile": {"profile_id": "baseline-bare-codex"},
            },
        }
        session = {
            "schema_version": 2,
            "session_id": "mislabeled",
            "session_role": "baseline",
            "status": "completed",
            "replicate_index": 0,
            "task_sequence": {"sequence_id": "unit-sequence"},
            "profile": {"profile_id": "unexpected-treatment-profile"},
            "baseline_pool": {"protocol_fingerprint": "unit-pool"},
            "frozen_protocol": identity,
            "selected_execution": selected,
            "interpretation": {"accepted_for_execution": True},
        }
        with mock.patch.object(runner, "baseline_protocol_fingerprint", return_value="unit-pool"), \
            mock.patch.object(
                runner,
                "current_baseline_v2_protocol",
                return_value=(identity, {"selected_execution": selected}),
            ):
            self.assertIsNone(
                runner.find_canonical_baseline_record({"sessions": [session]}, sequence, 0)
            )
        session["profile"]["profile_id"] = "baseline-bare-codex"
        session["selected_execution"]["descriptor"]["execution_role"] = "treatment"
        with mock.patch.object(runner, "baseline_protocol_fingerprint", return_value="unit-pool"), \
            mock.patch.object(
                runner,
                "current_baseline_v2_protocol",
                return_value=(identity, {"selected_execution": selected}),
            ):
            self.assertIsNone(
                runner.find_canonical_baseline_record({"sessions": [session]}, sequence, 0)
            )

    def test_session_builder_rejects_unpaired_accepted_treatment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            with self.assertRaisesRegex(ValueError, "requires a comparison baseline binding"):
                runner.workflow_session_record(
                    {},
                    {"accepted": True},
                    run_dir,
                    "terminal-tokenjuice-codex-hook-v1",
                    [],
                    0,
                    0,
                    {},
                    [],
                    prompt_delivery={},
                    leakage_controls={},
                )
            with self.assertRaisesRegex(ValueError, "must not carry"):
                runner.workflow_session_record(
                    {},
                    {"accepted": True},
                    run_dir,
                    "baseline-bare-codex",
                    [],
                    0,
                    0,
                    {},
                    [],
                    prompt_delivery={},
                    leakage_controls={},
                    comparison_baseline_session_id="not-allowed",
                )

    def test_direct_treatment_requires_reusable_same_replicate_baseline_before_setup(self) -> None:
        sequence = {"id": "unit-sequence"}
        with mock.patch.object(runner, "find_canonical_baseline_record", return_value=None):
            with self.assertRaisesRegex(ValueError, "requires a reusable canonical baseline"):
                runner.require_reusable_treatment_baseline({"sessions": []}, sequence, 0)
        malformed = {"session_id": "malformed-baseline"}
        with mock.patch.object(runner, "find_canonical_baseline_record", return_value=malformed), \
            mock.patch.object(runner, "reviewed_session_reuse_state", return_value="occupied"):
            with self.assertRaisesRegex(ValueError, "requires a reusable canonical baseline"):
                runner.require_reusable_treatment_baseline({"sessions": [malformed]}, sequence, 0)
        reusable = {"session_id": "reusable-baseline"}
        with mock.patch.object(runner, "find_canonical_baseline_record", return_value=reusable), \
            mock.patch.object(runner, "reviewed_session_reuse_state", return_value="reusable"):
            self.assertIs(
                runner.require_reusable_treatment_baseline({"sessions": [reusable]}, sequence, 0),
                reusable,
            )
        source = inspect.getsource(runner._run_one_locked)
        self.assertLess(
            source.index("require_reusable_treatment_baseline("),
            source.index("run_dir.mkdir("),
        )

    def test_registry_publication_atomically_rejects_duplicate_provider_slot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            registry_path = root / "data/workflow-sessions.json"
            registry_path.write_text('{"sessions": []}\n')
            record = {
                "schema_version": 2,
                "session_id": "first",
                "replicate_index": 0,
                "task_sequence": {"sequence_id": "unit-sequence"},
                "profile": {"profile_id": "baseline-bare-codex"},
                "baseline_pool": {"protocol_fingerprint": "unit-pool"},
                "frozen_protocol": {
                    "protocol_id": "unit-protocol",
                    "path": "protocols/unit-protocol.json",
                    "sha256": "a" * 64,
                },
            }
            with mock.patch.object(runner, "ROOT", root):
                runner.update_registry(record)
                duplicate = copy.deepcopy(record)
                duplicate["session_id"] = "different-session-id"
                duplicate["frozen_protocol"]["sha256"] = "b" * 64
                with self.assertRaisesRegex(FileExistsError, "slot already occupied"):
                    runner.update_registry(duplicate)
            self.assertEqual(
                [item["session_id"] for item in json.loads(registry_path.read_text())["sessions"]],
                ["first"],
            )

    def test_direct_provider_runs_share_nonblocking_production_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, \
            mock.patch.object(runner, "PRODUCTION_LOCK_PATH", Path(tmp) / ".production.lock"), \
            mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(runner.PRODUCTION_LOCK_FD_ENV, None)
            held_fd = runner.acquire_provider_production_lock()
            try:
                args = argparse.Namespace(
                    prepare_only=False,
                    sequence_id="fastify-lifecycle-sequence-v0",
                    profile_id="behavior-caveman",
                    replicate_index=0,
                )
                with mock.patch.object(runner, "_run_one_locked") as inner:
                    with self.assertRaisesRegex(RuntimeError, "already active"):
                        runner.run_one(args)
                inner.assert_not_called()
            finally:
                os.close(held_fd)

    def test_concurrent_process_cannot_acquire_direct_provider_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = str(Path(tmp) / ".production.lock")
            holder_code = """
import os,sys
from pathlib import Path
from scripts import run_codex_workflow_evaluation as runner
runner.PRODUCTION_LOCK_PATH = Path(sys.argv[1])
fd = runner.acquire_provider_production_lock()
print('locked', flush=True)
sys.stdin.readline()
os.close(fd)
"""
            contender_code = """
import sys
from pathlib import Path
from scripts import run_codex_workflow_evaluation as runner
runner.PRODUCTION_LOCK_PATH = Path(sys.argv[1])
try:
    runner.acquire_provider_production_lock()
except RuntimeError as exc:
    print(str(exc))
    raise SystemExit(0)
raise SystemExit(1)
"""
            holder = subprocess.Popen(
                [sys.executable, "-c", holder_code, lock_path],
                cwd=ROOT,
                text=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                self.assertIsNotNone(holder.stdout)
                assert holder.stdout is not None
                self.assertEqual(holder.stdout.readline().strip(), "locked")
                contender = subprocess.run(
                    [sys.executable, "-c", contender_code, lock_path],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    timeout=30,
                )
                self.assertEqual(contender.returncode, 0, contender.stderr)
                self.assertIn("already active", contender.stdout)
            finally:
                if holder.stdin is not None:
                    holder.stdin.write("release\n")
                    holder.stdin.flush()
                holder.communicate(timeout=30)

    def test_matrix_child_can_verify_inherited_production_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, \
            mock.patch.object(runner, "PRODUCTION_LOCK_PATH", Path(tmp) / ".production.lock"), \
            mock.patch.dict(os.environ, {}, clear=False):
            fd = runner.acquire_provider_production_lock()
            try:
                os.environ[runner.PRODUCTION_LOCK_FD_ENV] = str(fd)
                self.assertEqual(runner.acquire_provider_production_lock(), fd)
            finally:
                os.environ.pop(runner.PRODUCTION_LOCK_FD_ENV, None)
                os.close(fd)

    def test_unlocked_correct_inode_cannot_forge_matrix_parent_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(runner, "PRODUCTION_LOCK_PATH", Path(tmp) / ".production.lock"), \
             mock.patch.dict(os.environ, {}, clear=False):
            runner.PRODUCTION_LOCK_PATH.touch(mode=0o600)
            fd = os.open(runner.PRODUCTION_LOCK_PATH, os.O_RDWR)
            try:
                os.environ[runner.PRODUCTION_LOCK_FD_ENV] = str(fd)
                with self.assertRaisesRegex(RuntimeError, "was not held before child launch"):
                    runner.inherited_provider_production_lock_fd()
            finally:
                os.environ.pop(runner.PRODUCTION_LOCK_FD_ENV, None)
                os.close(fd)

    def production_v3_fixture(self, root: Path) -> tuple[dict, Path]:
        session_id = f"unit-production-session-{root.name}"
        run_dir = ROOT / "sources/evaluations/workflow-sessions" / session_id
        if run_dir.exists():
            shutil.rmtree(run_dir)
        run_dir.mkdir(parents=True)
        self.addCleanup(
            lambda path=run_dir: path.unlink(missing_ok=True)
            if path.is_symlink()
            else shutil.rmtree(path, ignore_errors=True)
        )
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
            "session_id": session_id,
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
                "root": f"sources/evaluations/workflow-sessions/{session_id}",
                "run_record": str((run_dir / "run.json").relative_to(ROOT)),
                "final_diff": str((run_dir / "changes.diff").relative_to(ROOT)),
                "evidence_bundle": str((run_dir / "evidence.jsonl.gz").relative_to(ROOT)),
                "manifest": str((run_dir / "manifest.sha256").relative_to(ROOT)),
            },
            "interpretation": {"accepted_for_execution": False, "accepted_for_objective": False, "claim_status": "failed", "exclusion_reason": "unit"},
        }
        run_payload = {
            **{
                key: session[key]
                for key in (
                    "frozen_protocol",
                    "baseline_pool",
                    "selected_execution",
                    "docker_image_identity",
                    "tool_adapter_identity",
                )
            },
            "session_id": session_id,
            "replicate_index": session["replicate_index"],
            "workflow_sequence_id": session["task_sequence"]["sequence_id"],
            "profile_id": session["profile"]["profile_id"],
            "accepted": session["interpretation"]["accepted_for_execution"],
            "token_usage": {
                key: session["cumulative_token_usage"].get(key)
                for key in validate_repository.PROVIDER_USAGE_FIELDS
            },
            "per_task_results": copy.deepcopy(session["per_task_results"]),
            "verifier_integrity_passed": None,
        }
        (run_dir / "run.json").write_text(json.dumps(run_payload, indent=2) + "\n")
        (run_dir / "changes.diff").write_text("")
        with gzip.open(run_dir / "evidence.jsonl.gz", "wt", encoding="utf-8") as evidence:
            evidence.write(json.dumps({"path": "unit-evidence.json", "content": "{}\n"}) + "\n")
        runner.write_manifest(run_dir)
        return session, protocol_path

    def production_v3_errors(
        self,
        session: dict,
        *,
        legacy_comparison_baseline: bool = False,
        symlink_comparison_baseline: bool = False,
    ) -> list[str]:
        errors: list[str] = []
        sessions = [session]
        comparison_id = session.get("interpretation", {}).get("comparison_baseline_session_id")
        if comparison_id:
            baseline = copy.deepcopy(session)
            baseline.update(
                schema_version=2,
                session_id=comparison_id,
                session_role="baseline",
                status="completed",
            )
            baseline["profile"] = {
                "profile_id": "baseline-bare-codex",
                "profile_type": "control",
                "enabled_surfaces": ["codex-native-shell-edit"],
                "disabled_overlaps": [],
                "component_ids": [],
            }
            baseline_descriptor = baseline["selected_execution"]["descriptor"]
            baseline_descriptor["execution_role"] = "baseline"
            baseline_descriptor["selected_profile"] = {"profile_id": "baseline-bare-codex"}
            baseline_descriptor["tool_adapter"] = None
            baseline["selected_execution"]["descriptor_sha256"] = validate_repository.canonical_json_hash(
                baseline_descriptor
            )
            baseline["tool_adapter_identity"] = None
            baseline["interpretation"].update(
                accepted_for_execution=True,
                accepted_for_objective=True,
                comparison_baseline_session_id="",
            )

            source_run_dir = ROOT / session["artifacts"]["run_record"]
            source_run_dir = source_run_dir.parent
            baseline_run_dir = source_run_dir.parent / comparison_id
            if baseline_run_dir.is_symlink():
                baseline_run_dir.unlink()
            elif baseline_run_dir.exists():
                shutil.rmtree(baseline_run_dir)
            shutil.copytree(source_run_dir, baseline_run_dir)
            self.addCleanup(
                lambda path=baseline_run_dir: path.unlink(missing_ok=True)
                if path.is_symlink()
                else shutil.rmtree(path, ignore_errors=True)
            )
            baseline["artifacts"] = {
                "artifact_contract": "compact-v1-four-files",
                "root": f"sources/evaluations/workflow-sessions/{comparison_id}",
                "run_record": str((baseline_run_dir / "run.json").relative_to(ROOT)),
                "final_diff": str((baseline_run_dir / "changes.diff").relative_to(ROOT)),
                "evidence_bundle": str((baseline_run_dir / "evidence.jsonl.gz").relative_to(ROOT)),
                "manifest": str((baseline_run_dir / "manifest.sha256").relative_to(ROOT)),
            }

            treatment_protocol_path = ROOT / session["frozen_protocol"]["path"]
            baseline_protocol = json.loads(treatment_protocol_path.read_text())
            baseline_protocol_id = "unit-baseline-production-v3"
            baseline_protocol["protocol_id"] = baseline_protocol_id
            baseline_protocol["selected_execution"] = copy.deepcopy(baseline["selected_execution"])
            baseline_protocol_path = treatment_protocol_path.with_name(f"{baseline_protocol_id}.json")
            baseline_protocol_path.write_text(json.dumps(baseline_protocol, indent=2) + "\n")
            baseline["frozen_protocol"] = {
                "protocol_id": baseline_protocol_id,
                "path": str(baseline_protocol_path.relative_to(ROOT)),
                "sha256": hashlib.sha256(baseline_protocol_path.read_bytes()).hexdigest(),
            }

            baseline_run = json.loads((baseline_run_dir / "run.json").read_text())
            baseline_run.update(
                session_id=comparison_id,
                profile_id="baseline-bare-codex",
                frozen_protocol=copy.deepcopy(baseline["frozen_protocol"]),
                baseline_pool=copy.deepcopy(baseline["baseline_pool"]),
                selected_execution=copy.deepcopy(baseline["selected_execution"]),
                docker_image_identity=copy.deepcopy(baseline["docker_image_identity"]),
                tool_adapter_identity=None,
                token_usage=copy.deepcopy(baseline["cumulative_token_usage"]),
                accepted=True,
                per_task_results=copy.deepcopy(baseline["per_task_results"]),
                verifier_integrity_passed=True,
            )
            (baseline_run_dir / "run.json").write_text(json.dumps(baseline_run, indent=2) + "\n")
            runner.write_manifest(baseline_run_dir)
            if symlink_comparison_baseline:
                external_baseline_dir = treatment_protocol_path.parent / f"{comparison_id}-external"
                if external_baseline_dir.exists():
                    shutil.rmtree(external_baseline_dir)
                baseline_run_dir.rename(external_baseline_dir)
                baseline_run_dir.symlink_to(external_baseline_dir, target_is_directory=True)
            if legacy_comparison_baseline:
                baseline["schema_version"] = 1
                baseline["artifacts"] = {}
            sessions.insert(0, baseline)
        validate_repository.validate_workflow_sessions(
            {"schema_version": 1, "primary_metric": "cumulative provider-reported workflow tokens", "sessions": sessions},
            {"unit-sequence"},
            {"fixtures": [{"id": "unit-fixture"}]},
            {
                "unit-profile": {
                    "profile_type": "individual_tool",
                    "session_role": "individual_tool_treatment",
                    "enabled_surfaces": ["terminal/tool-output-compaction"],
                    "disabled_overlaps": [],
                    "components": [{"component_id": "unit-tool"}],
                },
                "baseline-bare-codex": {
                    "profile_type": "control",
                    "session_role": "baseline",
                    "enabled_surfaces": ["codex-native-shell-edit"],
                    "disabled_overlaps": [],
                    "components": [],
                },
            },
            {"unit-runtime"},
            {"unit-model"},
            errors,
        )
        return errors

    def test_repository_validator_rejects_malformed_workflow_session_schema_versions(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            for malformed in (True, 1.0, 2.0, "2", None):
                candidate = copy.deepcopy(session)
                candidate["schema_version"] = malformed
                errors = self.production_v3_errors(candidate)
                self.assertTrue(any("schema_version must be 1 or 2" in error for error in errors), (malformed, errors))
                self.assertFalse(validate_repository.requires_structured_task_contract(candidate))
        for malformed in (False, True, 0.0, "0", None):
            errors: list[str] = []
            validate_repository.validate_workflow_sessions(
                {
                    "schema_version": malformed,
                    "primary_metric": "cumulative provider-reported workflow tokens",
                    "sessions": [],
                },
                set(),
                {"fixtures": []},
                {},
                set(),
                set(),
                errors,
            )
            self.assertTrue(any("workflow-sessions.json must use schema_version 1" in error for error in errors), (malformed, errors))

    def test_repository_validator_rejects_noncanonical_compact_evidence(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            evidence_path = ROOT / session["artifacts"]["evidence_bundle"]
            bundle_root = evidence_path.parent
            invalid_payloads = (
                b"plain bytes",
                gzip.compress(b""),
                gzip.compress(b"not-json\n"),
                gzip.compress(b'{"path":"first","path":"second","content":"x"}\n'),
                gzip.compress(b'{"path":"first","content":"x","content":"y"}\n'),
                gzip.compress(
                    (json.dumps({"path": "a/b", "content": "one"}) + "\n"
                     + json.dumps({"path": "a/./b", "content": "two"}) + "\n").encode()
                ),
                gzip.compress((json.dumps({"path": "../escape", "content": "bad"}) + "\n").encode()),
            )
            for payload in invalid_payloads:
                evidence_path.write_bytes(payload)
                runner.write_manifest(bundle_root)
                errors = self.production_v3_errors(session)
                self.assertTrue(any("canonical gzip JSONL bundle" in error for error in errors), errors)

    def test_evidence_parser_bounds_single_records_and_canonicalizes_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.jsonl.gz"
            with gzip.open(path, "wt", encoding="utf-8") as handle:
                handle.write(json.dumps({"path": "a/b", "content": "ok"}) + "\n")
            self.assertTrue(validate_repository.evidence_bundle_valid(path))
            with gzip.open(path, "wb") as handle:
                handle.write(b"x" * (8 * 1024 * 1024 + 1))
            self.assertFalse(validate_repository.evidence_bundle_valid(path))

    def test_baseline_v3_qualification_audit_protocol_references_are_live(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            relative_paths = [
                "data/workflow-task-sequences.json",
                "sources/evaluations/audits/baseline-v3-task-family-qualification-20260722.json",
            ]
            audit = json.loads((ROOT / relative_paths[1]).read_text())
            relative_paths.extend(item["qualification_path"] for item in audit["sequences"])
            relative_paths.extend(item["path"] for item in audit["protocols"])
            receipt_index_rel = "sources/evaluations/audits/baseline-v3-literal-command-receipts-20260722/index.json"
            receipt_index = json.loads((ROOT / receipt_index_rel).read_text())
            relative_paths.append(receipt_index_rel)
            for item in receipt_index["receipts"]:
                relative_paths.append(item["path"])
                receipt = json.loads((ROOT / item["path"]).read_text())
                relative_paths.extend(
                    [
                        receipt["literal_command"]["prompt_path"],
                        receipt["literal_command"]["log_path"],
                        receipt["controller_verifier"]["path"],
                        receipt["controller_verifier"]["log_path"],
                        receipt["production_bootstrap"]["log_path"],
                    ]
                )
            for relative in sorted(set(relative_paths)):
                destination = temp_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, destination)
            with mock.patch.object(validate_repository, "ROOT", temp_root):
                errors: list[str] = []
                validate_repository.validate_baseline_v3_qualification_audit(errors)
                self.assertEqual(errors, [])
                audit_path = temp_root / relative_paths[1]
                tampered = json.loads(audit_path.read_text())
                tampered["sequences"][0]["frozen_baseline_protocols"][0]["path"] = (
                    "sources/evaluations/protocols/missing-current-protocol.json"
                )
                audit_path.write_text(json.dumps(tampered))
                errors = []
                validate_repository.validate_baseline_v3_qualification_audit(errors)
                self.assertTrue(
                    any("frozen baseline protocol reference is stale" in error for error in errors),
                    errors,
                )
                for key, value, expected_message in (
                    (
                        "path",
                        "sources/evaluations/protocols/missing-current-protocol.json",
                        "current protocol is unreadable",
                    ),
                    ("sha256", "0" * 64, "current protocol reference is stale"),
                ):
                    tampered = copy.deepcopy(audit)
                    tampered["protocols"][0][key] = value
                    audit_path.write_text(json.dumps(tampered))
                    errors = []
                    validate_repository.validate_baseline_v3_qualification_audit(errors)
                    self.assertTrue(any(expected_message in error for error in errors), errors)
                for duplicate_target in ("sequences", "protocols"):
                    tampered = copy.deepcopy(audit)
                    tampered[duplicate_target].append(copy.deepcopy(tampered[duplicate_target][0]))
                    audit_path.write_text(json.dumps(tampered))
                    errors = []
                    validate_repository.validate_baseline_v3_qualification_audit(errors)
                    self.assertTrue(any("must not contain missing or duplicate" in error for error in errors), errors)
                tampered = copy.deepcopy(audit)
                rehearsal_sequences = tampered["literal_prompt_command_rehearsal"]["sequences"]
                rehearsal_sequences.append(copy.deepcopy(rehearsal_sequences[0]))
                audit_path.write_text(json.dumps(tampered))
                errors = []
                validate_repository.validate_baseline_v3_qualification_audit(errors)
                self.assertTrue(any("must not contain missing or duplicate" in error for error in errors), errors)

    def test_repository_validator_reports_missing_compact_root_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            session_id = "unit-missing-compact-root"
            session["session_id"] = session_id
            missing_root = f"sources/evaluations/workflow-sessions/{session_id}"
            session["artifacts"] = {
                "artifact_contract": "compact-v1-four-files",
                "root": missing_root,
                "run_record": f"{missing_root}/run.json",
                "final_diff": f"{missing_root}/changes.diff",
                "evidence_bundle": f"{missing_root}/evidence.jsonl.gz",
                "manifest": f"{missing_root}/manifest.sha256",
            }
            errors = self.production_v3_errors(session)
            self.assertTrue(any("compact artifact root does not exist as a directory" in error for error in errors), errors)
            self.assertTrue(any("compact artifact run_record does not exist" in error for error in errors), errors)

    def test_provider_usage_parser_rejects_boolean_and_float_components(self) -> None:
        usage = {
            "measurement_source": "codex-jsonl-usage-events",
            "fresh_input_tokens": 5,
            "cached_input_tokens": 4,
            "cache_write_tokens": 0,
            "output_tokens": 1,
            "reasoning_tokens": 1,
            "total_provider_tokens": 10,
        }
        self.assertTrue(validate_repository.provider_usage_valid(usage))
        legacy_null = copy.deepcopy(usage)
        legacy_null["cache_write_tokens"] = None
        self.assertFalse(validate_repository.provider_usage_valid(legacy_null))
        self.assertTrue(
            validate_repository.provider_usage_valid(
                legacy_null,
                allow_legacy_null_cache_write=True,
            )
        )
        for key in validate_repository.PROVIDER_USAGE_FIELDS:
            for invalid in (True, 1.5):
                candidate = copy.deepcopy(usage)
                candidate[key] = invalid
                self.assertFalse(validate_repository.provider_usage_valid(candidate), (key, invalid))

    def test_validator_rejects_generic_nonbaseline_execution_role(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            session["schema_version"] = 2
            session["selected_execution"]["descriptor"]["execution_role"] = "treatment"
            errors = self.production_v3_errors(session)
            self.assertTrue(any("selected execution does not match top-level role/profile" in error for error in errors), errors)

    def test_validator_rejects_boolean_replicate_and_token_counts(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            session, _ = self.production_v3_fixture(Path(tmp))
            session["replicate_index"] = True
            session["interpretation"]["accepted_for_objective"] = True
            session["task_sequence"]["leakage_controls"][
                "controller_verifier_scripts_and_canonical_copies_model_visible"
            ] = False
            session["cumulative_token_usage"].update(
                measurement_source="codex-jsonl-usage-events",
                fresh_input_tokens=5,
                cached_input_tokens=4,
                cache_write_tokens=None,
                output_tokens=1,
                reasoning_tokens=1,
                total_provider_tokens=10,
            )
            errors = self.production_v3_errors(session)
            self.assertTrue(any("replicate_index must be a non-negative integer" in error for error in errors), errors)
            self.assertTrue(any("canonical non-boolean provider-token usage" in error for error in errors), errors)

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
            run_path = ROOT / session["artifacts"]["run_record"]
            run_payload = json.loads(run_path.read_text())
            run_payload["verifier_integrity_passed"] = True
            run_path.write_text(json.dumps(run_payload, indent=2) + "\n")
            runner.write_manifest(run_path.parent)
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
                fresh_input_tokens=500,
                cached_input_tokens=400,
                cache_write_tokens=0,
                output_tokens=100,
                reasoning_tokens=50,
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
                comparison_baseline_session_id="unit-baseline",
                exclusion_reason="",
            )
            run_path = ROOT / session["artifacts"]["run_record"]
            run_payload = json.loads(run_path.read_text())
            run_payload.update(
                session_id=session["session_id"],
                replicate_index=session["replicate_index"],
                workflow_sequence_id=session["task_sequence"]["sequence_id"],
                profile_id=session["profile"]["profile_id"],
                accepted=True,
                frozen_protocol=copy.deepcopy(session["frozen_protocol"]),
                baseline_pool=copy.deepcopy(session["baseline_pool"]),
                selected_execution=copy.deepcopy(session["selected_execution"]),
                docker_image_identity=copy.deepcopy(session["docker_image_identity"]),
                tool_adapter_identity=copy.deepcopy(session["tool_adapter_identity"]),
                per_task_results=copy.deepcopy(session["per_task_results"]),
                verifier_integrity_passed=True,
                token_usage={
                    key: session["cumulative_token_usage"][key]
                    for key in validate_repository.PROVIDER_USAGE_FIELDS
                },
            )
            run_path.write_text(json.dumps(run_payload, indent=2) + "\n")
            runner.write_manifest(run_path.parent)
            self.assertEqual(self.production_v3_errors(session), [])
            legacy_errors = self.production_v3_errors(
                session,
                legacy_comparison_baseline=True,
            )
            self.assertTrue(
                any("error-free canonical schema-v2 baseline" in error for error in legacy_errors),
                legacy_errors,
            )
            symlink_errors = self.production_v3_errors(
                session,
                symlink_comparison_baseline=True,
            )
            self.assertTrue(
                any("compact artifact paths must use exact root" in error for error in symlink_errors),
                symlink_errors,
            )
            self.assertTrue(
                any("error-free canonical schema-v2 baseline" in error for error in symlink_errors),
                symlink_errors,
            )
            run_path = ROOT / session["artifacts"]["run_record"]
            run_root = run_path.parent
            original_run = json.loads(run_path.read_text())
            mutations = (
                lambda payload: payload["token_usage"].__setitem__(
                    "total_provider_tokens",
                    payload["token_usage"]["total_provider_tokens"] + 1,
                ),
                lambda payload: payload.__setitem__("accepted", False),
                lambda payload: payload.__setitem__("per_task_results", []),
            )
            for mutate in mutations:
                payload = copy.deepcopy(original_run)
                mutate(payload)
                run_path.write_text(json.dumps(payload, indent=2) + "\n")
                runner.write_manifest(run_root)
                mismatch_errors = self.production_v3_errors(session)
                self.assertTrue(
                    any("run.json does not exactly match registry session" in error for error in mismatch_errors),
                    mismatch_errors,
                )
            run_path.write_text(json.dumps(original_run, indent=2) + "\n")
            runner.write_manifest(run_root)

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
            self.assertTrue(any("run.json does not exactly match registry session" in error for error in self.production_v3_errors(session)))


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

    def test_contract_refresher_renders_registered_model_condition_launcher(self) -> None:
        command = contract_refresh.runner_command(
            {"id": "fastify-lifecycle-sequence-v0"},
            "baseline-bare-codex",
            ROOT / "sources/evaluations/protocols/sol-assisted.json",
            {
                "model_condition_override": {
                    "model_condition_id": "codex-openai-gpt-5-6-sol-high",
                    "model": "gpt-5.6-sol",
                    "reasoning_effort": "high",
                }
            },
        )
        self.assertIn("scripts/run_codex_workflow_model_condition.py", command)
        self.assertIn("--workflow-model-condition-id codex-openai-gpt-5-6-sol-high", command)
        self.assertIn("--workflow-model gpt-5.6-sol", command)
        self.assertIn("--workflow-reasoning-effort high", command)
        self.assertIn("--protocol sources/evaluations/protocols/sol-assisted.json", command)

    def test_unregistered_override_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            model_condition_runner.registered_condition("missing", "gpt-missing", "high")


class MatrixLifecycleContractTest(unittest.TestCase):
    def test_serial_lane_execution_is_fail_stop_and_does_not_prequeue(self) -> None:
        jobs = [("fastify", "baseline"), ("beets", "baseline"), ("terraform", "baseline")]
        calls: list[tuple[str, str]] = []

        def run(job: tuple[str, str]) -> dict[str, Any]:
            calls.append(job)
            if job[0] == "beets":
                raise FileNotFoundError("unit pre-provider lane failure")
            return {"lane_id": job[0], "exit_code": 0}

        with self.assertRaisesRegex(FileNotFoundError, "pre-provider lane failure"):
            matrix.execute_lane_jobs(jobs, 1, run)
        self.assertEqual(calls, jobs[:2])

        calls.clear()

        def return_nonzero(job: tuple[str, str]) -> dict[str, Any]:
            calls.append(job)
            return {"lane_id": job[0], "exit_code": 1 if job[0] == "beets" else 0}

        results = matrix.execute_lane_jobs(jobs, 1, return_nonzero)
        self.assertEqual(calls, jobs[:2])
        self.assertEqual([item["exit_code"] for item in results], [0, 1])
        self.assertEqual(matrix.execute_lane_jobs([], 3, return_nonzero), [])

    def test_validation_restores_protected_files_before_truthmark(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(
                 matrix.subprocess,
                 "run",
                 return_value=subprocess.CompletedProcess([], 0),
             ) as run, \
             mock.patch.object(matrix, "restore_protected_control_plane_files") as restore:
            result = matrix.run_validation(Path(tmp), sys.executable)
        self.assertTrue(result["passed"])
        self.assertEqual(run.call_count, 5)
        restore.assert_called_once_with(ROOT)

    def test_protected_test_restore_recovers_staged_deletion_from_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protected = root / "scripts/test_workflow_evaluation_contract.py"
            protected.parent.mkdir(parents=True)
            protected.write_text("protected\n")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "unit@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Unit Test"], cwd=root, check=True)
            subprocess.run(["git", "add", "--all"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=root, check=True)
            protected.unlink()
            subprocess.run(["git", "add", "--all"], cwd=root, check=True)
            matrix.restore_protected_control_plane_files(root)
            self.assertEqual(protected.read_text(), "protected\n")
            status = subprocess.run(
                ["git", "status", "--porcelain"], cwd=root, check=True, text=True, capture_output=True
            ).stdout
            self.assertEqual(status, "")

    def test_lane_checkout_excludes_parent_replication_receipts_in_fallback_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            destination = root / "destination"
            audits = source / "sources/evaluations/audits"
            attempts = audits / "current-low-complexity-baseline-r1-r2-attempts"
            attempts.mkdir(parents=True)
            (attempts / "beets-r1.json").write_text("{}\n")
            (audits / "retained-audit.json").write_text("{}\n")
            with mock.patch.object(matrix.shutil, "which", return_value=None):
                matrix.rsync_checkout(source, destination)
            self.assertFalse(
                (destination / "sources/evaluations/audits/current-low-complexity-baseline-r1-r2-attempts").exists()
            )
            self.assertTrue((destination / "sources/evaluations/audits/retained-audit.json").is_file())

    def test_current_replication_rejects_parallel_paid_plan_before_lane_root(self) -> None:
        with published_unoccupied_probe_worktree() as probe:
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_sequential_workflow_matrix.py",
                    "beets-lifecycle-sequence-v0",
                    "--replicate-index", "1",
                    "--max-parallel", "3",
                    "--workflow-model-condition-id", "codex-openai-gpt-5-6-sol-high",
                    "--workflow-model", "gpt-5.6-sol",
                    "--workflow-reasoning-effort", "high",
                    "--dry-run",
                ],
                cwd=probe,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --max-parallel 1", result.stderr + result.stdout)

    def test_paid_launch_checkout_gate_requires_clean_published_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            remote = base / "remote.git"
            root = base / "checkout"
            subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "config", "user.email", "unit@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Unit Test"], cwd=root, check=True)
            protected = root / "scripts/test_workflow_evaluation_contract.py"
            protected.parent.mkdir(parents=True)
            protected.write_text("protected\n")
            subprocess.run(["git", "add", "--all"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=root, check=True)
            subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=root, check=True)
            subprocess.run(["git", "push", "-q", "-u", "origin", "HEAD"], cwd=root, check=True)
            branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip()

            def gate() -> list[str]:
                with (
                    mock.patch.object(runner, "TRUSTED_REPOSITORY_ORIGIN", str(remote)),
                    mock.patch.object(runner, "TRUSTED_REPOSITORY_UPSTREAM", f"origin/{branch}"),
                    mock.patch.object(runner, "TRUSTED_REPOSITORY_REF", f"refs/heads/{branch}"),
                ):
                    return runner.paid_launch_checkout_errors(root)

            self.assertEqual(gate(), [])
            protected.unlink()
            subprocess.run(["git", "add", "--all"], cwd=root, check=True)
            errors = gate()
            self.assertTrue(any("protected control-plane" in error for error in errors), errors)
            self.assertTrue(any("not clean" in error for error in errors), errors)
            subprocess.run(
                ["git", "restore", "--source=HEAD", "--staged", "--worktree", "--", str(protected.relative_to(root))],
                cwd=root,
                check=True,
            )
            (root / "unpushed.txt").write_text("unpushed\n")
            subprocess.run(["git", "add", "--all"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "unpushed"], cwd=root, check=True)
            errors = gate()
            self.assertTrue(any("not the published upstream" in error for error in errors), errors)
            subprocess.run(["git", "push", "-q", "origin", "HEAD"], cwd=root, check=True)
            subprocess.run(["git", "checkout", "-q", "--detach", "HEAD"], cwd=root, check=True)
            errors = gate()
            self.assertTrue(any("published upstream is unreadable" in error for error in errors), errors)

    def test_provider_lane_clones_exact_trusted_published_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            remote = base / "remote.git"
            seed = base / "seed"
            destination = base / "lane"
            subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
            subprocess.run(["git", "init", "-q", str(seed)], check=True)
            subprocess.run(["git", "config", "user.email", "unit@example.invalid"], cwd=seed, check=True)
            subprocess.run(["git", "config", "user.name", "Unit Test"], cwd=seed, check=True)
            protected = seed / "scripts/test_workflow_evaluation_contract.py"
            protected.parent.mkdir(parents=True)
            protected.write_text("protected\n")
            subprocess.run(["git", "add", "--all"], cwd=seed, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=seed, check=True)
            subprocess.run(["git", "branch", "-M", "phase-3"], cwd=seed, check=True)
            subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=seed, check=True)
            subprocess.run(["git", "push", "-q", "-u", "origin", "phase-3"], cwd=seed, check=True)
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=seed, text=True).strip()
            with (
                mock.patch.object(runner, "TRUSTED_REPOSITORY_ORIGIN", str(remote)),
                mock.patch.object(matrix.workflow, "TRUSTED_REPOSITORY_ORIGIN", str(remote)),
            ):
                matrix.clone_published_checkout(destination, commit)
                self.assertEqual(runner.paid_launch_checkout_errors(destination), [])
            self.assertEqual(
                subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=destination, text=True).strip(),
                commit,
            )

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

    def test_plan_requires_explicit_baseline_gate(self) -> None:
        parameter = inspect.signature(matrix.plan_workflow_jobs).parameters["baseline_run_gate"]
        self.assertIs(parameter.default, inspect.Parameter.empty)

    def test_plan_blocks_occupied_baseline_before_creating_a_job(self) -> None:
        for treatment_profiles in ([], ["treatment"]):
            with self.subTest(treatment_profiles=treatment_profiles):
                with self.assertRaisesRegex(ValueError, "pilot identity is occupied"):
                    matrix.plan_workflow_jobs(
                        ["seq"],
                        treatment_profiles,
                        baseline_state=lambda _sequence: "missing",
                        profile_state=lambda _sequence, _profile: "missing",
                        baseline_run_gate=lambda _sequence: (False, "pilot identity is occupied"),
                    )

    def test_controller_validation_python_fails_closed_without_jsonschema(self) -> None:
        failed_probe = mock.Mock(returncode=1)
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch.object(matrix.sys, "executable", "/missing/controller-python"),
            mock.patch.object(matrix.shutil, "which", return_value="/missing/path-python"),
            mock.patch.object(matrix.subprocess, "run", return_value=failed_probe) as run_probe,
        ):
            with self.assertRaisesRegex(RuntimeError, "refusing to start lanes before validation is runnable"):
                matrix.controller_validation_python()
        self.assertEqual(run_probe.call_count, 2)

    def test_controller_validation_python_honors_prepared_override(self) -> None:
        with (
            mock.patch.dict(os.environ, {"WORKFLOW_VALIDATION_PYTHON": "/prepared/python"}, clear=True),
            mock.patch.object(matrix.subprocess, "run", return_value=mock.Mock(returncode=0)) as run_probe,
        ):
            self.assertEqual(matrix.controller_validation_python(), "/prepared/python")
        self.assertEqual(run_probe.call_args.args[0], ["/prepared/python", "-c", "import jsonschema"])

    def test_failed_lane_cannot_publish(self) -> None:
        self.assertFalse(
            matrix.publication_allowed(False, [{"exit_code": 1, "produced_session_ids": ["failed"]}])
        )
        self.assertFalse(
            matrix.publication_allowed(True, [{"exit_code": 0, "produced_session_ids": ["prepared"]}])
        )
        self.assertTrue(
            matrix.publication_allowed(False, [{"exit_code": 0, "produced_session_ids": ["valid"]}])
        )

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
            baseline_run_gate=lambda _sequence: (True, "unoccupied pilot identity"),
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

    def test_matrix_lane_publication_requires_exact_planned_job_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            checkout = Path(tmp)
            (checkout / "data").mkdir()
            selected = {"descriptor_sha256": "a" * 64, "descriptor": {"execution_role": "treatment"}}
            frozen = {"protocol_id": "planned", "path": "protocols/planned.json", "sha256": "b" * 64}
            session = {
                "session_id": "produced",
                "replicate_index": 0,
                "task_sequence": {
                    "sequence_id": "unit-sequence",
                    "prompt_delivery": {"mode": "sequential-one-task-at-a-time"},
                },
                "profile": {"profile_id": "wrong-profile"},
                "frozen_protocol": frozen,
                "baseline_pool": {"protocol_fingerprint": "unit-pool"},
                "selected_execution": selected,
            }
            (checkout / "data/workflow-sessions.json").write_text(
                json.dumps({"sessions": [session]}) + "\n"
            )
            expected = {
                "sequence_id": "unit-sequence",
                "profile_id": "expected-profile",
                "replicate_index": 0,
                "frozen_protocol": frozen,
                "baseline_pool_fingerprint": "unit-pool",
                "selected_execution": selected,
            }
            with self.assertRaisesRegex(ValueError, "planned job binding"):
                matrix.lane_session_records(checkout, expected, {"produced"})

    def test_matrix_artifact_ingress_fails_before_copy_on_invalid_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            checkout = Path(tmp)
            session = {
                "session_id": "bad-bundle",
                "artifacts": {
                    "root": "sources/evaluations/workflow-sessions/bad-bundle"
                },
            }
            with mock.patch.object(matrix.workflow, "pilot_session_artifacts_valid", return_value=False):
                with self.assertRaisesRegex(ValueError, "strict compact artifact ingress"):
                    matrix.copy_artifacts_for_sessions(checkout, [session])

    def test_matrix_publication_rollback_restores_registry_and_removes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "data/workflow-sessions.json"
            registry.parent.mkdir()
            before = b'{"sessions": []}\n'
            registry.write_text('{"sessions": [{"session_id": "contamination"}]}\n')
            artifact = root / "sources/evaluations/workflow-sessions/contamination"
            artifact.mkdir(parents=True)
            (artifact / "run.json").write_text("bad\n")
            runbook = root / "docs/evaluations/operations/runbook.md"
            runbook.parent.mkdir(parents=True)
            runbook.write_text("mutated\n")
            with mock.patch.object(matrix, "ROOT", root):
                matrix.rollback_matrix_publication(
                    registry,
                    before,
                    {"copied_artifacts": ["sources/evaluations/workflow-sessions/contamination"]},
                    [],
                    {runbook: b"original\n"},
                )
            self.assertEqual(registry.read_bytes(), before)
            self.assertFalse(artifact.exists())
            self.assertEqual(runbook.read_bytes(), b"original\n")

    def test_partial_comparison_publication_is_tracked_for_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry_path = root / "data/workflow-sessions.json"
            registry_path.parent.mkdir(parents=True)
            registry_path.write_text('{"sessions": []}\n')
            (root / matrix.WORKFLOW_ARTIFACT_ROOT).mkdir(parents=True)
            published: list[str] = []
            calls = 0

            def publish_one_then_fail(seq: dict[str, Any], _group: str, replicate: int, profile: str) -> dict[str, Any]:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise RuntimeError("second comparison failed")
                project_id = runner.PROJECT_META[seq["fixture_id"]]["project_id"]
                fingerprint = runner.baseline_protocol_fingerprint(seq)
                comparison_id = (
                    f"baseline-{runner.artifact_lane_label(project_id)}-{runner.DATE.replace('-', '')}"
                    f"-vs-{runner.artifact_profile_label(profile)}-p-{fingerprint}-r{replicate}"
                )
                (root / matrix.WORKFLOW_ARTIFACT_ROOT / f"{comparison_id}.json").write_text("{}\n")
                return {"comparison_id": comparison_id}

            with (
                mock.patch.object(matrix, "ROOT", root),
                mock.patch.object(matrix, "find_baseline_record", return_value={"session_id": "baseline"}),
                mock.patch.object(matrix, "baseline_reuse_state", return_value="reusable"),
                mock.patch.object(matrix.workflow, "find_pool_profile_record", return_value={"session_id": "treatment"}),
                mock.patch.object(matrix.workflow, "reviewed_session_reuse_state", return_value="reusable"),
                mock.patch.object(matrix.workflow, "write_comparison_if_ready", side_effect=publish_one_then_fail),
            ):
                with self.assertRaisesRegex(RuntimeError, "second comparison failed"):
                    matrix.publish_ready_comparisons(
                        ["fastify-lifecycle-sequence-v0", "beets-lifecycle-sequence-v0"],
                        ["terminal-tokenjuice-codex-hook-v1"],
                        0,
                        published,
                    )
                self.assertEqual(len(published), 2)
                self.assertTrue((root / published[0]).is_file())
                self.assertFalse((root / published[1]).exists())
                matrix.rollback_matrix_publication(
                    registry_path,
                    registry_path.read_bytes(),
                    {"copied_artifacts": []},
                    published,
                    {},
                )
                self.assertFalse((root / published[0]).exists())

    def test_merge_transaction_tracks_registry_replacement_before_fsync_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = "sources/evaluations/workflow-sessions/unit"
            (root / artifact).mkdir(parents=True)
            transaction: dict[str, Any] = {"skipped": "one or more lanes failed"}
            lane = {"checkout": str(root), "produced_session_ids": ["unit"], "expected_session_binding": {}}
            with (
                mock.patch.object(matrix, "ROOT", root),
                mock.patch.object(matrix, "lane_session_records", return_value=[{"session_id": "unit"}]),
                mock.patch.object(matrix.workflow, "pilot_session_artifacts_valid", return_value=True),
                mock.patch.object(matrix, "copy_artifacts_for_sessions", return_value=[artifact]),
                mock.patch.object(matrix, "merge_registry", side_effect=OSError("directory fsync failed after replace")),
            ):
                with self.assertRaisesRegex(OSError, "fsync failed"):
                    matrix.merge_lanes([lane], 0, transaction)
            self.assertTrue(transaction["registry_replacement_attempted"])
            self.assertEqual(transaction["merged_session_ids"], ["unit"])
            self.assertNotIn("skipped", transaction)

    def test_outer_transaction_rolls_back_tracked_artifact_on_keyboard_interrupt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = "sources/evaluations/workflow-sessions/interrupted"
            artifact_path = root / artifact
            artifact_path.mkdir(parents=True)
            registry_path = root / "data/workflow-sessions.json"
            registry_path.parent.mkdir(parents=True)
            registry_before = b'{"sessions": []}\n'
            registry_path.write_bytes(registry_before)
            transaction: dict[str, Any] = {}
            lane = {"checkout": str(root), "produced_session_ids": ["unit"], "expected_session_binding": {}}

            def interrupted_copy(_checkout: Path, _sessions: list[dict[str, Any]], copied: list[str]) -> list[str]:
                copied.append(artifact)
                raise KeyboardInterrupt()

            with (
                mock.patch.object(matrix, "ROOT", root),
                mock.patch.object(matrix, "lane_session_records", return_value=[{"session_id": "unit"}]),
                mock.patch.object(matrix.workflow, "pilot_session_artifacts_valid", return_value=True),
                mock.patch.object(matrix, "copy_artifacts_for_sessions", side_effect=interrupted_copy),
                mock.patch.object(matrix, "preserve_rejected_lane_artifacts", return_value=[]),
            ):
                with self.assertRaises(KeyboardInterrupt):
                    matrix.merge_lanes([lane], 0, transaction)
                self.assertTrue(artifact_path.exists())
                matrix.rollback_matrix_publication(
                    registry_path,
                    registry_before,
                    transaction,
                    [],
                    {},
                )
            self.assertFalse(artifact_path.exists())
            self.assertEqual(transaction["copied_artifacts"], [artifact])

    def test_merge_preserves_valid_sibling_when_failed_lane_session_is_rejected(self) -> None:
        valid = {"session_id": "valid-paid-session"}
        invalid = {"session_id": "invalid-diagnostic-session"}
        lane_results = [
            {
                "checkout": "/tmp/valid-lane",
                "lane_id": "valid-lane",
                "exit_code": 0,
                "produced_session_ids": [valid["session_id"]],
                "expected_session_binding": {},
            },
            {
                "checkout": "/tmp/failed-lane",
                "lane_id": "failed-lane",
                "exit_code": 1,
                "produced_session_ids": [invalid["session_id"]],
                "expected_session_binding": {},
            },
        ]
        copied_sessions: list[str] = []
        merged: list[dict] = []

        def copy_valid(_checkout, sessions, _copied):
            copied_sessions.extend(session["session_id"] for session in sessions)
            return _copied

        with (
            mock.patch.object(matrix, "lane_session_records", side_effect=[[valid], [invalid]]),
            mock.patch.object(matrix.workflow, "pilot_session_artifacts_valid", side_effect=[True, False]),
            mock.patch.object(matrix, "copy_artifacts_for_sessions", side_effect=copy_valid),
            mock.patch.object(matrix, "preserve_rejected_lane_artifacts", return_value=[]),
            mock.patch.object(matrix, "merge_registry", side_effect=lambda sessions: merged.extend(sessions)),
        ):
            summary = matrix.merge_lanes(lane_results, 0)
        self.assertEqual(copied_sessions, [valid["session_id"]])
        self.assertEqual(merged, [valid])
        self.assertEqual(summary["merged_session_ids"], [valid["session_id"]])
        self.assertEqual(summary["rejected_session_ids"], [invalid["session_id"]])

    def test_successful_lane_without_session_cannot_pass_or_publish(self) -> None:
        empty_lane = {
            "checkout": "/tmp/empty-lane",
            "lane_id": "empty-lane",
            "exit_code": 0,
            "produced_session_ids": [],
            "expected_session_binding": {},
        }
        self.assertFalse(matrix.publication_allowed(False, [empty_lane]))
        self.assertFalse(
            matrix.matrix_outputs_complete(
                prepare_only=False,
                planned_job_count=1,
                lane_results=[empty_lane],
                merge_summary={"merged_session_count": 0, "rejected_lane_errors": []},
            )
        )
        self.assertFalse(
            matrix.matrix_acceptance_state(
                prepare_only=False,
                execution_passed=False,
                awaiting_quality_review=False,
            )
        )
        with self.assertRaisesRegex(ValueError, "exactly one session"):
            matrix.lane_session_records(Path("/tmp/empty-lane"), {}, set())

    def test_zero_output_lane_cannot_hide_behind_valid_sibling(self) -> None:
        valid = {"session_id": "valid-sibling"}
        lane_results = [
            {
                "checkout": "/tmp/valid-lane",
                "lane_id": "valid-lane",
                "exit_code": 0,
                "produced_session_ids": [valid["session_id"]],
                "expected_session_binding": {},
            },
            {
                "checkout": "/tmp/empty-lane",
                "lane_id": "empty-lane",
                "exit_code": 0,
                "produced_session_ids": [],
                "expected_session_binding": {},
            },
        ]
        merged: list[dict] = []
        with (
            mock.patch.object(
                matrix,
                "lane_session_records",
                side_effect=[[valid], ValueError("matrix lane must produce exactly one session; found []")],
            ),
            mock.patch.object(matrix.workflow, "pilot_session_artifacts_valid", return_value=True),
            mock.patch.object(matrix, "copy_artifacts_for_sessions", return_value=[]),
            mock.patch.object(matrix, "merge_registry", side_effect=lambda sessions: merged.extend(sessions)),
        ):
            summary = matrix.merge_lanes(lane_results, 0)
        self.assertEqual(merged, [valid])
        self.assertEqual(summary["merged_session_ids"], [valid["session_id"]])
        self.assertTrue(summary["rejected_lane_errors"])
        self.assertFalse(matrix.publication_allowed(False, lane_results))
        self.assertFalse(
            matrix.matrix_outputs_complete(
                prepare_only=False,
                planned_job_count=2,
                lane_results=lane_results,
                merge_summary=summary,
            )
        )

    def test_merge_preserves_publication_error_for_outer_transaction_rollback(self) -> None:
        lane = {
            "checkout": "/tmp/unit-lane",
            "lane_id": "unit-lane",
            "exit_code": 0,
            "produced_session_ids": ["unit"],
            "expected_session_binding": {},
        }
        transaction: dict[str, Any] = {}

        def tracked_copy(_checkout, _sessions, copied):
            copied.append("sources/evaluations/workflow-sessions/unit")
            return copied

        with (
            mock.patch.object(matrix, "lane_session_records", return_value=[{"session_id": "unit"}]),
            mock.patch.object(matrix.workflow, "pilot_session_artifacts_valid", return_value=True),
            mock.patch.object(matrix, "copy_artifacts_for_sessions", side_effect=tracked_copy),
            mock.patch.object(matrix, "merge_registry", side_effect=RuntimeError("publication failed")),
            mock.patch.object(matrix.shutil, "rmtree", side_effect=OSError("cleanup failed")) as rmtree,
        ):
            with self.assertRaisesRegex(RuntimeError, "publication failed"):
                matrix.merge_lanes([lane], 0, transaction)
        rmtree.assert_not_called()
        self.assertEqual(
            transaction["copied_artifacts"],
            ["sources/evaluations/workflow-sessions/unit"],
        )

    def test_compact_artifacts_are_fsynced_before_registry_publication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            checkout = temp_root / "checkout"
            session_id = "unit-durable-session"
            relative_root = Path("sources/evaluations/workflow-sessions") / session_id
            source = checkout / relative_root
            source.mkdir(parents=True)
            for name in matrix.COMPACT_ARTIFACT_NAMES:
                (source / name).write_bytes(b"unit")
            session = {
                "session_id": session_id,
                "artifacts": {
                    "artifact_contract": "compact-v1-four-files",
                    "root": str(relative_root),
                },
            }
            copied: list[str] = []
            with (
                mock.patch.object(matrix, "ROOT", temp_root),
                mock.patch.object(matrix.workflow, "pilot_session_artifacts_valid", return_value=True),
                mock.patch.object(
                    matrix,
                    "fsync_compact_artifact_tree",
                    side_effect=OSError("artifact fsync failed"),
                ) as fsync_tree,
            ):
                with self.assertRaisesRegex(OSError, "artifact fsync failed"):
                    matrix.copy_artifacts_for_sessions(checkout, [session], copied)
            fsync_tree.assert_called_once_with(temp_root / relative_root)
            self.assertEqual(copied, [str(relative_root)])

    def test_publication_guard_rolls_back_interrupt_after_validation_result(self) -> None:
        for validation_passed in (True, False):
            rollbacks: list[bool] = []
            with self.assertRaises(KeyboardInterrupt):
                with matrix.publication_transaction_guard(
                    lambda: rollbacks.append(validation_passed),
                    enabled=True,
                ):
                    validation = {"passed": validation_passed}
                    self.assertEqual(validation["passed"], validation_passed)
                    raise KeyboardInterrupt()
            self.assertEqual(rollbacks, [validation_passed])

    def test_matrix_registry_merge_atomically_rejects_full_slot_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            registry_path = root / "data/workflow-sessions.json"
            registry_path.write_text('{"sessions": []}\n')
            first = {
                "schema_version": 2,
                "session_id": "first",
                "replicate_index": 0,
                "task_sequence": {"sequence_id": "unit-sequence"},
                "profile": {"profile_id": "baseline-bare-codex"},
                "baseline_pool": {"protocol_fingerprint": "unit-pool"},
                "frozen_protocol": {
                    "protocol_id": "unit-protocol",
                    "path": "protocols/unit-protocol.json",
                    "sha256": "a" * 64,
                },
            }
            duplicate = copy.deepcopy(first)
            duplicate["session_id"] = "different-session-id"
            with mock.patch.object(matrix, "ROOT", root):
                with self.assertRaisesRegex(FileExistsError, "slot already occupied"):
                    matrix.merge_registry([first, duplicate])
                self.assertEqual(json.loads(registry_path.read_text())["sessions"], [])
                matrix.merge_registry([first])
                with self.assertRaisesRegex(FileExistsError, "slot already occupied"):
                    matrix.merge_registry([duplicate])
            self.assertEqual(
                [item["session_id"] for item in json.loads(registry_path.read_text())["sessions"]],
                ["first"],
            )
            self.assertEqual(list((root / "data").glob(".workflow-sessions.json.*.tmp")), [])

    def test_matrix_reuse_has_no_weaker_hard_baseline_fallback(self) -> None:
        malformed = {
            "interpretation": {
                "primary_objective_hard_baseline": True,
                "usable_for_primary_objective_token_comparison": True,
                "operationally_completed": True,
            },
            "cumulative_token_usage": {"total_provider_tokens": True},
            "artifacts": {
                "run_record": "one-file",
                "final_diff": "one-file",
                "evidence_bundle": "one-file",
                "manifest": "one-file",
            },
        }
        with mock.patch.object(matrix.workflow, "reviewed_session_reuse_state", return_value="occupied"):
            self.assertEqual(matrix.baseline_reuse_state(malformed), "occupied")
        self.assertFalse(hasattr(matrix, "hard_baseline_usable"))
        self.assertFalse(hasattr(matrix, "write_hard_baseline_comparison"))

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
                baseline_run_gate=lambda _sequence: (True, "unused for occupied baseline"),
            )

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
            with self.assertRaisesRegex(ValueError, "strict compact artifact ingress|escapes lane checkout"):
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


class BaselineV3LowComplexityContractTest(unittest.TestCase):
    def test_active_sequences_bind_zero_mistake_generation_contracts(self) -> None:
        document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        active = [sequence for sequence in document["sequences"] if sequence["status"] == "active"]
        self.assertEqual(len(active), 3)
        expected_generations = {
            "fastify-lifecycle-sequence-v0": "baseline-v3",
            "beets-lifecycle-sequence-v0": "baseline-v4",
            "terraform-lifecycle-sequence-v0": "baseline-v4",
        }

        for sequence in active:
            generation = expected_generations[sequence["id"]]
            generation_label = generation.replace("baseline-v", "Baseline V")
            self.assertEqual(sequence["task_family_generation"], generation)
            self.assertEqual(
                Path(sequence["qualification_path"]).name,
                f"qualification-lifecycle-v0-{generation}.json",
            )
            gate = sequence["mistake_gate"]
            self.assertEqual(gate["designated_model_condition"], "codex-openai-gpt-5-6-sol-high")
            self.assertEqual(gate["model"], "gpt-5.6-sol")
            self.assertEqual(gate["reasoning_effort"], "high")
            self.assertEqual(gate["allowed_unique_model_incidents"], 0)
            self.assertEqual(gate["allowed_corrected_implementation_mistakes"], 0)
            self.assertEqual(gate["allowed_unresolved_defects"], 0)
            self.assertEqual(gate["allowed_prohibited_operations"], 0)
            self.assertEqual(gate["allowed_unnecessary_exploration_incidents"], 0)
            self.assertEqual(gate["allowed_model_caused_failed_commands"], 0)
            self.assertEqual(gate["allowed_code_rework_events"], 0)
            self.assertEqual(gate["allowed_verifier_or_environment_failures"], 0)
            for key, value in gate.items():
                if key.startswith("allowed_"):
                    self.assertIs(type(value), int, (sequence["id"], key, value))
                    self.assertEqual(value, 0, (sequence["id"], key, value))
            self.assertEqual(gate["incident_counting"], "unique-auditable-not-command-count")
            self.assertEqual(
                gate["pilot_audit_path"],
                f"sources/evaluations/audits/{generation}-pilot-zero-mistake.json",
            )
            treatment_ready, _reason = runner.baseline_v2_treatment_gate(sequence, ROOT)
            expected_gate_status = "passed-zero-incident" if treatment_ready else "provider-pilot-required"
            self.assertEqual(gate["status"], expected_gate_status)

            for task in sequence["tasks"]:
                self.assertIn(f"/{generation}/", task["prompt_path"])
                self.assertEqual(task["acceptance_visibility"], "model-visible-complete")
                task_dir = (ROOT / task["prompt_path"]).parent
                prompt = (ROOT / task["prompt_path"]).read_text()
                verifier = (ROOT / task["verifier_command"]).read_text()
                for marker in ("<<'NODE'", '<<"NODE"', "<<'PY'", '<<"PY"', "<<'TS'", '<<"TS"', "workflow-hidden"):
                    self.assertFalse(marker in verifier and marker not in prompt, (sequence["id"], task["id"], marker))
                for marker in (
                    f"{generation_label} mechanical",
                    "Do not discover or redesign anything.",
                    "Copy and run this command exactly:",
                    "Do not inspect, search, modify tests, run anything else, or evaluate aggregate Git state.",
                    "stop immediately when it exits 0",
                ):
                    self.assertIn(marker, prompt, (sequence["id"], task["id"], marker))

                production_paths = [
                    path
                    for path in validate_repository.patch_paths(task_dir / "seed-regression.patch")
                    if validate_repository.is_production_path(path)
                    and not path.endswith(("_test.go", "_test.py", ".test.js"))
                    and not path.startswith("test/")
                ]
                self.assertGreaterEqual(len(production_paths), 1)
                self.assertLessEqual(len(production_paths), 3)
                self.assertEqual(sorted(production_paths), sorted(task["expected_changed_paths"]))
                self.assertTrue(task["model_visible_validation_anchors"])
                self.assertEqual(task.get("model_concealed_paths", []), [])
                verifier = (ROOT / task["verifier_command"]).read_text()
                for anchor in task["model_visible_validation_anchors"]:
                    self.assertIn(anchor, prompt)
                    self.assertIn(anchor, verifier)

                if task["task_class"] == "code-review-correction":
                    self.assertTrue((task_dir / task["review_patch_path"]).is_file())

    def test_v3_prompts_bind_portable_locked_validation_commands(self) -> None:
        document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        for sequence in document["sequences"]:
            for task in sequence["tasks"]:
                prompt = (ROOT / task["prompt_path"]).read_text()
                verifier = (ROOT / task["verifier_command"]).read_text()
                self.assertEqual(prompt.count("```bash"), 1, task["id"])
                self.assertEqual(prompt.count("```"), 2, task["id"])
                self.assertIn("stop immediately when it exits 0", prompt, task["id"])
                self.assertNotIn("git diff", prompt, task["id"])
                rendered = runner.render_task_prompt(
                    sequence,
                    "baseline-bare-codex",
                    int(task["order"]),
                    prompt,
                    first_task=int(task["order"]) == 1,
                )
                self.assertIn("Run only the exact command block", rendered, task["id"])
                self.assertNotIn("current and previously disclosed work", rendered, task["id"])
                if sequence["fixture_id"] == "medium-beetbox-beets":
                    self.assertNotIn("--no-project", prompt)
                    self.assertNotIn("--no-project", verifier)
                    self.assertIn("uv run --offline --frozen", prompt)
                    self.assertIn("uv run --offline --frozen", verifier)
                if sequence["fixture_id"] == "large-hashicorp-terraform":
                    export = "export PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH"
                    self.assertIn(export, prompt)
                    self.assertIn(export, verifier)
                    self.assertNotIn("BaselineV2", prompt + verifier)
                    acceptance_root = (ROOT / task["prompt_path"]).parent / "controller-visible"
                    for asset in acceptance_root.rglob("*"):
                        if asset.is_file():
                            self.assertNotIn("BaselineV2", asset.read_text(), str(asset))

    def test_active_fixture_setup_and_reset_pin_the_sequence_snapshot(self) -> None:
        document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        fixtures = {
            item["id"]: item
            for item in json.loads((ROOT / "data/repository-fixtures.json").read_text())["fixtures"]
        }
        for sequence in document["sequences"]:
            fixture = fixtures[sequence["fixture_id"]]
            commit = fixture["snapshot"]["commit"]
            self.assertEqual(sequence["initial_snapshot"]["commit"], commit)
            for command_key in ("setup", "reset"):
                script = ROOT / fixture[command_key]["command"]
                script_text = script.read_text()
                if commit not in script_text:
                    self.assertEqual(command_key, "reset", (sequence["id"], command_key))
                    self.assertIn(Path(fixture["setup"]["command"]).name, script_text)

    def test_generated_runbook_matches_current_pilot_authorization_and_occupancy(self) -> None:
        runbook = (ROOT / "docs/evaluations/operations/runbook.md").read_text()
        document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        authorization = json.loads(
            (ROOT / "sources/evaluations/audits/baseline-v4-task-family-qualification-20260722.json").read_text()
        )
        v4_authorized = authorization["paid_pilot_authorized"] is True
        unoccupied_authorized_v4: list[str] = []
        flags = "--workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high"
        for sequence in document["sequences"]:
            prepare_command = f"python3 scripts/run_sequential_workflow_matrix.py {sequence['id']} {flags} --prepare-only"
            paid_command = f"python3 scripts/run_sequential_workflow_matrix.py {sequence['id']} {flags}"
            receipt = runner.baseline_pilot_attempt_receipt_path(sequence, ROOT)
            if sequence["task_family_generation"] == "baseline-v3":
                self.assertTrue(receipt.is_file())
                self.assertNotIn(prepare_command, runbook)
            else:
                if receipt.exists():
                    self.assertNotIn(paid_command, runbook.splitlines())
                else:
                    self.assertIn(prepare_command, runbook)
                    if v4_authorized:
                        unoccupied_authorized_v4.append(sequence["id"])
                        self.assertIn(paid_command, runbook.splitlines())
                    else:
                        self.assertNotIn(paid_command, runbook.splitlines())
        if v4_authorized:
            self.assertNotIn("Paid pilot execution is not authorized", runbook)
            if unoccupied_authorized_v4:
                self.assertIn("Only an unoccupied designated baseline pilot identity may run", runbook)
            else:
                self.assertNotIn("Only an unoccupied designated baseline pilot identity may run", runbook)
        else:
            self.assertIn("Paid pilot execution is not authorized", runbook)
        for replicate_index in (1, 2, 3):
            runnable = [
                sequence
                for sequence in document["sequences"]
                if runner.baseline_v2_pilot_run_gate(sequence, ROOT, replicate_index)[0]
            ]
            if not runnable:
                continue
            sequence_args = " ".join(sequence["id"] for sequence in runnable)
            command = (
                f"python3 scripts/run_sequential_workflow_matrix.py {sequence_args} "
                f"--replicate-index {replicate_index} --max-parallel 1 {flags}"
            )
            self.assertIn(command + " --prepare-only", runbook.splitlines())
            self.assertIn(command, runbook.splitlines())
        blocked_v4 = [
            sequence
            for sequence in document["sequences"]
            if sequence["task_family_generation"] == "baseline-v4"
            and not runner.baseline_v2_treatment_gate(sequence, ROOT)[0]
        ]
        if v4_authorized and not unoccupied_authorized_v4 and blocked_v4:
            self.assertIn("The designated pilot identities are occupied by immutable attempt evidence", runbook)
        else:
            self.assertNotIn("The designated pilot identities are occupied", runbook)

    def test_provider_free_v3_qualifications_pass_every_boundary(self) -> None:
        document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        for sequence in document["sequences"]:
            qualification = json.loads((ROOT / sequence["qualification_path"]).read_text())
            for key in (
                "composite_seed_merge_zero",
                "composite_seeded_verifiers_nonzero",
                "seeded_verifier_nonzero",
                "fixed_verifier_zero",
                "full_fixed_cumulative_verifier_zero",
                "no_unmerged_paths",
            ):
                self.assertIs(qualification[key], True, (sequence["id"], key))
            self.assertTrue(all(task["production_file_count"] <= 3 for task in qualification["tasks"]))

    def test_v3_audit_records_all_nine_literal_prompt_command_rehearsals(self) -> None:
        audit = json.loads(
            (ROOT / "sources/evaluations/audits/baseline-v3-task-family-qualification-20260722.json").read_text()
        )
        rehearsal = audit["literal_prompt_command_rehearsal"]
        self.assertEqual(rehearsal["status"], "passed")
        self.assertEqual(rehearsal["provider_calls"], 0)
        self.assertEqual(rehearsal["provider_tokens"], 0)
        tasks = [task for sequence in rehearsal["sequences"] for task in sequence["tasks"]]
        self.assertEqual(len(tasks), 9)
        for task in tasks:
            self.assertIs(type(task["prompt_command_exit"]), int)
            self.assertEqual(task["prompt_command_exit"], 0)
            self.assertIs(type(task["controller_verifier_exit"]), int)
            self.assertEqual(task["controller_verifier_exit"], 0)
            self.assertIs(task["model_visible_focused_test_selected"], True)

    def test_rejected_compact_evidence_is_preserved_before_lane_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            checkout = temp / "checkout"
            lane_dir = temp / "lane"
            lane_dir.mkdir()
            session_id = "baseline-v3-rejected-unit"
            source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / session_id
            source.mkdir(parents=True)
            original = {
                "run.json": b'{"schema_version":2}\n',
                "changes.diff": b"diff --git a/a b/a\n",
                "evidence.jsonl.gz": b"production-shaped-invalid-evidence",
                "manifest.sha256": b"unit manifest\n",
            }
            for name, content in original.items():
                (source / name).write_bytes(content)
            result = {
                "lane_id": "lane-unit",
                "sequence_id": "fastify-lifecycle-sequence-v0",
                "lane_dir": str(lane_dir),
                "checkout": str(checkout),
                "produced_session_ids": [session_id],
                "expected_session_binding": {},
            }
            with mock.patch.object(matrix, "lane_session_records", return_value=[{"session_id": session_id}]), \
                 mock.patch.object(matrix.workflow, "pilot_session_artifacts_valid", return_value=False):
                summary = matrix.merge_lanes([result], replicate_index=0)
            destination = lane_dir / "rejected-evidence" / session_id
            self.assertEqual(summary["rejected_session_ids"], [session_id])
            self.assertIn(str(destination), result["failure_evidence"])
            for name, content in original.items():
                self.assertEqual((destination / name).read_bytes(), content)
            rejection = json.loads((destination / "rejection.json").read_text())
            self.assertEqual(rejection["session_id"], session_id)
            self.assertIs(rejection["accepted_evidence"], False)
            self.assertIn("strict compact artifact ingress", rejection["reason"])
            self.assertFalse(any(path.name.startswith(f".{session_id}.tmp-") for path in destination.parent.iterdir()))

    def test_rejected_evidence_copy_failure_retains_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp) / "matrix-run"
            checkout = run_root / "lane" / "checkout"
            source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "rejected-unit"
            source.mkdir(parents=True)
            (source / "run.json").write_text("{}\n")
            result = {"lane_id": "lane", "lane_dir": str(run_root / "lane")}
            with mock.patch.object(matrix.shutil, "copy2", side_effect=OSError("injected copy failure")):
                with self.assertRaises(OSError):
                    matrix.preserve_rejected_lane_artifacts(
                        result,
                        checkout,
                        {"rejected-unit"},
                        "strict compact artifact ingress rejected the session",
                    )
            sentinel = run_root / matrix.PRESERVATION_FAILURE_SENTINEL
            self.assertTrue(sentinel.is_file())
            self.assertTrue(source.is_dir())
            matrix.cleanup_lane_checkouts(run_root)
            self.assertTrue(checkout.is_dir())
            self.assertFalse((run_root / "lane/rejected-evidence/rejected-unit").exists())

    def test_rejected_evidence_interruptions_retain_source_checkout(self) -> None:
        for interruption in (KeyboardInterrupt("unit interrupt"), SystemExit("unit exit")):
            with self.subTest(interruption=type(interruption).__name__), tempfile.TemporaryDirectory() as tmp:
                run_root = Path(tmp) / "matrix-run"
                checkout = run_root / "lane" / "checkout"
                source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "rejected-unit"
                source.mkdir(parents=True)
                (source / "run.json").write_text("{}\n")
                result = {"lane_id": "lane", "lane_dir": str(run_root / "lane")}
                with mock.patch.object(matrix.shutil, "copy2", side_effect=interruption):
                    with self.assertRaises(type(interruption)):
                        matrix.preserve_rejected_lane_artifacts(
                            result,
                            checkout,
                            {"rejected-unit"},
                            "strict compact artifact ingress rejected the session",
                        )
                matrix.cleanup_lane_checkouts(run_root)
                self.assertTrue(checkout.is_dir())

    def test_preservation_sentinel_write_failure_still_blocks_cleanup_in_memory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp) / "matrix-run"
            checkout = run_root / "lane" / "checkout"
            source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "rejected-unit"
            source.mkdir(parents=True)
            (source / "run.json").write_text("{}\n")
            result = {"lane_id": "lane", "lane_dir": str(run_root / "lane")}
            with mock.patch.object(matrix, "atomic_write_json", side_effect=OSError("injected sentinel failure")):
                with self.assertRaises(OSError):
                    matrix.preserve_rejected_lane_artifacts(
                        result,
                        checkout,
                        {"rejected-unit"},
                        "strict compact artifact ingress rejected the session",
                    )
            self.assertIn(run_root.resolve(), matrix.CLEANUP_PROHIBITED_RUN_ROOTS)
            matrix.cleanup_lane_checkouts(run_root)
            self.assertTrue(checkout.is_dir())
            matrix.CLEANUP_PROHIBITED_RUN_ROOTS.discard(run_root.resolve())

    def test_strict_ingress_interrupt_preserves_before_reraising(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp) / "matrix-run"
            lane_dir = run_root / "lane"
            checkout = lane_dir / "checkout"
            session_id = "interrupt-unit"
            source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / session_id
            source.mkdir(parents=True)
            (source / "run.json").write_text("{}\n")
            result = {
                "lane_id": "lane",
                "lane_dir": str(lane_dir),
                "checkout": str(checkout),
                "produced_session_ids": [session_id],
                "expected_session_binding": {},
            }
            with mock.patch.object(matrix, "lane_session_records", return_value=[{"session_id": session_id}]), \
                 mock.patch.object(matrix.workflow, "pilot_session_artifacts_valid", side_effect=KeyboardInterrupt("unit interrupt")):
                with self.assertRaises(KeyboardInterrupt):
                    matrix.merge_lanes([result], replicate_index=0)
            self.assertTrue((lane_dir / "rejected-evidence" / session_id / "rejection.json").is_file())

    def test_direct_runner_applies_strict_ingress_before_registry_publication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "sources/evaluations/workflow-sessions/direct-invalid"
            run_dir.mkdir(parents=True)
            record = {
                "session_id": "direct-invalid",
                "task_sequence": {"sequence_id": "fastify-lifecycle-sequence-v0"},
                "artifacts": {"root": str(run_dir.relative_to(root))},
            }
            sequence = {"mistake_gate": {"attempt_receipt_path": "sources/evaluations/audits/direct-attempt.json"}}
            with (
                mock.patch.object(runner, "ROOT", root),
                mock.patch.object(runner, "load_sequence", return_value=sequence),
                mock.patch.object(runner, "pilot_session_artifacts_valid", return_value=False),
                mock.patch.object(runner, "update_registry") as publish,
            ):
                with self.assertRaisesRegex(RuntimeError, "strict compact artifact ingress"):
                    runner.publish_session_after_strict_ingress(record, run_dir)
                publish.assert_not_called()
            rejection = run_dir.parent / "direct-invalid.strict-ingress-rejection.json"
            self.assertTrue(rejection.is_file())
            self.assertTrue(run_dir.is_dir())

    def test_provider_lane_interrupt_preserves_evidence_before_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_root = root / "matrix"
            sequence_id = "fastify-lifecycle-sequence-v0"
            profile_id = "baseline-bare-codex"
            lane_id = matrix.safe_name(f"{sequence_id}--{profile_id}")
            lane_dir = run_root / lane_id
            session_id = "interrupted-paid-session"
            reservation_seen = False

            def prepare_checkout(_source: Path, checkout: Path) -> None:
                (checkout / "data").mkdir(parents=True)
                (checkout / "data/workflow-sessions.json").write_text('{"sessions": []}\n')
                (checkout / matrix.WORKFLOW_ARTIFACT_ROOT).mkdir(parents=True)
                (checkout / "protocol.json").write_text(json.dumps({
                    "protocol_id": "unit-protocol",
                    "baseline_pool": {"protocol_fingerprint": "unit-pool"},
                    "selected_execution": {},
                }))
                # Simulate external scratch reclamation during a long trusted clone.
                shutil.rmtree(lane_dir / "logs")
                shutil.rmtree(lane_dir / "tmp")

            def interrupt_after_evidence(*_args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
                self.assertTrue(reservation_seen)
                self.assertTrue((lane_dir / matrix.LANE_CLEANUP_PROHIBITION_SENTINEL).is_file())
                checkout = Path(kwargs["cwd"])
                evidence = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / session_id
                evidence.mkdir()
                (evidence / "run.json").write_text("{}\n")
                raise KeyboardInterrupt("unit interrupt after evidence")

            def reserve_after_log_open(*_args: Any, **_kwargs: Any) -> None:
                nonlocal reservation_seen
                self.assertTrue((lane_dir / "logs/lane.log").is_file())
                reservation_seen = True

            with (
                mock.patch.object(matrix, "ROOT", root),
                mock.patch.object(matrix, "clone_published_checkout", side_effect=lambda destination, _commit: prepare_checkout(root, destination)),
                mock.patch.object(matrix, "find_protocol", side_effect=lambda checkout, *_: checkout / "protocol.json"),
                mock.patch.object(matrix, "workflow_lane_command", return_value=["unit-child"]),
                mock.patch.object(matrix.workflow, "load_sequence", return_value={"task_family_generation": "baseline-v3"}),
                mock.patch.object(matrix.workflow, "reserve_baseline_pilot_attempt", side_effect=reserve_after_log_open),
                mock.patch.object(matrix.subprocess, "run", side_effect=interrupt_after_evidence),
            ):
                with self.assertRaises(KeyboardInterrupt):
                    matrix.run_flow_lane(
                        sequence_id=sequence_id,
                        treatment_profile=profile_id,
                        lane_root=run_root,
                        replicate_index=0,
                        runner_args=[],
                        source_codex_home=None,
                        production_lock_fd=123,
                        published_launch_commit="unit-published",
                    )
            preserved = lane_dir / "rejected-evidence" / session_id / "rejection.json"
            self.assertTrue(preserved.is_file())
            matrix.cleanup_lane_checkouts(run_root)
            self.assertTrue(preserved.is_file())

    def test_provider_lane_post_child_registry_failure_preserves_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_root = root / "matrix"
            sequence_id = "fastify-lifecycle-sequence-v0"
            profile_id = "baseline-bare-codex"
            lane_id = matrix.safe_name(f"{sequence_id}--{profile_id}")
            lane_dir = run_root / lane_id
            session_id = "malformed-registry-paid-session"

            def prepare_checkout(_source: Path, checkout: Path) -> None:
                (checkout / "data").mkdir(parents=True)
                (checkout / "data/workflow-sessions.json").write_text('{"sessions": []}\n')
                (checkout / matrix.WORKFLOW_ARTIFACT_ROOT).mkdir(parents=True)
                (checkout / "protocol.json").write_text(json.dumps({
                    "protocol_id": "unit-protocol",
                    "baseline_pool": {"protocol_fingerprint": "unit-pool"},
                    "selected_execution": {},
                }))

            def corrupt_registry_after_evidence(*_args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
                checkout = Path(kwargs["cwd"])
                evidence = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / session_id
                evidence.mkdir()
                (evidence / "run.json").write_text("{}\n")
                (checkout / "data/workflow-sessions.json").write_text("not-json\n")
                return subprocess.CompletedProcess(["unit-child"], 0)

            with (
                mock.patch.object(matrix, "ROOT", root),
                mock.patch.object(matrix, "clone_published_checkout", side_effect=lambda destination, _commit: prepare_checkout(root, destination)),
                mock.patch.object(matrix, "find_protocol", side_effect=lambda checkout, *_: checkout / "protocol.json"),
                mock.patch.object(matrix, "workflow_lane_command", return_value=["unit-child"]),
                mock.patch.object(matrix.subprocess, "run", side_effect=corrupt_registry_after_evidence),
            ):
                with self.assertRaises(json.JSONDecodeError):
                    matrix.run_flow_lane(
                        sequence_id=sequence_id,
                        treatment_profile=profile_id,
                        lane_root=run_root,
                        replicate_index=0,
                        runner_args=[],
                        source_codex_home=None,
                        published_launch_commit="unit-published",
                    )
            preserved = lane_dir / "rejected-evidence" / session_id / "rejection.json"
            self.assertTrue(preserved.is_file())
            matrix.cleanup_lane_checkouts(run_root)
            self.assertTrue(preserved.is_file())

    def test_nonzero_provider_lane_unsafe_artifact_retains_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_root = root / "matrix"
            sequence_id = "fastify-lifecycle-sequence-v0"
            profile_id = "baseline-bare-codex"
            lane_id = matrix.safe_name(f"{sequence_id}--{profile_id}")
            lane_dir = run_root / lane_id

            def prepare_checkout(_source: Path, checkout: Path) -> None:
                (checkout / "data").mkdir(parents=True)
                (checkout / "data/workflow-sessions.json").write_text('{"sessions": []}\n')
                (checkout / matrix.WORKFLOW_ARTIFACT_ROOT).mkdir(parents=True)
                (checkout / "protocol.json").write_text(json.dumps({
                    "protocol_id": "unit-protocol",
                    "baseline_pool": {"protocol_fingerprint": "unit-pool"},
                    "selected_execution": {},
                }))

            def fail_with_unsafe_output(*_args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
                self.assertTrue((lane_dir / matrix.LANE_CLEANUP_PROHIBITION_SENTINEL).is_file())
                checkout = Path(kwargs["cwd"])
                (checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "unsafe-regular-file").write_text("evidence\n")
                return subprocess.CompletedProcess(["unit-child"], 1)

            with (
                mock.patch.object(matrix, "ROOT", root),
                mock.patch.object(matrix, "clone_published_checkout", side_effect=lambda destination, _commit: prepare_checkout(root, destination)),
                mock.patch.object(matrix, "find_protocol", side_effect=lambda checkout, *_: checkout / "protocol.json"),
                mock.patch.object(matrix, "workflow_lane_command", return_value=["unit-child"]),
                mock.patch.object(matrix.subprocess, "run", side_effect=fail_with_unsafe_output),
            ):
                result = matrix.run_flow_lane(
                    sequence_id=sequence_id,
                    treatment_profile=profile_id,
                    lane_root=run_root,
                    replicate_index=0,
                    runner_args=[],
                    source_codex_home=None,
                    published_launch_commit="unit-published",
                )
            self.assertEqual(result["exit_code"], 1)
            self.assertEqual(result["failure_evidence"], [])
            checkout = lane_dir / "checkout"
            matrix.cleanup_lane_checkouts(run_root)
            self.assertTrue((checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "unsafe-regular-file").is_file())
            matrix.CLEANUP_PROHIBITED_LANE_DIRS.discard(lane_dir.resolve())

    def test_provider_lane_symlinked_registry_retains_whole_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_root = root / "matrix"
            sequence_id = "fastify-lifecycle-sequence-v0"
            profile_id = "baseline-bare-codex"
            lane_id = matrix.safe_name(f"{sequence_id}--{profile_id}")
            lane_dir = run_root / lane_id

            def prepare_checkout(_source: Path, checkout: Path) -> None:
                (checkout / "data").mkdir(parents=True)
                (checkout / "data/workflow-sessions.json").write_text('{"sessions": []}\n')
                (checkout / matrix.WORKFLOW_ARTIFACT_ROOT).mkdir(parents=True)
                (checkout / "protocol.json").write_text(json.dumps({
                    "protocol_id": "unit-protocol",
                    "baseline_pool": {"protocol_fingerprint": "unit-pool"},
                    "selected_execution": {},
                }))

            def replace_registry(*_args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
                checkout = Path(kwargs["cwd"])
                evidence = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "internal-session"
                evidence.mkdir()
                (evidence / "run.json").write_text("{}\n")
                external = root / "external-registry.json"
                external.write_text('{"sessions": []}\n')
                registry = checkout / "data/workflow-sessions.json"
                registry.unlink()
                registry.symlink_to(external)
                return subprocess.CompletedProcess(["unit-child"], 1)

            with (
                mock.patch.object(matrix, "ROOT", root),
                mock.patch.object(matrix, "clone_published_checkout", side_effect=lambda destination, _commit: prepare_checkout(root, destination)),
                mock.patch.object(matrix, "find_protocol", side_effect=lambda checkout, *_: checkout / "protocol.json"),
                mock.patch.object(matrix, "workflow_lane_command", return_value=["unit-child"]),
                mock.patch.object(matrix.subprocess, "run", side_effect=replace_registry),
            ):
                with self.assertRaises(matrix.UnsafeLaneOutputError):
                    matrix.run_flow_lane(
                        sequence_id=sequence_id,
                        treatment_profile=profile_id,
                        lane_root=run_root,
                        replicate_index=0,
                        runner_args=[],
                        source_codex_home=None,
                        published_launch_commit="unit-published",
                    )
            matrix.cleanup_lane_checkouts(run_root)
            self.assertTrue((lane_dir / "checkout").is_dir())
            self.assertFalse((lane_dir / "rejected-evidence/internal-session").exists())
            matrix.CLEANUP_PROHIBITED_LANE_DIRS.discard(lane_dir.resolve())

    def test_v3_validator_rejects_non_integer_provider_counts_and_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            audit_rel = Path("sources/evaluations/audits/baseline-v3-task-family-qualification-20260722.json")
            index_rel = Path("sources/evaluations/audits/baseline-v3-literal-command-receipts-20260722/index.json")
            sequence_rel = Path("data/workflow-task-sequences.json")
            audit = json.loads((ROOT / audit_rel).read_text())
            index = json.loads((ROOT / index_rel).read_text())
            sequences = json.loads((ROOT / sequence_rel).read_text())
            paths = {audit_rel, index_rel, sequence_rel}
            for sequence in sequences["sequences"]:
                qualification_path = str(sequence["qualification_path"])
                if sequence.get("task_family_generation") == "baseline-v4":
                    qualification_path = qualification_path.replace("baseline-v4", "baseline-v3")
                paths.add(Path(qualification_path))
                for task in sequence["tasks"]:
                    prompt_path = str(task["prompt_path"])
                    verifier_path = str(task["verifier_command"])
                    if sequence.get("task_family_generation") == "baseline-v4":
                        prompt_path = prompt_path.replace("baseline-v4", "baseline-v3")
                        verifier_path = verifier_path.replace("baseline-v4", "baseline-v3")
                    paths.add(Path(prompt_path))
                    paths.add(Path(verifier_path))
            for protocol in audit["protocols"]:
                paths.add(Path(protocol["path"]))
            for item in index["receipts"]:
                receipt_rel = Path(item["path"])
                paths.add(receipt_rel)
                receipt = json.loads((ROOT / receipt_rel).read_text())
                paths.update(
                    Path(value)
                    for value in (
                        receipt["literal_command"]["log_path"],
                        receipt["controller_verifier"]["log_path"],
                        receipt["production_bootstrap"]["log_path"],
                    )
                )
            for relative in paths:
                destination = temp_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, destination)

            mutated_audit = copy.deepcopy(audit)
            mutated_audit["provider_accounting"]["provider_calls"] = False
            (temp_root / audit_rel).write_text(json.dumps(mutated_audit, indent=2) + "\n")
            errors: list[str] = []
            with mock.patch.object(validate_repository, "ROOT", temp_root):
                validate_repository.validate_baseline_v3_qualification_audit(errors)
            self.assertTrue(any("strict integer zero" in error for error in errors), errors)
            (temp_root / audit_rel).write_text(json.dumps(audit, indent=2) + "\n")

            numeric_paths: list[tuple[object, ...]] = []

            def collect_numeric_paths(value: object, path: tuple[object, ...] = ()) -> None:
                if isinstance(value, dict):
                    for key, child in value.items():
                        collect_numeric_paths(child, path + (key,))
                elif isinstance(value, list):
                    for index, child in enumerate(value):
                        collect_numeric_paths(child, path + (index,))
                elif type(value) is int:
                    numeric_paths.append(path)

            collect_numeric_paths(audit)
            for numeric_path in numeric_paths:
                for invalid_value in (False, True, 0.0, "0", None):
                    with self.subTest(
                        audit_numeric=".".join(map(str, numeric_path)),
                        invalid_value=repr(invalid_value),
                    ):
                        mutated_audit = copy.deepcopy(audit)
                        target: Any = mutated_audit
                        for key in numeric_path[:-1]:
                            target = target[key]
                        target[numeric_path[-1]] = invalid_value
                        (temp_root / audit_rel).write_text(json.dumps(mutated_audit, indent=2) + "\n")
                        errors = []
                        with mock.patch.object(validate_repository, "ROOT", temp_root):
                            validate_repository.validate_baseline_v3_qualification_audit(errors)
                        self.assertTrue(
                            any("numeric" in error or "strict non-boolean integer" in error for error in errors),
                            errors,
                        )
            (temp_root / audit_rel).write_text(json.dumps(audit, indent=2) + "\n")

            for sequence_index, sequence in enumerate(audit["sequences"]):
                for field in ("current_protocol_id", "current_protocol_path"):
                    with self.subTest(sequence=sequence["sequence_id"], stale_field=field):
                        mutated_audit = copy.deepcopy(audit)
                        mutated_audit["sequences"][sequence_index][field] = "bogus-current-protocol-binding"
                        (temp_root / audit_rel).write_text(json.dumps(mutated_audit, indent=2) + "\n")
                        errors = []
                        with mock.patch.object(validate_repository, "ROOT", temp_root):
                            validate_repository.validate_baseline_v3_qualification_audit(errors)
                        self.assertTrue(
                            any("per-sequence current protocol binding is stale" in error for error in errors),
                            errors,
                        )
            (temp_root / audit_rel).write_text(json.dumps(audit, indent=2) + "\n")

            for index_field in ("schema_version", "provider_calls", "provider_tokens", "receipt_count"):
                for invalid_value in (False, True, 0.0, "0", None):
                    with self.subTest(
                        receipt_index_field=index_field,
                        invalid_value=repr(invalid_value),
                    ):
                        mutated_index = copy.deepcopy(index)
                        mutated_index[index_field] = invalid_value
                        (temp_root / index_rel).write_text(json.dumps(mutated_index, indent=2) + "\n")
                        errors = []
                        with mock.patch.object(validate_repository, "ROOT", temp_root):
                            validate_repository.validate_baseline_v3_qualification_audit(errors)
                        self.assertTrue(any("receipt index" in error for error in errors), errors)
            (temp_root / index_rel).write_text(json.dumps(index, indent=2) + "\n")

            first_item = index["receipts"][0]
            receipt_rel = Path(first_item["path"])
            original_receipt = json.loads((temp_root / receipt_rel).read_text())
            mutations = (
                ("schema_version",),
                ("task_order",),
                ("provider_calls",),
                ("provider_tokens",),
                ("production_bootstrap", "exit_code"),
                ("literal_command", "exit_code"),
                ("controller_verifier", "exit_code"),
            )
            for keys in mutations:
                for invalid_value in (False, True, 0.0, "0", None):
                    with self.subTest(
                        receipt_field=".".join(keys),
                        invalid_value=repr(invalid_value),
                    ):
                        mutated_receipt = copy.deepcopy(original_receipt)
                        target = mutated_receipt
                        for key in keys[:-1]:
                            target = target[key]
                        target[keys[-1]] = invalid_value
                        receipt_bytes = (json.dumps(mutated_receipt, indent=2) + "\n").encode()
                        (temp_root / receipt_rel).write_bytes(receipt_bytes)
                        rehashed_index = copy.deepcopy(index)
                        rehashed_item = next(
                            item for item in rehashed_index["receipts"] if item["task_id"] == first_item["task_id"]
                        )
                        rehashed_item["sha256"] = hashlib.sha256(receipt_bytes).hexdigest()
                        (temp_root / index_rel).write_text(json.dumps(rehashed_index, indent=2) + "\n")
                        errors = []
                        with mock.patch.object(validate_repository, "ROOT", temp_root):
                            validate_repository.validate_baseline_v3_qualification_audit(errors)
                        self.assertTrue(
                            any(f"receipt is invalid for {first_item['task_id']}" in error for error in errors),
                            errors,
                        )

    def test_v3_qualification_numeric_evidence_rejects_non_integer_mutations(self) -> None:
        sequences = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
        original_load_json = validate_repository.load_json
        for sequence in sequences:
            qualification_rel = sequence["qualification_path"]
            qualification = json.loads((ROOT / qualification_rel).read_text())
            numeric_paths: list[tuple[object, ...]] = []

            def collect(value: object, path: tuple[object, ...] = ()) -> None:
                if isinstance(value, dict):
                    for key, child in value.items():
                        collect(child, path + (key,))
                elif isinstance(value, list):
                    for index, child in enumerate(value):
                        collect(child, path + (index,))
                elif type(value) is int:
                    numeric_paths.append(path)

            collect(qualification)
            for numeric_path in numeric_paths:
                for invalid_value in (False, True, 0.0, "0", None):
                    with self.subTest(
                        sequence=sequence["id"],
                        numeric_path=".".join(map(str, numeric_path)),
                        invalid_value=repr(invalid_value),
                    ):
                        mutated = copy.deepcopy(qualification)
                        target: Any = mutated
                        for key in numeric_path[:-1]:
                            target = target[key]
                        target[numeric_path[-1]] = invalid_value

                        def load_json(relative: str, mutated: dict[str, Any] = mutated) -> dict[str, Any]:
                            if relative == qualification_rel:
                                return mutated
                            return original_load_json(relative)

                        errors: list[str] = []
                        with mock.patch.object(validate_repository, "load_json", side_effect=load_json):
                            validate_repository.validate_qualification(sequence, errors)
                        self.assertTrue(
                            any("strict non-boolean integers" in error for error in errors),
                            errors,
                        )

    def test_retired_baseline_v2_authority_cannot_claim_future_execution(self) -> None:
        audit_rel = Path("sources/evaluations/audits/baseline-v2-task-family-qualification-20260721.json")
        pilot_rel = Path("sources/evaluations/audits/baseline-v2-pilot-zero-mistake.json")
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            for relative in (audit_rel, pilot_rel):
                destination = temp_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, destination)
            errors: list[str] = []
            with mock.patch.object(validate_repository, "ROOT", temp_root):
                validate_repository.validate_retired_baseline_v2_audit(errors)
            self.assertEqual(errors, [])

            audit = json.loads((temp_root / audit_rel).read_text())
            audit["decision"] = "Activate Baseline V2 for future execution"
            audit["supersession"]["rerun_allowed"] = True
            audit["treatment_gate"]["pilot_audit_present"] = False
            audit["protocols"] = [{"path": "missing-current-protocol.json"}]
            (temp_root / audit_rel).write_text(json.dumps(audit, indent=2) + "\n")
            errors = []
            with mock.patch.object(validate_repository, "ROOT", temp_root):
                validate_repository.validate_retired_baseline_v2_audit(errors)
            self.assertTrue(any("retired Baseline V2 qualification authority is stale" in error for error in errors), errors)

    def test_active_candidate_qualification_and_count_bindings_fail_closed(self) -> None:
        workflow_doc = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        fixtures_doc = json.loads((ROOT / "data/repository-fixtures.json").read_text())
        large_doc = json.loads((ROOT / "data/large-project-candidates.json").read_text())
        medium_doc = json.loads((ROOT / "data/medium-project-candidates.json").read_text())
        errors: list[str] = []
        validate_repository.validate_fixture_sequence_status_consistency(
            workflow_doc, fixtures_doc, large_doc, medium_doc, errors
        )
        self.assertEqual(errors, [])

        stale_medium = copy.deepcopy(medium_doc)
        stale_medium["candidates"][0]["qualification_evidence"] = "legacy-qualification.json"
        stale_medium["selection_policy"]["active_fixture_count"] = 1
        stale_medium["selection_policy"]["target_matrix"] = "One active Beets workflow; Fastify is retired."
        errors = []
        validate_repository.validate_fixture_sequence_status_consistency(
            workflow_doc, fixtures_doc, large_doc, stale_medium, errors
        )
        self.assertTrue(any("active qualification" in error for error in errors), errors)
        self.assertTrue(any("active_fixture_count" in error for error in errors), errors)
        self.assertTrue(any("target_matrix" in error for error in errors), errors)

    def test_nonzero_provider_lane_symlinked_artifact_ancestor_retains_checkout(self) -> None:
        for symlink_level in ("artifact-root", "ancestor"):
            with self.subTest(symlink_level=symlink_level), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                run_root = root / "matrix"
                sequence_id = "fastify-lifecycle-sequence-v0"
                profile_id = "baseline-bare-codex"
                lane_id = matrix.safe_name(f"{sequence_id}--{profile_id}")
                lane_dir = run_root / lane_id

                def prepare_checkout(_source: Path, checkout: Path) -> None:
                    (checkout / "data").mkdir(parents=True)
                    (checkout / "data/workflow-sessions.json").write_text('{"sessions": []}\n')
                    (checkout / matrix.WORKFLOW_ARTIFACT_ROOT).mkdir(parents=True)
                    (checkout / "protocol.json").write_text(json.dumps({
                        "protocol_id": "unit-protocol",
                        "baseline_pool": {"protocol_fingerprint": "unit-pool"},
                        "selected_execution": {},
                    }))

                def fail_with_symlinked_output(*_args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
                    checkout = Path(kwargs["cwd"])
                    artifact_root = checkout / matrix.WORKFLOW_ARTIFACT_ROOT
                    artifact_root.rmdir()
                    external = root / f"external-{symlink_level}"
                    external_artifacts = external / "workflow-sessions"
                    evidence = external_artifacts / "outside-session"
                    evidence.mkdir(parents=True)
                    (evidence / "run.json").write_text("{}\n")
                    if symlink_level == "artifact-root":
                        artifact_root.symlink_to(external_artifacts, target_is_directory=True)
                    else:
                        artifact_root.parent.rmdir()
                        artifact_root.parent.symlink_to(external, target_is_directory=True)
                    return subprocess.CompletedProcess(["unit-child"], 1)

                with (
                    mock.patch.object(matrix, "ROOT", root),
                    mock.patch.object(matrix, "clone_published_checkout", side_effect=lambda destination, _commit: prepare_checkout(root, destination)),
                    mock.patch.object(matrix, "find_protocol", side_effect=lambda checkout, *_: checkout / "protocol.json"),
                    mock.patch.object(matrix, "workflow_lane_command", return_value=["unit-child"]),
                    mock.patch.object(matrix.subprocess, "run", side_effect=fail_with_symlinked_output),
                ):
                    result = matrix.run_flow_lane(
                        sequence_id=sequence_id,
                        treatment_profile=profile_id,
                        lane_root=run_root,
                        replicate_index=0,
                        runner_args=[],
                        source_codex_home=None,
                        published_launch_commit="unit-published",
                    )
                self.assertEqual(result["failure_evidence"], [])
                self.assertFalse((lane_dir / "rejected-evidence/outside-session").exists())
                matrix.cleanup_lane_checkouts(run_root)
                self.assertTrue((lane_dir / "checkout").is_dir())
                self.assertTrue((lane_dir / matrix.LANE_CLEANUP_PROHIBITION_SENTINEL).is_file())
                matrix.CLEANUP_PROHIBITED_LANE_DIRS.discard(lane_dir.resolve())

    def test_symlinked_run_root_ancestor_is_rejected_before_preservation_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            external_run_root = temp / "external-run"
            external_run_root.mkdir()
            aliased_run_root = temp / "aliased-run"
            aliased_run_root.symlink_to(external_run_root, target_is_directory=True)
            lane_dir = aliased_run_root / "lane"
            checkout = lane_dir / "repo"
            source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "session-a"
            source.mkdir(parents=True)
            (source / "run.json").write_text("{}\n")
            matrix.CLEANUP_PROHIBITED_LANE_DIRS.add(lane_dir.resolve())
            result = {
                "lane_id": "lane",
                "lane_dir": str(lane_dir),
                "run_root": str(aliased_run_root),
                "failure_evidence": [],
            }
            with self.assertRaisesRegex(ValueError, "unsafe run root or lane ancestor"):
                matrix.preserve_discovered_lane_artifacts(
                    result=result,
                    checkout=checkout,
                    artifact_root=checkout / matrix.WORKFLOW_ARTIFACT_ROOT,
                    before_artifact_entries=set(),
                    reason="unit rejection",
                )
            self.assertFalse((external_run_root / matrix.PRESERVATION_FAILURE_SENTINEL).exists())
            self.assertFalse((external_run_root / "lane/rejected-evidence").exists())
            self.assertIn(lane_dir.resolve(), matrix.CLEANUP_PROHIBITED_LANE_DIRS)
            with self.assertRaisesRegex(ValueError, "lane root contains a symlink"):
                matrix.main(["--dry-run", "--lane-root", str(aliased_run_root)])
            matrix.CLEANUP_PROHIBITED_LANE_DIRS.discard(lane_dir.resolve())

    def test_symlinked_rejected_evidence_root_retains_source_without_external_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp) / "matrix"
            lane_dir = run_root / "lane"
            checkout = lane_dir / "repo"
            source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "session-a"
            source.mkdir(parents=True)
            (source / "run.json").write_text("{}\n")
            external = Path(tmp) / "external"
            external.mkdir()
            lane_dir.mkdir(parents=True, exist_ok=True)
            (lane_dir / "rejected-evidence").symlink_to(external, target_is_directory=True)
            matrix.retain_lane_checkout(lane_dir, "lane", "unit test")
            result = {"lane_id": "lane", "lane_dir": str(lane_dir), "failure_evidence": []}
            with self.assertRaisesRegex(ValueError, "unsafe rejected evidence destination root"):
                matrix.preserve_discovered_lane_artifacts(
                    result=result,
                    checkout=checkout,
                    artifact_root=checkout / matrix.WORKFLOW_ARTIFACT_ROOT,
                    before_artifact_entries=set(),
                    reason="unit rejection",
                )
            self.assertEqual(list(external.iterdir()), [])
            self.assertIn(lane_dir.resolve(), matrix.CLEANUP_PROHIBITED_LANE_DIRS)
            matrix.cleanup_lane_checkouts(run_root)
            self.assertTrue(lane_dir.exists())
            self.assertTrue((lane_dir / matrix.LANE_CLEANUP_PROHIBITION_SENTINEL).is_file())
            matrix.CLEANUP_PROHIBITED_LANE_DIRS.discard(lane_dir.resolve())

    def test_existing_rejected_evidence_destination_retains_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp) / "matrix"
            lane_dir = run_root / "lane"
            checkout = lane_dir / "checkout"
            source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "session-a"
            source.mkdir(parents=True)
            (source / "run.json").write_text("{}\n")
            (lane_dir / "rejected-evidence/session-a").mkdir(parents=True)
            matrix.retain_lane_checkout(lane_dir, "lane", "unit test")
            result = {"lane_id": "lane", "lane_dir": str(lane_dir), "failure_evidence": []}
            with self.assertRaises(FileExistsError):
                matrix.preserve_rejected_lane_artifacts(result, checkout, {"session-a"}, "unit rejection")
            matrix.cleanup_lane_checkouts(run_root)
            self.assertTrue(source.is_dir())
            self.assertEqual(result["failure_evidence"], [])
            matrix.CLEANUP_PROHIBITED_LANE_DIRS.discard(lane_dir.resolve())
            matrix.CLEANUP_PROHIBITED_RUN_ROOTS.discard(run_root.resolve())
            matrix.ACTIVE_RUN_PRESERVATIONS.pop(run_root.resolve(), None)

    def test_post_rename_fsync_failure_and_retry_retain_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp) / "matrix"
            lane_dir = run_root / "lane"
            checkout = lane_dir / "checkout"
            source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "session-a"
            source.mkdir(parents=True)
            (source / "run.json").write_text("{}\n")
            matrix.retain_lane_checkout(lane_dir, "lane", "unit test")
            result = {"lane_id": "lane", "lane_dir": str(lane_dir), "failure_evidence": []}
            failure_root = lane_dir / "rejected-evidence"
            real_fsync = matrix.fsync_directory
            failed = False

            def fail_after_rename(directory: Path) -> None:
                nonlocal failed
                if directory == failure_root and (failure_root / "session-a").exists() and not failed:
                    failed = True
                    raise OSError("unit post-rename fsync failure")
                real_fsync(directory)

            with mock.patch.object(matrix, "fsync_directory", side_effect=fail_after_rename):
                with self.assertRaisesRegex(OSError, "post-rename"):
                    matrix.preserve_rejected_lane_artifacts(result, checkout, {"session-a"}, "unit rejection")
            with self.assertRaises(FileExistsError):
                matrix.preserve_rejected_lane_artifacts(result, checkout, {"session-a"}, "unit retry")
            matrix.cleanup_lane_checkouts(run_root)
            self.assertTrue(source.is_dir())
            self.assertEqual(result["failure_evidence"], [])
            matrix.CLEANUP_PROHIBITED_LANE_DIRS.discard(lane_dir.resolve())
            matrix.CLEANUP_PROHIBITED_RUN_ROOTS.discard(run_root.resolve())
            matrix.ACTIVE_RUN_PRESERVATIONS.pop(run_root.resolve(), None)

    def test_parallel_rejected_evidence_preservation_is_reference_counted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp) / "matrix"
            calls: list[tuple[dict[str, Any], Path, set[str], str]] = []
            for index in range(2):
                lane_dir = run_root / f"lane-{index}"
                checkout = lane_dir / "checkout"
                session_id = f"session-{index}"
                source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / session_id
                source.mkdir(parents=True)
                (source / "run.json").write_text("{}\n")
                result = {"lane_id": f"lane-{index}", "lane_dir": str(lane_dir), "failure_evidence": []}
                calls.append((result, checkout, {session_id}, "unit parallel rejection"))
            barrier = threading.Barrier(2)
            real_copy = matrix.shutil.copy2

            def synchronized_copy(source: Path, destination: Path) -> Any:
                barrier.wait(timeout=5)
                return real_copy(source, destination)

            with (
                mock.patch.object(matrix.shutil, "copy2", side_effect=synchronized_copy),
                concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool,
            ):
                results = list(pool.map(lambda args: matrix.preserve_rejected_lane_artifacts(*args), calls))
            self.assertTrue(all(len(result) == 1 for result in results))
            self.assertNotIn(run_root.resolve(), matrix.CLEANUP_PROHIBITED_RUN_ROOTS)
            self.assertNotIn(run_root.resolve(), matrix.ACTIVE_RUN_PRESERVATIONS)
            self.assertFalse((run_root / matrix.PRESERVATION_FAILURE_SENTINEL).exists())

    def test_unsafe_rejected_evidence_shape_retains_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp) / "matrix-run"
            checkout = run_root / "lane" / "checkout"
            source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "oversized-shape"
            source.mkdir(parents=True)
            for index in range(33):
                (source / f"entry-{index:02d}.json").write_text("{}\n")
            result = {"lane_id": "lane", "lane_dir": str(run_root / "lane")}
            with self.assertRaises(ValueError):
                matrix.preserve_rejected_lane_artifacts(
                    result,
                    checkout,
                    {"oversized-shape"},
                    "strict compact artifact ingress rejected the session",
                )
            sentinel = json.loads((run_root / matrix.PRESERVATION_FAILURE_SENTINEL).read_text())
            self.assertEqual(sentinel["error_type"], "UnsafeRejectedEvidenceShape")
            matrix.cleanup_lane_checkouts(run_root)
            self.assertTrue(checkout.is_dir())

    def test_empty_directory_and_symlink_rejected_evidence_retain_checkout(self) -> None:
        for shape in ("missing", "empty", "nested-directory", "symlink-entry"):
            with self.subTest(shape=shape), tempfile.TemporaryDirectory() as tmp:
                run_root = Path(tmp) / "matrix-run"
                checkout = run_root / "lane" / "checkout"
                checkout.mkdir(parents=True)
                source = checkout / matrix.WORKFLOW_ARTIFACT_ROOT / "unsafe-shape"
                if shape != "missing":
                    source.mkdir(parents=True)
                if shape == "nested-directory":
                    (source / "unexpected").mkdir()
                elif shape == "symlink-entry":
                    target = source / "target.json"
                    target.write_text("{}\n")
                    (source / "link.json").symlink_to(target.name)
                result = {"lane_id": "lane", "lane_dir": str(run_root / "lane")}
                with self.assertRaises(ValueError):
                    matrix.preserve_rejected_lane_artifacts(
                        result,
                        checkout,
                        {"unsafe-shape"},
                        "strict compact artifact ingress rejected the session",
                    )
                matrix.cleanup_lane_checkouts(run_root)
                self.assertTrue(checkout.is_dir())

    def test_production_dependency_bootstrap_preserves_pinned_toolchain_path_and_lock_mode(self) -> None:
        captured: dict[str, Any] = {}

        def fake_run_backend(cmd: list[str], **kwargs: Any) -> Any:
            captured["cmd"] = cmd
            captured["env"] = kwargs["env"]
            return argparse.Namespace(returncode=0)

        sequence = {"fixture_id": "medium-beetbox-beets"}
        record = {"target": {"repository_path": "/tmp/provider-free-bootstrap-unit"}}
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(runner.fixture, "codex_env", return_value={"PATH": "/usr/bin"}), \
             mock.patch.object(runner.fixture, "container_mounts_for_record", return_value=[]), \
             mock.patch.object(runner.fixture, "run_backend", side_effect=fake_run_backend):
            code = runner.docker_setup_deps(
                sequence,
                record,
                Path(tmp) / "codex-home",
                Path(tmp),
                "token-eval-codex:latest",
            )
        self.assertEqual(code, 0)
        self.assertEqual(captured["cmd"], ["bash", "-c", "uv sync --group test --frozen"])
        self.assertTrue(captured["env"]["PATH"].startswith("/opt/data/bin:/opt/data/opt/go/bin:"))

    def test_runner_scrubs_ambient_git_object_store_environment(self) -> None:
        ambient = {name: f"unit-{name}" for name in runner.AMBIENT_GIT_OBJECT_ENV_VARS}
        with mock.patch.dict(os.environ, ambient, clear=False):
            runner.clear_ambient_git_object_environment()
            for name in runner.AMBIENT_GIT_OBJECT_ENV_VARS:
                self.assertNotIn(name, os.environ)

    def test_matrix_scrubs_hostile_git_environment_before_argument_processing(self) -> None:
        ambient = {name: f"hostile-{name}" for name in runner.AMBIENT_GIT_OBJECT_ENV_VARS}
        with mock.patch.dict(os.environ, ambient, clear=False), \
             mock.patch.object(matrix, "parse_args", side_effect=RuntimeError("stop after scrub")):
            with self.assertRaisesRegex(RuntimeError, "stop after scrub"):
                matrix.main([])
            for name in runner.AMBIENT_GIT_OBJECT_ENV_VARS:
                self.assertNotIn(name, os.environ)

    def test_lane_environment_never_forwards_ambient_git_plumbing(self) -> None:
        ambient = {name: f"hostile-{name}" for name in runner.AMBIENT_GIT_OBJECT_ENV_VARS}
        with mock.patch.dict(os.environ, ambient, clear=False):
            env = matrix.workflow_lane_environment(Path("/tmp/unit-lane"))
        for name in runner.AMBIENT_GIT_OBJECT_ENV_VARS:
            self.assertNotIn(name, env)
        self.assertEqual(env["TMPDIR"], "/tmp/unit-lane")

    def test_direct_current_replication_rejects_invalid_authority_before_lock(self) -> None:
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        args = argparse.Namespace(
            prepare_only=False,
            profile_id="baseline-bare-codex",
            sequence_id=sequence["id"],
            replicate_index=1,
        )
        with mock.patch.object(runner, "load_sequence", return_value=sequence), \
             mock.patch.object(runner, "load_current_baseline_replication_authority", side_effect=ValueError("invalid authorization, scope, budget, model, or policy")), \
             mock.patch.object(runner, "acquire_provider_production_lock") as acquire_lock, \
             mock.patch.object(runner, "_run_one_locked") as locked:
            with self.assertRaisesRegex(ValueError, "invalid authorization"):
                runner.run_one(args)
        acquire_lock.assert_not_called()
        locked.assert_not_called()

    def test_direct_current_replication_rejects_unpublished_checkout_before_lock(self) -> None:
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        args = argparse.Namespace(
            prepare_only=False,
            profile_id="baseline-bare-codex",
            sequence_id=sequence["id"],
            replicate_index=1,
        )
        with mock.patch.object(runner, "load_sequence", return_value=sequence), \
             mock.patch.object(runner, "require_zero_mistake_pilot_replicate"), \
             mock.patch.object(runner, "baseline_v2_pilot_run_gate", return_value=(True, "unit unoccupied")), \
             mock.patch.object(runner, "inherited_provider_production_lock_fd", return_value=None), \
             mock.patch.object(runner, "paid_launch_checkout_errors", return_value=["repository checkout is not clean"]), \
             mock.patch.object(runner, "acquire_provider_production_lock") as acquire_lock, \
             mock.patch.object(runner, "_run_one_locked") as locked:
            with self.assertRaisesRegex(ValueError, "paid launch checkout gate failed"):
                runner.run_one(args)
        acquire_lock.assert_not_called()
        locked.assert_not_called()

    def test_prelocked_standalone_cannot_bypass_published_checkout_gate(self) -> None:
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        args = argparse.Namespace(
            prepare_only=False,
            profile_id="baseline-bare-codex",
            sequence_id=sequence["id"],
            replicate_index=1,
        )
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(runner, "PRODUCTION_LOCK_PATH", Path(tmp) / ".production.lock"), \
             mock.patch.dict(os.environ, {}, clear=False):
            fd = runner.acquire_provider_production_lock()
            os.environ[runner.PRODUCTION_LOCK_FD_ENV] = str(fd)
            try:
                with mock.patch.object(runner, "load_sequence", return_value=sequence), \
                     mock.patch.object(runner, "require_zero_mistake_pilot_replicate"), \
                     mock.patch.object(runner, "baseline_v2_pilot_run_gate", return_value=(True, "unit unoccupied")), \
                     mock.patch.object(runner, "paid_launch_checkout_errors", return_value=["repository checkout is not clean"]), \
                     mock.patch.object(runner, "_run_one_locked") as locked:
                    with self.assertRaisesRegex(ValueError, "paid launch checkout gate failed"):
                        runner.run_one(args)
                locked.assert_not_called()
            finally:
                os.environ.pop(runner.PRODUCTION_LOCK_FD_ENV, None)
                os.close(fd)

    def test_unknown_baseline_generation_fails_closed_before_any_paid_boundary(self) -> None:
        sequence = copy.deepcopy(runner.load_sequence("beets-lifecycle-sequence-v0"))
        sequence["task_family_generation"] = "baseline-v5"
        allowed, reason = runner.baseline_v2_pilot_run_gate(sequence, ROOT, 3)
        self.assertFalse(allowed)
        self.assertIn("requires explicit authority", reason)
        args = argparse.Namespace(
            prepare_only=False,
            profile_id="baseline-bare-codex",
            sequence_id=sequence["id"],
            replicate_index=3,
        )
        with mock.patch.object(runner, "load_sequence", return_value=sequence), \
             mock.patch.object(runner, "require_zero_mistake_pilot_replicate"), \
             mock.patch.object(runner, "acquire_provider_production_lock") as acquire_lock, \
             mock.patch.object(runner, "_run_one_locked") as locked:
            with self.assertRaisesRegex(ValueError, "requires explicit authority"):
                runner.run_one(args)
        acquire_lock.assert_not_called()
        locked.assert_not_called()

    def test_direct_current_baseline_rejects_unauthorized_replicate_before_lock(self) -> None:
        sequence = next(
            item
            for item in json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
            if item.get("task_family_generation") == "baseline-v4"
        )
        args = argparse.Namespace(
            prepare_only=False,
            profile_id="baseline-bare-codex",
            sequence_id=sequence["id"],
            replicate_index=4,
        )
        with mock.patch.object(runner, "load_sequence", return_value=sequence), \
             mock.patch.object(runner, "acquire_provider_production_lock") as acquire_lock, \
             mock.patch.object(runner, "_run_one_locked") as locked:
            with self.assertRaisesRegex(ValueError, "not authorized"):
                runner.run_one(args)
        acquire_lock.assert_not_called()
        locked.assert_not_called()

    def test_matrix_current_baseline_rejects_unauthorized_replicate_before_lane_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lane_root = Path(tmp) / "lanes"
            with mock.patch.object(matrix, "controller_validation_python", return_value=sys.executable), \
                 mock.patch.object(matrix.workflow, "baseline_v2_pilot_run_gate", return_value=(True, "unit authorized")), \
                 mock.patch.object(matrix, "acquire_production_lock") as acquire_lock, \
                 mock.patch.object(matrix.workflow, "reserve_baseline_pilot_attempt") as reserve_attempt, \
                 mock.patch.object(matrix, "run_flow_lane") as run_lane:
                with self.assertRaisesRegex(ValueError, "not authorized"):
                    matrix.main([
                        "beets-lifecycle-sequence-v0",
                        "--replicate-index", "4",
                        "--lane-root", str(lane_root),
                    ])
            self.assertFalse(lane_root.exists())
            acquire_lock.assert_not_called()
            reserve_attempt.assert_not_called()
            run_lane.assert_not_called()

    def test_beets_r3_replacement_authority_scopes_one_immutable_identity(self) -> None:
        sequences = {
            item["id"]: item
            for item in json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
        }
        authority = runner.load_beets_r3_replacement_authority(ROOT)
        self.assertEqual(authority["authorized_by_owner_message_id"], "1531806010350633101")
        self.assertEqual(authority["authorized_replicate_indexes"], [3])
        self.assertEqual(authority["allowed_paid_baseline_runs"], 1)
        self.assertEqual(authority["allowed_model_turns"], 3)
        binding, receipt = runner.baseline_replication_binding(
            sequences["beets-lifecycle-sequence-v0"], 3, ROOT
        )
        self.assertEqual(binding["sequence_id"], "beets-lifecycle-sequence-v0")
        self.assertEqual(receipt.relative_to(ROOT).as_posix(), runner.BEETS_R3_REPLACEMENT_ATTEMPT_REL)
        allowed, reason = runner.baseline_v2_pilot_run_gate(
            sequences["beets-lifecycle-sequence-v0"], ROOT, 3
        )
        if receipt.exists():
            attempt = json.loads(receipt.read_text())
            self.assertEqual(attempt["sequence_id"], "beets-lifecycle-sequence-v0")
            self.assertEqual(attempt["replicate_index"], 3)
            self.assertTrue(attempt["immutable_identity_receipt"])
            self.assertFalse(allowed)
            self.assertIn("occupied", reason)
        else:
            self.assertTrue(allowed, reason)
        for sequence_id in ("fastify-lifecycle-sequence-v0", "terraform-lifecycle-sequence-v0"):
            with self.assertRaisesRegex(ValueError, "covers only"):
                runner.baseline_replication_binding(sequences[sequence_id], 3, ROOT)

    def test_strict_replication_authority_rejects_every_decision_field_mutation(self) -> None:
        source_authority = ROOT / runner.BASELINE_REPLICATION_AUTHORITY_REL
        source_sequences = ROOT / "data/workflow-task-sequences.json"
        original = json.loads(source_authority.read_text())
        mutations = {
            "serialization": lambda doc: doc.__setitem__("serialization_required", False),
            "run-budget": lambda doc: doc.__setitem__("allowed_paid_baseline_runs", 7),
            "turn-budget": lambda doc: doc.__setitem__("allowed_model_turns", 19),
            "model": lambda doc: doc.__setitem__("model_condition", {"id": "codex-openai-gpt-5-6-luna-xhigh", "model": "gpt-5.6-luna", "reasoning_effort": "xhigh"}),
            "first-valid": lambda doc: doc.__setitem__("first_valid_sample_policy", False),
            "rerun": lambda doc: doc.__setitem__("rerun_after_attempt_receipt", True),
            "provider-calls": lambda doc: doc.__setitem__("provider_calls", 1),
            "provider-tokens": lambda doc: doc.__setitem__("provider_tokens", 1),
            "sequence-order": lambda doc: doc.__setitem__("sequence_order", list(reversed(doc["sequence_order"]))),
            "indexes-true": lambda doc: doc.__setitem__("authorized_replicate_indexes", [True, 2]),
            "indexes-false": lambda doc: doc.__setitem__("authorized_replicate_indexes", [False, 2]),
            "indexes-float": lambda doc: doc.__setitem__("authorized_replicate_indexes", [1.0, 2]),
            "indexes-string": lambda doc: doc.__setitem__("authorized_replicate_indexes", ["1", 2]),
            "indexes-null": lambda doc: doc.__setitem__("authorized_replicate_indexes", [None, 2]),
            "extra-field": lambda doc: doc.__setitem__("unreviewed_override", True),
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authority_path = root / runner.BASELINE_REPLICATION_AUTHORITY_REL
            authority_path.parent.mkdir(parents=True)
            sequence_path = root / "data/workflow-task-sequences.json"
            sequence_path.parent.mkdir(parents=True)
            shutil.copy2(source_sequences, sequence_path)
            shutil.copytree(
                ROOT / "sources/evaluations/protocols",
                root / "sources/evaluations/protocols",
            )
            for label, mutate in mutations.items():
                with self.subTest(label=label):
                    changed = copy.deepcopy(original)
                    mutate(changed)
                    authority_path.write_text(json.dumps(changed, indent=2) + "\n")
                    with self.assertRaisesRegex(
                        ValueError,
                        "invalid authorization, scope, budget, model, or policy|stale nested binding",
                    ):
                        runner.load_current_baseline_replication_authority(root)

    def test_beets_r3_replacement_authority_rejects_scope_budget_and_binding_mutation(self) -> None:
        source_authority = ROOT / runner.BEETS_R3_REPLACEMENT_AUTHORITY_REL
        original = json.loads(source_authority.read_text())
        beets = runner.load_sequence("beets-lifecycle-sequence-v0")
        frozen_identity, frozen_protocol = runner.current_baseline_v2_protocol(
            beets, beets["mistake_gate"], ROOT
        )
        mutations = {
            "owner": lambda doc: doc.__setitem__("authorized_by_owner_message_id", "wrong"),
            "sequence": lambda doc: doc.__setitem__("sequence_order", ["fastify-lifecycle-sequence-v0"]),
            "index": lambda doc: doc.__setitem__("authorized_replicate_indexes", [2]),
            "index-bool": lambda doc: doc.__setitem__("authorized_replicate_indexes", [True]),
            "runs": lambda doc: doc.__setitem__("allowed_paid_baseline_runs", 2),
            "turns": lambda doc: doc.__setitem__("allowed_model_turns", 6),
            "serialization": lambda doc: doc.__setitem__("serialization_required", False),
            "rerun": lambda doc: doc.__setitem__("rerun_after_attempt_receipt", True),
            "provider": lambda doc: doc.__setitem__("provider_tokens", 1),
            "binding": lambda doc: doc["sequences"][0].__setitem__("protocol_sha256", "0" * 64),
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authority_path = root / runner.BEETS_R3_REPLACEMENT_AUTHORITY_REL
            authority_path.parent.mkdir(parents=True)
            sequence_path = root / "data/workflow-task-sequences.json"
            sequence_path.parent.mkdir(parents=True)
            shutil.copy2(ROOT / "data/workflow-task-sequences.json", sequence_path)
            shutil.copytree(
                ROOT / "sources/evaluations/protocols",
                root / "sources/evaluations/protocols",
            )
            for label, mutate in mutations.items():
                with self.subTest(label=label):
                    changed = copy.deepcopy(original)
                    mutate(changed)
                    authority_path.write_text(json.dumps(changed, indent=2) + "\n")
                    with mock.patch.object(
                        runner,
                        "current_baseline_v2_protocol",
                        return_value=(frozen_identity, frozen_protocol),
                    ), self.assertRaisesRegex(
                        ValueError,
                        "invalid authorization, scope, budget, model, or policy|stale nested binding",
                    ):
                        runner.load_beets_r3_replacement_authority(root)

    def test_real_matrix_paid_branch_rejects_mutated_authority_before_lane_root(self) -> None:
        probe_context = published_unoccupied_probe_worktree()
        probe = probe_context.__enter__()
        authority_path = probe / runner.BASELINE_REPLICATION_AUTHORITY_REL
        original_bytes = authority_path.read_bytes()
        original = json.loads(original_bytes)
        mutations = {
            "serialization_required": lambda doc: doc.__setitem__("serialization_required", False),
            "allowed_paid_baseline_runs": lambda doc: doc.__setitem__("allowed_paid_baseline_runs", 7),
            "allowed_model_turns": lambda doc: doc.__setitem__("allowed_model_turns", 19),
            "first_valid_sample_policy": lambda doc: doc.__setitem__("first_valid_sample_policy", False),
            "rerun_after_attempt_receipt": lambda doc: doc.__setitem__("rerun_after_attempt_receipt", True),
            "provider_calls": lambda doc: doc.__setitem__("provider_calls", 1),
            "provider_tokens": lambda doc: doc.__setitem__("provider_tokens", 1),
            "indexes_true": lambda doc: doc.__setitem__("authorized_replicate_indexes", [True, 2]),
            "indexes_false": lambda doc: doc.__setitem__("authorized_replicate_indexes", [False, 2]),
            "indexes_float": lambda doc: doc.__setitem__("authorized_replicate_indexes", [1.0, 2]),
            "indexes_string": lambda doc: doc.__setitem__("authorized_replicate_indexes", ["1", 2]),
            "indexes_null": lambda doc: doc.__setitem__("authorized_replicate_indexes", [None, 2]),
            "sibling_sequence": lambda doc: doc["sequences"][0].__setitem__("sequence_id", "wrong-sequence"),
            "sibling_generation": lambda doc: doc["sequences"][0].__setitem__("task_family_generation", "baseline-v999"),
            "sibling_protocol_path": lambda doc: doc["sequences"][0].__setitem__("protocol_path", "sources/evaluations/protocols/wrong.json"),
            "sibling_protocol_sha": lambda doc: doc["sequences"][0].__setitem__("protocol_sha256", "0" * 64),
            "sibling_pool": lambda doc: doc["sequences"][0].__setitem__("baseline_pool_fingerprint", "000000000000"),
        }
        try:
            for field, mutate in mutations.items():
                with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                    changed = copy.deepcopy(original)
                    mutate(changed)
                    authority_path.write_text(json.dumps(changed, indent=2) + "\n")
                    lane_root = Path(tmp) / "lanes"
                    result = subprocess.run(
                        [
                            sys.executable,
                            "scripts/run_sequential_workflow_matrix.py",
                            "beets-lifecycle-sequence-v0",
                            "--replicate-index", "1",
                            "--max-parallel", "1",
                            "--workflow-model-condition-id", "codex-openai-gpt-5-6-sol-high",
                            "--workflow-model", "gpt-5.6-sol",
                            "--workflow-reasoning-effort", "high",
                            "--lane-root", str(lane_root),
                            "--dry-run",
                        ],
                        cwd=probe,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertNotEqual(result.returncode, 0, field)
                    self.assertRegex(
                        result.stderr + result.stdout,
                        "invalid authorization, scope, budget, model, or policy|stale nested binding",
                    )
                    self.assertFalse(lane_root.exists())
        finally:
            authority_path.write_bytes(original_bytes)
            probe_context.__exit__(None, None, None)

    def test_matrix_rejects_unapproved_model_before_lane_root_or_receipt(self) -> None:
        with published_unoccupied_probe_worktree() as probe:
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_sequential_workflow_matrix.py",
                    "beets-lifecycle-sequence-v0",
                    "--replicate-index", "1",
                    "--max-parallel", "1",
                    "--workflow-model-condition-id", "codex-openai-gpt-5-6-luna-xhigh",
                    "--workflow-model", "gpt-5.6-luna",
                    "--workflow-reasoning-effort", "xhigh",
                    "--dry-run",
                ],
                cwd=probe,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("launch model does not match", result.stderr + result.stdout)

    def test_current_baseline_r1_r2_authority_binds_all_six_immutable_identities(self) -> None:
        sequences = {
            item["id"]: item
            for item in json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
        }
        self.assertEqual(
            set(sequences),
            {"fastify-lifecycle-sequence-v0", "beets-lifecycle-sequence-v0", "terraform-lifecycle-sequence-v0"},
        )
        receipts: set[Path] = set()
        for sequence in sequences.values():
            for replicate_index in (1, 2):
                binding, receipt = runner.baseline_replication_binding(sequence, replicate_index, ROOT)
                self.assertEqual(binding["sequence_id"], sequence["id"])
                gate_allowed, gate_reason = runner.baseline_v2_pilot_run_gate(sequence, ROOT, replicate_index)
                if receipt.exists():
                    attempt = json.loads(receipt.read_text())
                    self.assertEqual(attempt["sequence_id"], sequence["id"])
                    self.assertEqual(attempt["replicate_index"], replicate_index)
                    self.assertTrue(attempt["immutable_identity_receipt"])
                    self.assertEqual(attempt["attempt_status"], "reserved-before-provider-task")
                    self.assertFalse(gate_allowed)
                    self.assertIn("occupied", gate_reason)
                else:
                    self.assertTrue(gate_allowed, gate_reason)
                receipts.add(receipt)
            r3_allowed = runner.baseline_v2_pilot_run_gate(sequence, ROOT, 3)[0]
            if sequence["id"] == "beets-lifecycle-sequence-v0":
                _binding, r3_receipt = runner.baseline_replication_binding(sequence, 3, ROOT)
                self.assertEqual(r3_allowed, not r3_receipt.exists())
            else:
                self.assertFalse(r3_allowed)
            self.assertFalse(runner.baseline_v2_pilot_run_gate(sequence, ROOT, 4)[0])
        self.assertEqual(len(receipts), 6)

    def test_v4_canonical_protocol_identity_ignores_noncausal_provenance_hashes(self) -> None:
        sequences = {
            item["id"]: item
            for item in json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
        }
        sequence = sequences["beets-lifecycle-sequence-v0"]
        descriptor = runner.baseline_protocol_descriptor(sequence)
        execution = runner.execution_condition_descriptor(sequence, "baseline-bare-codex")
        mutated = copy.deepcopy(descriptor)
        for field in runner.NON_CAUSAL_PROTOCOL_PROVENANCE_FIELDS:
            mutated[field] = "f" * 64
        self.assertEqual(
            runner.canonical_protocol_id(
                sequence,
                "baseline-bare-codex",
                baseline_descriptor=descriptor,
                selected_execution=execution,
            ),
            runner.canonical_protocol_id(
                sequence,
                "baseline-bare-codex",
                baseline_descriptor=mutated,
                selected_execution=execution,
            ),
        )
        legacy = sequences["fastify-lifecycle-sequence-v0"]
        legacy_descriptor = runner.baseline_protocol_descriptor(legacy)
        legacy_mutated = copy.deepcopy(legacy_descriptor)
        legacy_mutated["validator_sha256"] = "f" * 64
        self.assertNotEqual(
            runner.canonical_protocol_id(
                legacy,
                "baseline-bare-codex",
                baseline_descriptor=legacy_descriptor,
            ),
            runner.canonical_protocol_id(
                legacy,
                "baseline-bare-codex",
                baseline_descriptor=legacy_mutated,
            ),
        )

    def test_v3_pilot_attempt_receipt_atomically_occupies_direct_and_matrix_gates(self) -> None:
        sequence = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"][0]
        with tempfile.TemporaryDirectory() as tmp:
            authority = Path(tmp)
            protocol = {
                "protocol_id": "unit-protocol",
                "baseline_pool": {"protocol_fingerprint": "unit-fingerprint"},
            }
            identity = {
                "protocol_id": "unit-protocol",
                "path": "sources/evaluations/protocols/unit-protocol.json",
                "sha256": "0" * 64,
                "qualification_sha256": "1" * 64,
            }
            with mock.patch.object(runner, "current_baseline_v2_protocol", return_value=(identity, protocol)):
                receipt = runner.reserve_baseline_pilot_attempt(
                    sequence,
                    root=authority,
                    orchestrator="unit-matrix",
                    replicate_index=0,
                )
                with self.assertRaises(FileExistsError):
                    runner.reserve_baseline_pilot_attempt(
                        sequence,
                        root=authority,
                        orchestrator="unit-direct",
                        replicate_index=0,
                    )
            receipt_path = runner.baseline_pilot_attempt_receipt_path(sequence, authority)
            self.assertEqual(json.loads(receipt_path.read_text()), receipt)
            self.assertIn(
                receipt_path.name,
                matrix.copytree_ignore(str(receipt_path.parent), [receipt_path.name]),
            )
            allowed, reason = runner.baseline_v2_pilot_run_gate(sequence, authority)
            self.assertFalse(allowed)
            self.assertIn("immutable attempt receipt", reason)
            with mock.patch.object(runner, "acquire_provider_production_lock", return_value=os.open(os.devnull, os.O_RDONLY)), \
                 mock.patch.object(runner, "load_sequence", return_value=sequence), \
                 mock.patch.object(runner, "baseline_v2_pilot_run_gate", return_value=(False, reason)), \
                 mock.patch.object(runner, "_run_one_locked") as locked:
                args = argparse.Namespace(
                    prepare_only=False,
                    profile_id="baseline-bare-codex",
                    sequence_id=sequence["id"],
                    replicate_index=0,
                )
                with mock.patch.object(runner, "ROOT", authority):
                    with self.assertRaises(ValueError):
                        runner.run_one(args)
                locked.assert_not_called()
            with self.assertRaises(ValueError):
                matrix.plan_workflow_jobs(
                    [sequence["id"]],
                    [],
                    baseline_state=lambda _sequence: "missing",
                    profile_state=lambda _sequence, _profile: "missing",
                    treatment_gate=lambda _sequence: (False, "blocked"),
                    baseline_run_gate=lambda _sequence: runner.baseline_v2_pilot_run_gate(sequence, authority),
                )

    def test_active_generation_gates_preserve_fastify_v3_and_current_v4_state(self) -> None:
        document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        authorization = json.loads(
            (ROOT / "sources/evaluations/audits/baseline-v4-task-family-qualification-20260722.json").read_text()
        )
        for sequence in document["sequences"]:
            passed, reason = runner.baseline_v2_treatment_gate(sequence, ROOT)
            rerun_allowed, rerun_reason = runner.baseline_v2_pilot_run_gate(sequence, ROOT)
            if sequence["id"] == "fastify-lifecycle-sequence-v0":
                self.assertTrue(passed, reason)
                self.assertIn("zero-incident", reason)
                self.assertFalse(rerun_allowed)
                self.assertIn("immutable attempt receipt", rerun_reason)
            else:
                receipt = runner.baseline_pilot_attempt_receipt_path(sequence, ROOT)
                if receipt.exists():
                    self.assertFalse(rerun_allowed, rerun_reason)
                    self.assertIn("immutable attempt receipt", rerun_reason)
                    if passed:
                        self.assertIn("zero-incident", reason)
                    else:
                        self.assertIn("exactly one entry", reason)
                elif authorization["paid_pilot_authorized"] is True:
                    self.assertFalse(passed)
                    self.assertIn("exactly one entry", reason)
                    self.assertTrue(rerun_allowed, rerun_reason)
                    self.assertIn("no prior Baseline V4 pilot attempt", rerun_reason)
                else:
                    self.assertFalse(passed)
                    self.assertFalse(rerun_allowed, rerun_reason)
                    self.assertIn("not authorized", rerun_reason)
        for slug in ("beets", "terraform"):
            self.assertTrue(
                (ROOT / f"sources/evaluations/audits/baseline-v3-pilot-attempt-{slug}.json").is_file(),
                f"missing immutable Baseline V3 receipt for {slug}",
            )

    def test_workflow_authority_describes_mixed_generations_and_completed_fastify_pilot(self) -> None:
        document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        self.assertIn("Baseline V3/V4", document["description"])
        sequences = {sequence["id"]: sequence for sequence in document["sequences"]}
        fastify = sequences["fastify-lifecycle-sequence-v0"]
        self.assertEqual(fastify["task_family_generation"], "baseline-v3")
        self.assertEqual(fastify["readiness_blockers"], [])
        self.assertEqual(fastify["mistake_gate"]["status"], "passed-zero-incident")
        self.assertNotIn("blocked until", fastify["mistake_gate"]["treatment_launch_policy"])
        self.assertEqual(runner.baseline_v2_treatment_gate(fastify, ROOT)[0], True)
        fixtures = {
            fixture["id"]: fixture
            for fixture in json.loads((ROOT / "data/repository-fixtures.json").read_text())["fixtures"]
        }
        fastify_fixture = fixtures["medium-fastify-fastify"]
        self.assertEqual(fastify_fixture["blockers"], [])
        self.assertEqual(fastify_fixture["current_task_family"]["provider_pilot_status"], "completed-passed-zero-incident")
        self.assertNotIn(
            "blocked-baseline-v3-pilot",
            {lane.get("status") for lane in fastify_fixture["future_evaluation_lanes"]},
        )
        for relative in (
            "docs/evaluations/design/token-and-quality-policy.md",
            "docs/evaluations/design/workflow-model.md",
            "docs/evaluations/operations/fixture-guide.md",
        ):
            text = (ROOT / relative).read_text()
            self.assertIn("active Baseline V3/V4", text, relative)
            self.assertNotIn("active Baseline V3 zero-mistake", text, relative)
        beets = sequences["beets-lifecycle-sequence-v0"]
        self.assertEqual(beets["readiness_blockers"], [])
        self.assertEqual(beets["mistake_gate"]["status"], "passed-zero-incident")
        self.assertTrue(runner.baseline_v2_treatment_gate(beets, ROOT)[0])
        terraform = sequences["terraform-lifecycle-sequence-v0"]
        self.assertEqual(terraform["readiness_blockers"], [])
        self.assertEqual(terraform["mistake_gate"]["status"], "passed-zero-incident")
        self.assertTrue(runner.baseline_v2_treatment_gate(terraform, ROOT)[0])

        stale_sequences = copy.deepcopy(document)
        for sequence in stale_sequences["sequences"]:
            if sequence.get("task_family_generation") == "baseline-v4":
                sequence["readiness_blockers"] = [
                    "provider-backed strongest-model zero-mistake Baseline V4 pilot is not authorized or executed"
                ]
        errors: list[str] = []
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            runner,
            "baseline_pilot_attempt_receipt_path",
            return_value=Path(tmp) / "unoccupied.json",
        ):
            validate_repository.validate_workflow_task_sequences(
                stale_sequences,
                json.loads((ROOT / "data/repository-fixtures.json").read_text()),
                errors,
            )
        self.assertTrue(
            any("authorized but not executed or independently audited" in error for error in errors),
            errors,
        )

    def test_v4_active_authorities_are_generation_consistent(self) -> None:
        sequences = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
        fixtures = {
            item["id"]: item
            for item in json.loads((ROOT / "data/repository-fixtures.json").read_text())["fixtures"]
        }
        for sequence in sequences:
            if sequence.get("task_family_generation") != "baseline-v4":
                continue
            serialized = json.dumps(sequence)
            self.assertNotIn("Baseline V3 pilot not yet executed", serialized)
            self.assertNotIn("zero-mistake Baseline V3 pilot not yet executed", serialized)
            self.assertIn("Baseline V4", sequence["conversion_note"])
            self.assertIn("Baseline V3", sequence["conversion_note"])
            fixture = fixtures[sequence["fixture_id"]]
            self.assertEqual(fixture["current_task_family"]["generation"], "baseline-v4")
            self.assertIn("/baseline-v4/", fixture["prompt"]["path"])
            self.assertIn("Baseline V4", fixture["prompt"]["prompt_policy"])
            task_root = (ROOT / fixture["prompt"]["path"]).parents[2] / "tasks"
            for task in sequence["tasks"]:
                task_doc = task_root / task["id"] / "task.md"
                task_text = task_doc.read_text()
                self.assertIn("task-generations/baseline-v4/", task_text, str(task_doc))
                self.assertNotIn("task-generations/baseline-v3/", task_text, str(task_doc))
            blocked = [
                lane["status"]
                for lane in fixture["future_evaluation_lanes"]
                if lane.get("status", "").startswith("blocked-baseline-")
            ]
            treatment_ready, _reason = runner.baseline_v2_treatment_gate(sequence, ROOT)
            if treatment_ready:
                self.assertEqual(blocked, [])
            else:
                self.assertTrue(blocked)
                self.assertEqual(set(blocked), {"blocked-baseline-v4-pilot"})
        for path in (
            ROOT / "sources/evaluations/fixtures/medium/beetbox-beets/task-generations/baseline-v2/README.md",
            ROOT / "sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/baseline-v2/README.md",
        ):
            self.assertNotIn("Active tasks now live under `../baseline-v3/`", path.read_text())
        for path in (
            ROOT / "sources/evaluations/fixtures/medium/beetbox-beets/task-generations/baseline-v4/README.md",
            ROOT / "sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/baseline-v4/README.md",
        ):
            text = path.read_text()
            self.assertNotIn("prompts, seed states", text)
            self.assertIn("prompts differ", text)
            self.assertNotIn("currently unoccupied", text)
            self.assertNotIn("remain blocked until a fresh", text)
            self.assertIn("occupied pilot must never be rerun", text)
            self.assertIn("Treatment protocol freezing is now eligible", text)
            self.assertIn("only by the generation label", text)
            self.assertIn("command blocks", text)

    def test_v4_authorization_paths_are_repository_contained(self) -> None:
        sequence_doc = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        fixture_doc = json.loads((ROOT / "data/repository-fixtures.json").read_text())
        mismatched_fixtures = copy.deepcopy(fixture_doc)
        for fixture in mismatched_fixtures["fixtures"]:
            if fixture["id"] in {"medium-beetbox-beets", "large-hashicorp-terraform"}:
                fixture["current_task_family"]["generation"] = "baseline-v3"
        errors: list[str] = []
        validate_repository.validate_workflow_task_sequences(sequence_doc, mismatched_fixtures, errors)
        self.assertTrue(any("current_task_family generation" in error for error in errors), errors)
        for sequence in sequence_doc["sequences"]:
            if sequence.get("task_family_generation") == "baseline-v4":
                sequence["mistake_gate"]["pilot_authorization_path"] = "../external-authorization.json"
        errors = []
        validate_repository.validate_workflow_task_sequences(sequence_doc, fixture_doc, errors)
        self.assertTrue(any("pilot_authorization_path" in error and "authority root" in error for error in errors), errors)

    def test_v4_empirical_docs_do_not_claim_unretained_dry_run_results(self) -> None:
        for relative in (
            "README.md",
            "docs/evaluations/README.md",
            "docs/research/roadmap.md",
            "docs/truthmark/engineering/research/current-findings.md",
        ):
            text = (ROOT / relative).read_text().lower()
            self.assertNotIn("dry-run pass", text, relative)
            self.assertNotIn("dry-run matrices pass", text, relative)

    def test_v4_qualification_audit_is_provider_free_and_current(self) -> None:
        errors: list[str] = []
        validate_repository.validate_baseline_v4_qualification_audit(errors)
        self.assertEqual(errors, [])
        audit = json.loads(
            (ROOT / "sources/evaluations/audits/baseline-v4-task-family-qualification-20260722.json").read_text()
        )
        self.assertIs(type(audit["provider_calls"]), int)
        self.assertIs(type(audit["provider_tokens"]), int)
        self.assertEqual((audit["provider_calls"], audit["provider_tokens"]), (0, 0))
        self.assertIs(audit["paid_pilot_authorized"], True)
        active_v4 = [
            sequence
            for sequence in json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
            if sequence.get("task_family_generation") == "baseline-v4"
        ]
        self.assertIs(
            audit["treatment_unlocked"],
            all(runner.baseline_v2_treatment_gate(sequence, ROOT)[0] for sequence in active_v4),
        )
        for record in audit["sequences"]:
            qualification = json.loads((ROOT / record["qualification_path"]).read_text())
            protocol = json.loads((ROOT / record["protocol_path"]).read_text())
            self.assertEqual(qualification["task_family_generation"], "baseline-v4")
            self.assertEqual(protocol["task_fixture"]["task_family_generation"], "baseline-v4")
            self.assertEqual(protocol["baseline_pool"]["descriptor"]["task_family_generation"], "baseline-v4")

    def test_v4_evidence_identity_validation_rejects_duplicates_and_malformed_prepare_evidence(self) -> None:
        audit = json.loads(
            (ROOT / "sources/evaluations/audits/baseline-v4-task-family-qualification-20260722.json").read_text()
        )
        index = json.loads((ROOT / audit["literal_command_receipt_index"]).read_text())
        receipt_documents = {
            item["path"]: json.loads((ROOT / item["path"]).read_text())
            for item in index["receipts"]
        }
        prepare_manifest = json.loads((ROOT / audit["prepare_only_manifest"]).read_text())
        prepare_files = {
            name: (ROOT / audit["prepare_only_manifest"]).parent.joinpath(name).read_bytes()
            for name in prepare_manifest["files"]
        }
        expected_sequences = {
            item["id"]: item
            for item in json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
            if item.get("status") == "active" and item.get("task_family_generation") == "baseline-v4"
        }

        def validate(candidate_audit, candidate_index, candidate_manifest, candidate_files=None) -> list[str]:
            errors: list[str] = []
            validate_repository.validate_baseline_v4_evidence_identity(
                candidate_audit,
                candidate_index,
                receipt_documents,
                candidate_manifest,
                prepare_files if candidate_files is None else candidate_files,
                expected_sequences,
                errors,
            )
            return errors

        self.assertEqual(validate(audit, index, prepare_manifest), [])

        def retired_migration_authority(previous_bindings: dict[str, dict[str, str]]) -> dict:
            candidate = copy.deepcopy(audit)
            candidate["prepare_only_refresh_pending"] = {
                "reason": "controller replicate-index binding changed without changing baseline pool fingerprints",
                "provider_calls": 0,
                "provider_tokens": 0,
                "previous_protocol_bindings": previous_bindings,
            }
            return candidate

        def encoded_prepare_evidence(candidate_plan: dict, candidate_summary: dict) -> tuple[dict, dict[str, bytes]]:
            candidate_files = {
                "plan.json": (json.dumps(candidate_plan, indent=2) + "\n").encode(),
                "matrix-summary.json": (json.dumps(candidate_summary, indent=2) + "\n").encode(),
            }
            candidate_manifest = copy.deepcopy(prepare_manifest)
            candidate_manifest["files"] = {
                name: hashlib.sha256(content).hexdigest()
                for name, content in candidate_files.items()
            }
            return candidate_manifest, candidate_files

        invented_bindings = {}
        for record in audit["sequences"]:
            sequence_id = record["sequence_id"]
            invented_id = f"{sequence_id}-baseline-bare-codex-invented000000"
            invented_bindings[sequence_id] = {
                "protocol_id": invented_id,
                "path": f"sources/evaluations/protocols/{invented_id}.json",
                "sha256": "0" * 64,
                "baseline_pool_fingerprint": record["baseline_pool_fingerprint"],
            }
        invented_audit = retired_migration_authority(invented_bindings)
        invented_plan = json.loads(prepare_files["plan.json"])
        invented_summary = json.loads(prepare_files["matrix-summary.json"])
        for job in invented_plan["jobs"]:
            job["protocol"] = invented_bindings[job["sequence_id"]]["path"]
        invented_summary["plan"] = invented_plan
        for lane in invented_summary["lane_results"]:
            binding = invented_bindings[lane["sequence_id"]]
            lane["expected_session_binding"]["frozen_protocol"] = {
                "protocol_id": binding["protocol_id"],
                "path": binding["path"],
                "sha256": binding["sha256"],
            }
        invented_manifest, invented_files = encoded_prepare_evidence(invented_plan, invented_summary)
        invented_errors = validate(invented_audit, index, invented_manifest, invented_files)
        self.assertTrue(any("prepare plan" in error for error in invented_errors), invented_errors)
        self.assertTrue(any("prepare lane identity" in error for error in invented_errors), invented_errors)

        current_bindings = {
            record["sequence_id"]: {
                "protocol_id": record["protocol_id"],
                "path": record["protocol_path"],
                "sha256": record["protocol_sha256"],
                "baseline_pool_fingerprint": record["baseline_pool_fingerprint"],
            }
            for record in audit["sequences"]
        }
        prompt_audit = retired_migration_authority(current_bindings)
        prompt_plan = json.loads(prepare_files["plan.json"])
        prompt_summary = json.loads(prepare_files["matrix-summary.json"])
        selected_execution = prompt_summary["lane_results"][0]["expected_session_binding"]["selected_execution"]
        selected_execution["descriptor"]["model_facing_prompts"]["tasks"][0]["rendered_prompt_sha256"] = "0" * 64
        selected_execution["descriptor_sha256"] = validate_repository.canonical_json_hash(selected_execution["descriptor"])
        prompt_manifest, prompt_files = encoded_prepare_evidence(prompt_plan, prompt_summary)
        prompt_errors = validate(prompt_audit, index, prompt_manifest, prompt_files)
        self.assertTrue(any("prepare lane identity" in error for error in prompt_errors), prompt_errors)

        tampered = copy.deepcopy(audit)
        tampered["sequences"][0]["task_count"] = False
        self.assertTrue(validate(tampered, index, prepare_manifest))
        tampered = copy.deepcopy(audit)
        tampered["sequences"] = [tampered["sequences"][0], copy.deepcopy(tampered["sequences"][0])]
        self.assertTrue(validate(tampered, index, prepare_manifest))
        tampered = copy.deepcopy(audit)
        tampered["sequences"][0]["literal_command_receipts"][0]["path"] = "wrong.receipt.json"
        self.assertTrue(validate(tampered, index, prepare_manifest))
        tampered_index = copy.deepcopy(index)
        tampered_index["receipts"] = [copy.deepcopy(index["receipts"][0]) for _ in range(6)]
        self.assertTrue(validate(audit, tampered_index, prepare_manifest))
        tampered_manifest = copy.deepcopy(prepare_manifest)
        tampered_manifest["provider_calls"] = False
        self.assertTrue(validate(audit, index, tampered_manifest))
        tampered_manifest = copy.deepcopy(prepare_manifest)
        tampered_manifest["files"]["plan.json"] = "0" * 64
        self.assertTrue(validate(audit, index, tampered_manifest))
        tampered_files = dict(prepare_files)
        tampered_plan = json.loads(tampered_files["plan.json"])
        tampered_plan["jobs"][0]["profile_id"] = "not-baseline"
        tampered_files["plan.json"] = (json.dumps(tampered_plan, indent=2) + "\n").encode()
        tampered_summary = json.loads(tampered_files["matrix-summary.json"])
        tampered_summary["plan"] = tampered_plan
        tampered_files["matrix-summary.json"] = (json.dumps(tampered_summary, indent=2) + "\n").encode()
        tampered_manifest = copy.deepcopy(prepare_manifest)
        tampered_manifest["files"] = {
            name: hashlib.sha256(content).hexdigest()
            for name, content in tampered_files.items()
        }
        self.assertTrue(validate(audit, index, tampered_manifest, tampered_files))

        def validate_mutated_summary(mutator) -> list[str]:
            candidate_files = dict(prepare_files)
            summary = json.loads(candidate_files["matrix-summary.json"])
            mutator(summary)
            candidate_files["matrix-summary.json"] = (json.dumps(summary, indent=2) + "\n").encode()
            candidate_manifest = copy.deepcopy(prepare_manifest)
            candidate_manifest["files"] = {
                name: hashlib.sha256(content).hexdigest()
                for name, content in candidate_files.items()
            }
            return validate(audit, index, candidate_manifest, candidate_files)

        self.assertTrue(validate_mutated_summary(lambda summary: summary["lane_results"][0].__setitem__("treatment_profile", "not-baseline")))
        self.assertTrue(validate_mutated_summary(lambda summary: summary["lane_results"][0]["expected_session_binding"]["selected_execution"].__setitem__("descriptor_sha256", "0" * 64)))
        self.assertTrue(validate_mutated_summary(lambda summary: summary["validation"]["results"][0].__setitem__("command", ["provider-capable-placeholder"])))
        tampered_manifest = copy.deepcopy(prepare_manifest)
        tampered_manifest["lane_exit_codes"].pop(next(iter(tampered_manifest["lane_exit_codes"])))
        self.assertTrue(validate(audit, index, tampered_manifest))

    def test_v4_pilot_requires_explicit_authorization_authority(self) -> None:
        sequence = {
            "id": "beets-lifecycle-sequence-v0",
            "task_family_generation": "baseline-v4",
            "mistake_gate": {
                "pilot_audit_path": "sources/evaluations/audits/baseline-v4-pilot-zero-mistake.json",
                "attempt_receipt_path": "sources/evaluations/audits/baseline-v4-pilot-attempt-beets.json",
                "pilot_authorization_path": "sources/evaluations/audits/baseline-v4-task-family-qualification-20260722.json",
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            authority = Path(tmp)
            auth_path = authority / sequence["mistake_gate"]["pilot_authorization_path"]
            auth_path.parent.mkdir(parents=True)
            auth_path.write_text(json.dumps({"schema_version": 1, "generation": "baseline-v4", "paid_pilot_authorized": False}))
            allowed, reason = runner.baseline_v2_pilot_run_gate(sequence, authority)
            self.assertFalse(allowed)
            self.assertIn("not authorized", reason)
            for malformed in (True,):
                authorization = json.loads(auth_path.read_text())
                authorization["paid_pilot_authorized"] = malformed
                auth_path.write_text(json.dumps(authorization))
                allowed, reason = runner.baseline_v2_pilot_run_gate(sequence, authority)
                self.assertTrue(allowed, reason)
            original_authorization_path = sequence["mistake_gate"]["pilot_authorization_path"]
            external_authority = authority.parent / f"{authority.name}-external-authorization.json"
            external_authority.write_text(json.dumps({"schema_version": 1, "generation": "baseline-v4", "paid_pilot_authorized": True}))
            self.addCleanup(external_authority.unlink, missing_ok=True)
            lexical_traversal = str(Path(original_authorization_path).parent / ".." / "audits" / Path(original_authorization_path).name)
            for escaped in (
                str(auth_path),
                lexical_traversal,
                str(external_authority),
                f"../{external_authority.name}",
            ):
                sequence["mistake_gate"]["pilot_authorization_path"] = escaped
                allowed, reason = runner.baseline_v2_pilot_run_gate(sequence, authority)
                self.assertFalse(allowed)
                self.assertIn("repository-relative path without traversal", reason)
            sequence["mistake_gate"]["pilot_authorization_path"] = original_authorization_path
            treatment_allowed, treatment_reason = runner.baseline_v2_treatment_gate(sequence, authority)
            self.assertFalse(treatment_allowed)
            self.assertIn("pilot audit is absent", treatment_reason)

    def test_failed_v2_pilot_preserves_exact_executed_protocol_bytes(self) -> None:
        audit = json.loads(
            (ROOT / "sources/evaluations/audits/baseline-v2-pilot-zero-mistake.json").read_text()
        )
        evidence_root = ROOT / "sources/evaluations/audits/baseline-v2-pilot-20260722-failed"
        for sequence in audit["sequences"]:
            executed = sequence["executed_protocol"]
            preserved_path = ROOT / executed["path"]
            preserved_bytes = preserved_path.read_bytes()
            self.assertEqual(hashlib.sha256(preserved_bytes).hexdigest(), executed["sha256"])
            source_path = f"sources/evaluations/protocols/{executed['protocol_id']}.json"
            self.assertRegex(audit["source_commit"], r"^[0-9a-f]{40}$")
            self.assertFalse((ROOT / source_path).exists())
            protocol = json.loads(preserved_bytes)
            self.assertEqual(protocol["protocol_id"], executed["protocol_id"])
            lane_log = json.loads(
                next(evidence_root.glob(f"{sequence['sequence_id']}--*-lane.log")).read_text()
            )
            self.assertEqual(lane_log["frozen_protocol"]["protocol_id"], executed["protocol_id"])
            self.assertEqual(lane_log["frozen_protocol"]["sha256"], executed["sha256"])

    def test_current_fastify_v3_frozen_protocol_accepts_only_noncausal_provenance_drift(self) -> None:
        script = r'''
import argparse
import copy
import sys
sys.path.insert(0, 'scripts')
import run_codex_workflow_model_condition as condition
condition.configure_model_condition('codex-openai-gpt-5-6-sol-high', 'gpt-5.6-sol', 'high')
runner = condition.runner
sequence = runner.load_sequence('fastify-lifecycle-sequence-v0')
identity, protocol = runner.current_baseline_v2_protocol(sequence, sequence['mistake_gate'], runner.ROOT)
args = argparse.Namespace(
    prepare_only=True,
    protocol=identity['path'],
    timeout_per_task=3600,
    docker_image=runner.DEFAULT_DOCKER_IMAGE,
)
assert runner.validate_protocol_for_run(sequence, 'baseline-bare-codex', args) == protocol
mutated = copy.deepcopy(protocol)
mutated['baseline_pool']['descriptor']['objective'] += ' causal drift'
assert not runner.baseline_protocol_descriptor_compatible(
    mutated['baseline_pool']['descriptor'],
    runner.baseline_protocol_descriptor(sequence),
)
'''
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_current_v3_pilot_protocol_identity_is_unique_and_exact(self) -> None:
        script = """
import json
import sys
sys.path.insert(0, 'scripts')
import run_codex_workflow_evaluation as runner
import run_codex_workflow_model_condition as condition
condition.configure_model_condition('codex-openai-gpt-5-6-sol-high', 'gpt-5.6-sol', 'high')
document = json.loads((runner.ROOT / 'data/workflow-task-sequences.json').read_text())
for sequence in document['sequences']:
    identity, protocol = runner.current_baseline_v2_protocol(sequence, sequence['mistake_gate'], runner.ROOT)
    assert identity['protocol_id'] == protocol['protocol_id']
    assert identity['path'].endswith(identity['protocol_id'] + '.json')
    assert identity['qualification_sha256'] == protocol['task_fixture']['qualification_sha256']
    for isolation in (protocol['baseline_pool']['descriptor']['isolation'], protocol['selected_execution']['descriptor']['isolation']):
        assert 'verifier_assets_model_visible' not in isolation
        assert isolation['controller_verifier_scripts_and_canonical_copies_model_visible'] is False
        assert isolation['model_visible_acceptance_asset_paths'] == runner.sequence_model_visible_acceptance_paths(sequence)
print(len(document['sequences']))
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "3")

    def test_direct_v2_run_rejects_arbitrarily_renamed_protocol_before_setup(self) -> None:
        code = r'''import argparse, copy, json, tempfile
from pathlib import Path
from scripts import run_codex_workflow_evaluation as runner
from scripts import run_codex_workflow_model_condition as launcher
launcher.configure_model_condition('codex-openai-gpt-5-6-sol-high', 'gpt-5.6-sol', 'high')
sequence = runner.load_sequence('fastify-lifecycle-sequence-v0')
identity, protocol = runner.current_baseline_v2_protocol(sequence, sequence['mistake_gate'], runner.ROOT)
with tempfile.TemporaryDirectory(dir=runner.ROOT / 'sources/evaluations/protocols') as temp:
    fake_path = Path(temp) / 'arbitrarily-renamed-protocol.json'
    fake = copy.deepcopy(protocol)
    fake['protocol_id'] = 'arbitrarily-renamed-protocol'
    original_rel = identity['path']
    fake_rel = str(fake_path.relative_to(runner.ROOT))
    fake['baseline']['command'] = fake['baseline']['command'].replace(original_rel, fake_rel)
    fake_path.write_text(json.dumps(fake))
    args = argparse.Namespace(
        prepare_only=True,
        protocol=fake_rel,
        timeout_per_task=3600,
        docker_image=runner.DEFAULT_DOCKER_IMAGE,
    )
    try:
        runner.validate_protocol_for_run(sequence, 'baseline-bare-codex', args)
    except ValueError as exc:
        assert 'canonical_protocol_identity' in str(exc) or 'does not match run inputs' in str(exc), exc
    else:
        raise AssertionError('arbitrarily renamed Baseline V3 protocol was accepted')
'''
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_current_v2_protocol_rejects_arbitrarily_renamed_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sequence = {
                "id": "unit-sequence-v0",
                "fixture_id": "unit-fixture",
                "initial_snapshot": {"commit": "unit-snapshot"},
                "qualification_path": "qualification.json",
            }
            gate = {
                "designated_model_condition": "unit-condition",
                "model": "unit-model",
                "reasoning_effort": "high",
            }
            (root / "qualification.json").write_text("{}\n")
            expected_descriptor = {"contract": "current"}
            expected_execution = {"execution": "current"}
            expected_protocol_id = "unit-sequence-v0-baseline-bare-codex-canonical"
            document = {
                "protocol_schema_version": 3,
                "status": "frozen-ready-not-run",
                "protocol_id": "unit-sequence-v0-baseline-bare-codex-arbitrary",
                "task_fixture": {
                    "sequence_id": sequence["id"],
                    "fixture_id": sequence["fixture_id"],
                    "snapshot": "unit-snapshot",
                    "qualification_path": "qualification.json",
                    "qualification_sha256": hashlib.sha256((root / "qualification.json").read_bytes()).hexdigest(),
                },
                "baseline": {
                    "profile_id": "baseline-bare-codex",
                    "model_condition_id": "unit-condition",
                    "model": "unit-model",
                    "reasoning_effort": "high",
                },
                "treatment": {},
                "baseline_pool": {"protocol_fingerprint": "unit-pool", "descriptor": expected_descriptor},
                "selected_execution": {
                    "descriptor": expected_execution,
                    "descriptor_sha256": runner._json_hash(expected_execution),
                },
            }
            protocol_dir = root / "sources/evaluations/protocols"
            protocol_dir.mkdir(parents=True)
            arbitrary_path = protocol_dir / f"{document['protocol_id']}.json"
            arbitrary_path.write_text(json.dumps(document))
            with (
                mock.patch.object(runner, "condition_bound_protocol_descriptors", return_value=(expected_descriptor, expected_execution)),
                mock.patch.object(runner, "baseline_protocol_fingerprint_from_descriptor", return_value="unit-pool"),
                mock.patch.object(runner, "canonical_protocol_id", return_value=expected_protocol_id),
            ):
                with self.assertRaisesRegex(ValueError, "found 0"):
                    runner.current_baseline_v2_protocol(sequence, gate, root)
                document["protocol_id"] = expected_protocol_id
                (protocol_dir / f"{expected_protocol_id}.json").write_text(json.dumps(document))
                identity, _ = runner.current_baseline_v2_protocol(sequence, gate, root)
                self.assertEqual(identity["protocol_id"], expected_protocol_id)

        sequence = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"][0]
        self.assertEqual(
            contract_refresh.protocol_id(sequence, "baseline-bare-codex"),
            runner.canonical_protocol_id(sequence, "baseline-bare-codex"),
        )

    def test_pilot_session_artifact_bundle_is_manifest_verified_and_session_bound(self) -> None:
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        session = next(
            item
            for item in reversed(registry["sessions"])
            if item.get("session_role") == "baseline"
            and item.get("artifacts", {}).get("artifact_contract") == "compact-v1-four-files"
            and (ROOT / item.get("artifacts", {}).get("run_record", "missing")).is_file()
        )
        source = (ROOT / session["artifacts"]["run_record"]).parent
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            bundle = temp_root / "sources/evaluations/workflow-sessions" / session["session_id"]
            bundle.parent.mkdir(parents=True)
            shutil.copytree(source, bundle)
            candidate = copy.deepcopy(session)
            candidate["cumulative_token_usage"]["cache_write_tokens"] = 0
            candidate["artifacts"]["root"] = (
                f"sources/evaluations/workflow-sessions/{session['session_id']}"
            )
            for key, name in {
                "run_record": "run.json",
                "final_diff": "changes.diff",
                "evidence_bundle": "evidence.jsonl.gz",
                "manifest": "manifest.sha256",
            }.items():
                candidate["artifacts"][key] = (
                    f"sources/evaluations/workflow-sessions/{session['session_id']}/{name}"
                )
            def rewrite_manifest() -> None:
                manifest_lines = [
                    f"{hashlib.sha256((bundle / name).read_bytes()).hexdigest()}  {name}"
                    for name in ("run.json", "changes.diff", "evidence.jsonl.gz")
                ]
                (bundle / "manifest.sha256").write_text("\n".join(manifest_lines) + "\n")

            def normalize_bundle() -> None:
                run_record = json.loads((bundle / "run.json").read_text())
                run_record["token_usage"] = {
                    key: candidate["cumulative_token_usage"].get(key)
                    for key in ("measurement_source", *runner.PILOT_PROVIDER_USAGE_FIELDS)
                }
                run_record["agent_condition"] = {
                    key: candidate["agent"].get(key)
                    for key in ("runtime_id", "provider", "model", "model_condition_id", "reasoning_effort")
                }
                run_record["session_id"] = candidate["session_id"]
                run_record["replicate_index"] = candidate["replicate_index"]
                run_record["workflow_sequence_id"] = candidate["task_sequence"]["sequence_id"]
                run_record["profile_id"] = candidate["profile"]["profile_id"]
                run_record["selected_execution"] = candidate["selected_execution"]
                (bundle / "run.json").write_text(json.dumps(run_record, indent=2) + "\n")
                rewrite_manifest()

            def restore_bundle() -> None:
                shutil.rmtree(bundle)
                shutil.copytree(source, bundle)
                normalize_bundle()

            normalize_bundle()
            self.assertTrue(runner.pilot_session_artifacts_valid(candidate, temp_root))
            candidate["cumulative_token_usage"]["cache_write_tokens"] = None
            normalize_bundle()
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            candidate["cumulative_token_usage"]["cache_write_tokens"] = 0
            normalize_bundle()

            relocated = temp_root / "relocated-bundle"
            shutil.copytree(bundle, relocated)
            relocated_candidate = copy.deepcopy(candidate)
            for key, name in {
                "run_record": "run.json",
                "final_diff": "changes.diff",
                "evidence_bundle": "evidence.jsonl.gz",
                "manifest": "manifest.sha256",
            }.items():
                relocated_candidate["artifacts"][key] = f"relocated-bundle/{name}"
            self.assertFalse(runner.pilot_session_artifacts_valid(relocated_candidate, temp_root))

            (bundle / "unmanifested").mkdir()
            (bundle / "unmanifested" / "secret.txt").write_text("undeclared\n")
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            shutil.rmtree(bundle / "unmanifested")
            (bundle / "escape-link").symlink_to("/etc")
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            (bundle / "escape-link").unlink()

            (bundle / "evidence.jsonl.gz").write_bytes(b"not gzip or jsonl")
            rewrite_manifest()
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            restore_bundle()

            original_model = candidate["agent"]["model"]
            candidate["agent"]["model"] = "gpt-5.6-luna"
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            candidate["agent"]["model"] = original_model

            original_profile = candidate["profile"]["profile_id"]
            candidate["profile"]["profile_id"] = "terminal-tokenjuice-codex-hook-v1"
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            candidate["profile"]["profile_id"] = original_profile

            baseline_candidate = copy.deepcopy(candidate)
            sequence_definition = runner.load_sequence(
                baseline_candidate["task_sequence"]["sequence_id"]
            )
            baseline_candidate["task_sequence"]["leakage_controls"].update(
                controller_verifier_scripts_and_canonical_copies_model_visible=False,
                model_visible_acceptance_asset_paths=runner.sequence_model_visible_acceptance_paths(
                    sequence_definition
                ),
            )
            for treatment_profile in (
                "terminal-tokenjuice-codex-hook-v1",
                "stack-tokenjuice-jcodemunch-mcp",
            ):
                candidate = copy.deepcopy(baseline_candidate)
                expected_role = runner.PROFILE_META[treatment_profile]["session_role"]
                candidate["profile"]["profile_id"] = treatment_profile
                candidate["session_role"] = expected_role
                descriptor = candidate["selected_execution"]["descriptor"]
                descriptor["execution_role"] = expected_role
                descriptor["selected_profile"]["profile_id"] = treatment_profile
                candidate["selected_execution"]["descriptor_sha256"] = runner._json_hash(descriptor)
                normalize_bundle()
                with (
                    mock.patch.object(runner.repository_validation, "validate_docker_identity"),
                    mock.patch.object(runner.repository_validation, "validate_tool_adapter_identity"),
                ):
                    self.assertTrue(runner.pilot_session_artifacts_valid(candidate, temp_root))
                    self.assertEqual(runner.reviewed_session_reuse_state(candidate, temp_root), "reusable")
                    with tempfile.TemporaryDirectory() as destination_temp:
                        destination_root = Path(destination_temp)
                        (destination_root / "sources/evaluations/workflow-sessions").mkdir(parents=True)
                        with mock.patch.object(matrix, "ROOT", destination_root):
                            copied = matrix.copy_artifacts_for_sessions(temp_root, [candidate])
                        self.assertEqual(copied, [candidate["artifacts"]["root"]])
            candidate = baseline_candidate
            restore_bundle()

            (bundle / "changes.diff").write_text((bundle / "changes.diff").read_text() + "tamper\n")
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            restore_bundle()
            first_manifest_line = (bundle / "manifest.sha256").read_text().splitlines()[0]
            with (bundle / "manifest.sha256").open("a") as handle:
                handle.write(first_manifest_line + "\n")
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            restore_bundle()
            manifest_lines = (bundle / "manifest.sha256").read_text().splitlines()
            (bundle / "manifest.sha256").write_text("\n".join(manifest_lines[:-1]) + "\n")
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            restore_bundle()
            (bundle / "manifest.sha256").write_text("malformed\n")
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            restore_bundle()
            original_final_diff = candidate["artifacts"]["final_diff"]
            candidate["artifacts"]["final_diff"] = candidate["artifacts"]["manifest"]
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            candidate["artifacts"]["final_diff"] = original_final_diff
            original_evidence = candidate["artifacts"]["evidence_bundle"]
            candidate["artifacts"]["final_diff"], candidate["artifacts"]["evidence_bundle"] = (
                original_evidence,
                original_final_diff,
            )
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            candidate["artifacts"]["final_diff"], candidate["artifacts"]["evidence_bundle"] = (
                original_final_diff,
                original_evidence,
            )
            run_record = json.loads((bundle / "run.json").read_text())
            run_record["token_usage"]["fresh_input_tokens"] += 1
            run_record["token_usage"]["total_provider_tokens"] += 1
            (bundle / "run.json").write_text(json.dumps(run_record, indent=2) + "\n")
            rewrite_manifest()
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            restore_bundle()
            run_record = json.loads((bundle / "run.json").read_text())
            run_record["docker_image_identity"] = {
                **run_record["docker_image_identity"],
                "image_ref": "wrong-runtime:latest",
            }
            (bundle / "run.json").write_text(json.dumps(run_record, indent=2) + "\n")
            rewrite_manifest()
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))
            restore_bundle()
            run_record = json.loads((bundle / "run.json").read_text())
            run_record["session_id"] = "wrong-session"
            (bundle / "run.json").write_text(json.dumps(run_record, indent=2) + "\n")
            rewrite_manifest()
            self.assertFalse(runner.pilot_session_artifacts_valid(candidate, temp_root))

    def test_v2_pilot_gate_requires_exact_independent_zero_count_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            protocol_rel = "sources/evaluations/protocols/unit.json"
            protocol_path = root / protocol_rel
            protocol_path.parent.mkdir(parents=True)
            protocol_path.write_text('{"protocol_id":"unit-current"}\n')
            protocol = {
                "protocol_id": "unit-current",
                "path": protocol_rel,
                "sha256": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
            }
            gate = {
                "pilot_audit_path": "sources/evaluations/audits/baseline-v2-pilot-zero-mistake.json",
                "designated_model_condition": "codex-openai-gpt-5-6-sol-high",
                "model": "gpt-5.6-sol",
                "reasoning_effort": "high",
            }
            sequence = {
                "id": "unit-sequence-v0",
                "fixture_id": "unit-fixture",
                "initial_snapshot": {"commit": "unit-snapshot"},
                "qualification_path": "unit-qualification.json",
                "task_family_generation": "baseline-v2",
                "mistake_gate": gate,
                "tasks": [{"id": "unit-task", "order": 1}],
            }
            docker_identity = {
                "image_ref": "unit-image:latest",
                "image_id": f"sha256:{'a' * 64}",
                "repo_digests": [],
                "repo_tags": ["unit-image:latest"],
            }
            selected_descriptor = {
                "execution_role": "baseline",
                "selected_profile": {"profile_id": "baseline-bare-codex"},
                "runtime": {"docker_image_identity": docker_identity},
                "tool_adapter": {"tool_id": None},
                "agent_condition": {
                    "model_condition_id": gate["designated_model_condition"],
                    "model": gate["model"],
                    "reasoning_effort": gate["reasoning_effort"],
                },
            }
            selected_execution = {"descriptor": selected_descriptor, "descriptor_sha256": "unit-execution"}
            session = {
                "schema_version": 2,
                "session_id": "unit-baseline",
                "status": "completed",
                "session_role": "baseline",
                "replicate_index": 0,
                "task_sequence": {"sequence_id": sequence["id"]},
                "profile": {"profile_id": "baseline-bare-codex"},
                "agent": {
                    "runtime_id": "codex-cli",
                    "provider": "openai",
                    "model_condition_id": gate["designated_model_condition"],
                    "model": gate["model"],
                    "reasoning_effort": gate["reasoning_effort"],
                },
                "interpretation": {
                    "accepted_for_execution": True,
                    "operationally_completed": True,
                    "evaluation_validity": "valid",
                    "accepted_for_objective": True,
                    "primary_objective_hard_baseline": True,
                    "usable_for_primary_objective_token_comparison": True,
                },
                "cumulative_token_usage": {
                    "measurement_source": "codex-jsonl-usage-events",
                    "fresh_input_tokens": 1,
                    "cached_input_tokens": 0,
                    "cache_write_tokens": 0,
                    "output_tokens": 0,
                    "reasoning_tokens": 0,
                    "total_provider_tokens": 1,
                },
                "per_task_results": [{
                    "task_id": "unit-task",
                    "order": 1,
                    "agent_attempted": True,
                    "codex_exit_code": 0,
                    "controller_verification": "passed",
                    "verifier_exit_code": 0,
                    "verifier_passed": True,
                    "accepted": True,
                    "operational_retry_count": 0,
                }],
                "software_quality": {
                    "tasks_attempted": 1,
                    "tasks_passed": 1,
                    "final_verifier_passed": True,
                    "functional_verifier_passed": True,
                },
                "frozen_protocol": protocol,
                "baseline_pool": {"protocol_fingerprint": "unit-pool"},
                "selected_execution": selected_execution,
                "docker_image_identity": docker_identity,
                "tool_adapter_identity": None,
            }
            registry_path = root / "data/workflow-sessions.json"
            registry_path.parent.mkdir(parents=True)
            registry_sessions = [session]
            registry_path.write_text(json.dumps({"sessions": registry_sessions}))
            entry = {
                "sequence_id": sequence["id"],
                "passed": True,
                "trajectory_review_complete": True,
                "independent_source_review_passed": True,
                "reviewer_role": "independent",
                "model_condition": {"id": gate["designated_model_condition"], "model": gate["model"], "reasoning_effort": gate["reasoning_effort"]},
                "baseline_session_id": session["session_id"],
                "frozen_protocol": protocol,
                "qualification_sha256": "unit-qualification",
                "baseline_pool_fingerprint": "unit-pool",
                **{field: 0 for field in runner.PILOT_ZERO_COUNT_FIELDS},
            }
            audit_path = root / gate["pilot_audit_path"]
            audit_path.parent.mkdir(parents=True)
            audit = {"schema_version": 1, "task_family_generation": "baseline-v2", "sequences": [entry]}
            current_identity = {
                **protocol,
                "qualification_sha256": "unit-qualification",
                "baseline_pool_fingerprint": "unit-pool",
                "selected_execution_sha256": "unit-execution",
            }
            current_document = {"selected_execution": selected_execution}
            artifact_valid = True

            def evaluate() -> tuple[bool, str]:
                audit_path.write_text(json.dumps(audit))
                registry_path.write_text(json.dumps({"sessions": registry_sessions}))
                with (
                    mock.patch.object(runner, "current_baseline_v2_protocol", return_value=(current_identity, current_document)),
                    mock.patch.object(runner, "reviewed_session_reuse_state", return_value="reusable"),
                    mock.patch.object(runner, "pilot_session_artifacts_valid", return_value=artifact_valid),
                ):
                    return runner.baseline_v2_treatment_gate(sequence, root)

            self.assertTrue(evaluate()[0])
            for field, malformed in (
                ("audit_schema_version", True),
                ("audit_schema_version", 1.0),
                ("session_schema_version", True),
                ("session_schema_version", 2.0),
                ("replicate_index", False),
                ("replicate_index", 0.0),
            ):
                if field == "audit_schema_version":
                    original = audit["schema_version"]
                    audit["schema_version"] = malformed
                elif field == "session_schema_version":
                    original = session["schema_version"]
                    session["schema_version"] = malformed
                else:
                    original = session["replicate_index"]
                    session["replicate_index"] = malformed
                passed, _reason = evaluate()
                self.assertFalse(passed, (field, malformed))
                if field == "audit_schema_version":
                    audit["schema_version"] = original
                elif field == "session_schema_version":
                    session["schema_version"] = original
                else:
                    session["replicate_index"] = original
            for malformed in (False, True, 0.0, 1.0, 2.0, "0", None):
                duplicate = copy.deepcopy(session)
                duplicate["session_id"] = f"malformed-slot-{malformed!r}"
                duplicate["replicate_index"] = malformed
                registry_sessions.append(duplicate)
                passed, reason = evaluate()
                self.assertFalse(passed, (malformed, reason))
                self.assertIn("malformed replicate_index", reason)
                registry_sessions.pop()
            for malformed in (False, 0.0, "0", None, 1):
                entry["observed_prohibited_operations"] = malformed
                passed, reason = evaluate()
                self.assertFalse(passed)
                self.assertIn("non-integer, or nonzero", reason)
            entry["observed_prohibited_operations"] = 0
            arbitrary = {**protocol, "protocol_id": "unit-arbitrary"}
            entry["frozen_protocol"] = arbitrary
            session["frozen_protocol"] = arbitrary
            passed, reason = evaluate()
            self.assertFalse(passed)
            self.assertIn("exact current designated baseline protocol", reason)
            entry["frozen_protocol"] = protocol
            session["frozen_protocol"] = protocol
            session["profile"]["profile_id"] = "unit-treatment"
            passed, reason = evaluate()
            self.assertFalse(passed)
            self.assertIn("operationally valid provider-backed baseline", reason)
            session["profile"]["profile_id"] = "baseline-bare-codex"
            selected_descriptor["execution_role"] = "treatment"
            passed, reason = evaluate()
            self.assertFalse(passed)
            self.assertIn("operationally valid provider-backed baseline", reason)
            selected_descriptor["execution_role"] = "baseline"
            session["cumulative_token_usage"]["measurement_source"] = "not-provider-backed"
            passed, reason = evaluate()
            self.assertFalse(passed)
            self.assertIn("operationally valid provider-backed baseline", reason)
            session["cumulative_token_usage"]["measurement_source"] = "codex-jsonl-usage-events"
            for malformed_total in (False, 0, 0.0, -1, "1", None):
                session["cumulative_token_usage"]["total_provider_tokens"] = malformed_total
                passed, reason = evaluate()
                self.assertFalse(passed)
                self.assertIn("operationally valid provider-backed baseline", reason)
            session["cumulative_token_usage"]["total_provider_tokens"] = 1
            for field in runner.PILOT_PROVIDER_USAGE_FIELDS:
                value = session["cumulative_token_usage"].pop(field)
                passed, reason = evaluate()
                self.assertFalse(passed, field)
                self.assertIn("operationally valid provider-backed baseline", reason)
                session["cumulative_token_usage"][field] = value
            session["cumulative_token_usage"]["fresh_input_tokens"] = 2
            passed, reason = evaluate()
            self.assertFalse(passed)
            self.assertIn("operationally valid provider-backed baseline", reason)
            session["cumulative_token_usage"]["fresh_input_tokens"] = 1
            del session["cumulative_token_usage"]["measurement_source"]
            session["cumulative_token_usage"]["provider_reported_total"] = 1
            passed, reason = evaluate()
            self.assertFalse(passed)
            self.assertIn("operationally valid provider-backed baseline", reason)
            del session["cumulative_token_usage"]["provider_reported_total"]
            session["cumulative_token_usage"]["measurement_source"] = "codex-jsonl-usage-events"
            session["agent"]["provider"] = "not-openai"
            passed, reason = evaluate()
            self.assertFalse(passed)
            self.assertIn("operationally valid provider-backed baseline", reason)
            session["agent"]["provider"] = "openai"
            session["per_task_results"][0]["task_id"] = "wrong-task"
            passed, reason = evaluate()
            self.assertFalse(passed)
            self.assertIn("operationally valid provider-backed baseline", reason)
            session["per_task_results"][0]["task_id"] = "unit-task"
            session["per_task_results"][0]["verifier_passed"] = False
            session["per_task_results"][0]["verifier_exit_code"] = 1
            session["per_task_results"][0]["controller_verification"] = "failed"
            session["per_task_results"][0]["accepted"] = False
            passed, reason = evaluate()
            self.assertFalse(passed)
            self.assertIn("operationally valid provider-backed baseline", reason)
            session["per_task_results"][0].update({
                "verifier_passed": True,
                "verifier_exit_code": 0,
                "controller_verification": "passed",
                "accepted": True,
            })
            for field, malformed in (
                ("tasks_attempted", 0),
                ("tasks_passed", False),
                ("final_verifier_passed", False),
                ("functional_verifier_passed", False),
            ):
                original = session["software_quality"][field]
                session["software_quality"][field] = malformed
                passed, reason = evaluate()
                self.assertFalse(passed, field)
                self.assertIn("operationally valid provider-backed baseline", reason)
                session["software_quality"][field] = original
            session["docker_image_identity"] = {**docker_identity, "image_ref": "wrong:latest"}
            passed, reason = evaluate()
            self.assertFalse(passed)
            self.assertIn("runtime identity", reason)
            session["docker_image_identity"] = docker_identity
            for mutate_duplicate in (
                lambda duplicate: duplicate.update({"session_role": "treatment"}),
                lambda duplicate: duplicate["selected_execution"].update({"descriptor_sha256": "stale-execution"}),
            ):
                duplicate = copy.deepcopy(session)
                duplicate["session_id"] = "unit-baseline-rerun"
                mutate_duplicate(duplicate)
                registry_sessions.append(duplicate)
                passed, reason = evaluate()
                self.assertFalse(passed)
                self.assertIn("ambiguous, or was rerun", reason)
                registry_sessions.pop()
            artifact_valid = False
            passed, reason = evaluate()
            self.assertFalse(passed)
            self.assertIn("operationally valid provider-backed baseline", reason)

    def test_treatment_planner_requires_passing_pilot_gate(self) -> None:
        with self.assertRaisesRegex(ValueError, "treatments are blocked"):
            matrix.plan_workflow_jobs(
                ["unit-sequence-v0"],
                ["unit-treatment"],
                baseline_state=lambda _sequence: "reusable",
                profile_state=lambda _sequence, _profile: "missing",
                baseline_run_gate=lambda _sequence: (True, "unused for reusable baseline"),
                treatment_gate=lambda _sequence: (False, "pilot audit is absent"),
            )
        jobs = matrix.plan_workflow_jobs(
            ["unit-sequence-v0"],
            ["unit-treatment"],
            baseline_state=lambda _sequence: "reusable",
            profile_state=lambda _sequence, _profile: "missing",
            baseline_run_gate=lambda _sequence: (True, "unused for reusable baseline"),
            treatment_gate=lambda _sequence: (True, "zero-incident pilot passed"),
        )
        self.assertEqual(jobs, [("unit-sequence-v0", "unit-treatment")])

    def test_direct_treatment_runner_checks_pilot_gate_before_protocol(self) -> None:
        sequences = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
        sequence = sequences[0]
        args = mock.Mock(sequence_id=sequence["id"], profile_id="terminal-tokenjuice-codex-hook-v1", prepare_only=True)
        with (
            mock.patch.object(runner, "validate_default_model_condition"),
            mock.patch.object(runner, "validate_run_safety_args"),
            mock.patch.object(runner, "load_sequence", return_value=sequence),
            mock.patch.object(runner, "baseline_v2_treatment_gate", return_value=(False, "synthetic missing pilot audit")),
            self.assertRaisesRegex(ValueError, "treatments are blocked"),
        ):
            runner.run_one(args)

    def test_treatment_protocol_freeze_checks_pilot_gate_before_qualification(self) -> None:
        sequences = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
        sequence = sequences[0]
        with (
            mock.patch.object(contract_refresh.runner, "validate_default_model_condition"),
            mock.patch.object(contract_refresh.runner, "assert_profile_runnable"),
            mock.patch.object(contract_refresh.runner, "load_sequence", return_value=sequence),
            mock.patch.object(contract_refresh.runner, "baseline_v2_treatment_gate", return_value=(False, "synthetic missing pilot audit")),
            self.assertRaisesRegex(ValueError, "treatments are blocked"),
        ):
            contract_refresh.main([
                "--sequence-id", sequence["id"],
                "--profile-id", "terminal-tokenjuice-codex-hook-v1",
            ])

    def test_v2_verifiers_reject_modified_model_visible_acceptance_tests(self) -> None:
        document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        for sequence in document["sequences"]:
            for task in sequence["tasks"]:
                task_dir = (ROOT / task["prompt_path"]).parent
                controller_visible = task_dir / "controller-visible"
                assets = [path for path in controller_visible.rglob("*") if path.is_file()] if controller_visible.is_dir() else []
                for canonical in assets:
                    candidate_rel = canonical.relative_to(controller_visible)
                    with tempfile.TemporaryDirectory() as temp:
                        candidate = Path(temp) / candidate_rel
                        candidate.parent.mkdir(parents=True, exist_ok=True)
                        candidate.write_text("modified acceptance asset\n")
                        result = subprocess.run(
                            ["bash", str(task_dir / "verify.sh")],
                            cwd=temp,
                            env={**os.environ, "WORKFLOW_REPO": temp},
                            text=True,
                            capture_output=True,
                            check=False,
                        )
                    self.assertEqual(result.returncode, 1, (task["id"], result.stdout, result.stderr))
                    self.assertIn("differs from canonical bytes", result.stderr)
                if assets:
                    with tempfile.TemporaryDirectory() as temp:
                        result = subprocess.run(
                            ["bash", str(task_dir / "verify.sh")],
                            cwd=temp,
                            env={**os.environ, "WORKFLOW_REPO": temp},
                            text=True,
                            capture_output=True,
                            check=False,
                        )
                    self.assertEqual(result.returncode, 1, (task["id"], result.stdout, result.stderr))
                    self.assertRegex(result.stderr, r"(?:differs from canonical bytes|acceptance test is missing)")

    def test_provider_free_v2_qualification_records_complete_visible_acceptance(self) -> None:
        document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        for sequence in document["sequences"]:
            qualification_record = json.loads((ROOT / sequence["qualification_path"]).read_text())
            self.assertEqual(qualification_record["acceptance_visibility"], "model-visible-complete")
            self.assertIs(qualification_record["no_model_visible_acceptance_assets"], False)
            self.assertIs(qualification_record["all_acceptance_behavior_model_visible"], True)
            self.assertIs(qualification_record["model_visible_acceptance_assets_match_verifier_copies"], True)
            self.assertIs(qualification_record["no_model_concealed_acceptance_assets"], True)
            self.assertEqual(
                qualification_record["expected_model_visible_acceptance_asset_count"],
                sum(len(validate_repository.BASELINE_V3_ACCEPTANCE_ASSET_PATHS[task["id"]]) for task in sequence["tasks"]),
            )
            records = {record["task_id"]: record for record in qualification_record["tasks"]}
            for task in sequence["tasks"]:
                task_dir = (ROOT / task["prompt_path"]).parent
                controller_visible = task_dir / "controller-visible"
                expected_paths = validate_repository.BASELINE_V3_ACCEPTANCE_ASSET_PATHS[task["id"]]
                self.assertEqual(task["model_visible_acceptance_asset_paths"], expected_paths)
                expected_assets = [
                    {
                        "path": str(Path("controller-visible") / path_text),
                        "model_visible_path": path_text,
                        "sha256": hashlib.sha256((controller_visible / path_text).read_bytes()).hexdigest(),
                    }
                    for path_text in expected_paths
                ]
                self.assertEqual(records[task["id"]]["model_visible_acceptance_asset_paths"], expected_paths)
                self.assertEqual(records[task["id"]]["controller_visible_acceptance_assets"], expected_assets)
        audit = json.loads((ROOT / "sources/evaluations/audits/baseline-v3-task-family-qualification-20260722.json").read_text())
        expected_mistake_gate = {
            key: value
            for key, value in document["sequences"][0]["mistake_gate"].items()
            if key.startswith("allowed_") or key in {"designated_model_condition", "model", "reasoning_effort"}
        }
        for key, value in expected_mistake_gate.items():
            self.assertEqual(audit["mistake_gate"].get(key), value)
        self.assertNotIn("all three counts", json.dumps(audit).lower())
        self.assertEqual(audit["zero_mistake_gate"]["status"], "mixed-fastify-passed-beets-terraform-failed-preserved")
        self.assertEqual(audit["treatment_gate"]["status"], "fastify-eligible-v3-beets-terraform-ineligible")
        self.assertIs(audit["treatment_gate"]["pilot_audit_present"], True)
        self.assertIs(audit["treatment_gate"]["fail_closed"], True)
        self.assertEqual(audit["treatment_gate"]["required_zero_count_fields"], list(runner.PILOT_ZERO_COUNT_FIELDS))
        self.assertEqual(
            audit["treatment_gate"]["enforced_at"],
            ["treatment-protocol-freeze", "matrix-treatment-plan", "direct-treatment-runner"],
        )

    def test_repository_validator_rejects_missing_v2_acceptance_asset_declaration(self) -> None:
        document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        fixtures = json.loads((ROOT / "data/repository-fixtures.json").read_text())
        document["sequences"][0]["tasks"][0]["model_visible_acceptance_asset_paths"] = []
        errors: list[str] = []
        validate_repository.validate_workflow_task_sequences(document, fixtures, errors)
        self.assertTrue(any("exact file-backed Baseline V3 acceptance assets" in error for error in errors), errors)

    def test_repository_validator_rejects_noninteger_or_nonzero_v2_mistake_allowance(self) -> None:
        source_document = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        fixtures = json.loads((ROOT / "data/repository-fixtures.json").read_text())
        for malformed in (1, False, 0.0):
            document = copy.deepcopy(source_document)
            document["sequences"][0]["mistake_gate"]["allowed_unique_model_incidents"] = malformed
            errors: list[str] = []
            validate_repository.validate_workflow_task_sequences(document, fixtures, errors)
            self.assertTrue(any("zero-mistake gate" in error for error in errors), (malformed, errors))


if __name__ == "__main__":
    unittest.main()
