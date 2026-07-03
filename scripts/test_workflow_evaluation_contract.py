from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import generate_workflow_qualification as qualification
from scripts import refresh_workflow_contracts as contract_refresh
from scripts import run_codex_workflow_evaluation as runner
from scripts import run_codex_workflow_model_condition as model_condition_runner
from scripts import run_sequential_workflow_matrix as matrix
from scripts import validate_repository


SEQUENCE_ID = "terraform-lifecycle-sequence-v0"


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
        runbook = (ROOT / "docs/evaluations/workflow-evaluation-runbook.md").read_text()
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
        self.assertEqual(shortlisted, ["retrieval-codegraph"])
        runner.assert_profile_runnable("retrieval-codegraph")
        with self.assertRaisesRegex(ValueError, "deferred"):
            runner.assert_profile_runnable("terminal-rtk")

        fixtures = json.loads((ROOT / "data/repository-fixtures.json").read_text())["fixtures"]
        active = [fixture for fixture in fixtures if fixture.get("evaluation_use") == "primary-objective"]
        self.assertEqual(
            [fixture["id"] for fixture in active],
            ["medium-fastify-fastify", "medium-beetbox-beets", "large-hashicorp-terraform"],
        )
        for fixture in active:
            self.assertEqual(fixture["candidate_profiles"], ["baseline-bare-codex", "retrieval-codegraph"])

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

    def test_protocol_writer_refuses_to_overwrite_different_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "protocol.json"
            contract_refresh.write_json(path, {"value": 1})
            contract_refresh.write_json(path, {"value": 1})
            with self.assertRaises(FileExistsError):
                contract_refresh.write_json(path, {"value": 2})

    def test_empty_preproduction_registry_has_no_occupied_campaign_slots(self) -> None:
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        sequence = runner.load_sequence("beets-lifecycle-sequence-v0")
        self.assertEqual(registry["production_status"], "pre-production")
        self.assertEqual(registry["sessions"], [])
        self.assertIsNone(matrix.find_baseline_record(registry, sequence, 0))
        self.assertIsNone(runner.find_pool_profile_record(registry, sequence, "behavior-caveman", 0))

    def test_protocol_lookup_rejects_unknown_sequence(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown or non-active workflow sequence"):
            matrix.find_protocol(
                ROOT,
                "missing-lifecycle-sequence-v0",
                "baseline-bare-codex",
            )

    def test_active_protocol_remains_discoverable_after_execution(self) -> None:
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
                            {"frozen_protocol": {"path": protocol_rel}}
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
                        "selected_profile": {"profile_id": "baseline-bare-codex"}
                    },
                    "descriptor_sha256": "unit-exec-hash",
                },
            }
            (root / protocol_rel).write_text(json.dumps(protocol))
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
                    "execution_condition_descriptor",
                    return_value={
                        "selected_profile": {
                            "profile_id": "baseline-bare-codex"
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
                        "baseline-bare-codex",
                    ),
                    root / protocol_rel,
                )

    def test_current_protocols_declare_strict_schema_version(self) -> None:
        for sequence_id in runner.active_sequence_ids():
            path = matrix.find_protocol(ROOT, sequence_id, "baseline-bare-codex")
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
        for rel in (
            "templates/progressive-evaluation-change/protocol.md",
            "templates/progressive-evaluation-change/results.md",
        ):
            self.assertNotIn("estimated cost", (ROOT / rel).read_text().lower(), rel)

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
        self.assertTrue(sequence["qualification_path"].endswith("qualification-lifecycle-v0.json"))

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
            protocol=str(matrix.find_protocol(ROOT, SEQUENCE_ID, "baseline-bare-codex").relative_to(ROOT)),
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
            protocol=str(matrix.find_protocol(ROOT, SEQUENCE_ID, "baseline-bare-codex").relative_to(ROOT)),
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
            protocol=str(matrix.find_protocol(ROOT, SEQUENCE_ID, "baseline-bare-codex").relative_to(ROOT)),
            prepare_only=True,
            no_provider=True,
            timeout_per_task=3600,
            docker_image=runner.DEFAULT_DOCKER_IMAGE,
        )
        with self.assertRaisesRegex(ValueError, "selected_execution|treatment_profile_id"):
            runner.validate_protocol_for_run(seq, "retrieval-codegraph", args)

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
                protocol_path.write_text(json.dumps(self.frozen_protocol_doc(protocol_path, seq, "retrieval-codegraph"), indent=2) + "\n")
            args = mock.Mock(protocol=str(protocol_path), prepare_only=True, no_provider=True, timeout_per_task=3600, docker_image=runner.DEFAULT_DOCKER_IMAGE)
            with mock.patch.object(runner, "docker_image_identity", return_value=image), mock.patch.object(runner, "executable_identity", return_value=binary_b):
                with self.assertRaisesRegex(ValueError, "selected_execution"):
                    runner.validate_protocol_for_run(seq, "retrieval-codegraph", args)

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

    def test_unregistered_override_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            model_condition_runner.registered_condition("missing", "gpt-missing", "high")


class MatrixLifecycleContractTest(unittest.TestCase):
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

    def test_quality_passing_nonaccepted_baseline_is_not_hard_reusable(self) -> None:
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
                "quality_score": 4,
            },
            "cumulative_token_usage": {"total_provider_tokens": 1000},
        }
        with mock.patch.object(matrix, "compact_artifacts_intact", return_value=True):
            self.assertFalse(matrix.hard_baseline_usable(session))

    def test_hard_baseline_comparison_scores_correctness_and_tokens(self) -> None:
        sequence = runner.load_sequence("fastify-lifecycle-sequence-v0")
        baseline = {
            "session_id": "hard-baseline",
            "study_id": "study",
            "cumulative_token_usage": {"total_provider_tokens": 1000},
            "software_quality": {"tasks_agent_claimed_complete": 5, "tasks_passed": 0},
        }
        treatment = {
            "session_id": "treatment",
            "experiment_group_id": "group",
            "cumulative_token_usage": {"total_provider_tokens": 900},
            "software_quality": {"tasks_agent_claimed_complete": 5, "tasks_passed": 1},
        }
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(matrix, "ROOT", Path(tmp)):
            path = matrix.write_hard_baseline_comparison(sequence, baseline, treatment, "terminal-rtk", 0)
            comparison = json.loads(path.read_text())
        self.assertTrue(comparison["correctness_improved"])
        self.assertTrue(comparison["token_efficiency_improved"])
        self.assertTrue(comparison["treatment_outperforms_baseline"])
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


if __name__ == "__main__":
    unittest.main()
