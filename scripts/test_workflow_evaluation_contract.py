from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import generate_workflow_qualification as qualification
from scripts import run_codex_workflow_evaluation as runner
from scripts import run_codex_workflow_model_condition as model_condition_runner
from scripts import run_sequential_workflow_matrix as matrix
from scripts import validate_repository


ROOT = Path(__file__).resolve().parents[1]
SEQUENCE_ID = "terraform-maintenance-sequence-v2"


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

    def test_active_qualifications_prove_composite_broken_start(self) -> None:
        sequences = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())["sequences"]
        for sequence in sequences:
            if sequence.get("status") != "active":
                continue
            qualification = json.loads((ROOT / sequence["qualification_path"]).read_text())
            self.assertTrue(qualification["composite_seed_merge_zero"])
            self.assertTrue(qualification["composite_seeded_verifiers_nonzero"])
            self.assertTrue(qualification["full_fixed_cumulative_verifier_zero"])
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
        self.assertEqual(script.count("if ! bash "), 3)
        self.assertGreater(script.index('exit "$status"'), script.rfind("if ! bash "))

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
        for retired in ("previous task verifier passed", "injected only the current regression", "until this verifier passes"):
            self.assertNotIn(retired, prompt.lower())

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
            "sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-path-format-core-regression/agent-prompt.txt": ["PF_KEY_QUERIES", "comp:true", "custom keys", "all three prompts"],
            "sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-multivalue-core-regression/agent-prompt.txt": ["TrackInfo", 'MULTI_VALUE_DSV.normalize("Jazz; Funk")', "TYPE_BY_FIELD", "all three prompts"],
            "sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-tidal-metadata-sync-regression-v2/agent-prompt.txt": ["REIMPORT_FRESH_FIELDS_ITEM", "coverArt", "every paginated request", "all three prompts"],
            "sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-161ffe-tracing-context-regression/agent-prompt.txt": ["ContextOpts.TracingContext", "localRun(ctx, op)", "must compile"],
        }
        for path, required in cases.items():
            prompt = (ROOT / path).read_text()
            for text in required:
                self.assertIn(text, prompt, path)

    def test_all_active_prompts_explain_validation_without_inaccessible_verifier_claims(self) -> None:
        for sequence_id in runner.active_sequence_ids():
            for task in runner.load_sequence(sequence_id)["tasks"]:
                prompt = (ROOT / task["prompt_path"]).read_text()
                self.assertIn("Validation is part of the repair", prompt, task["id"])
                self.assertNotIn("Use the fixture verifier", prompt, task["id"])
                self.assertNotIn("seeded with the regression", prompt, task["id"])

    def test_schema_discriminates_warm_and_legacy_protocols(self) -> None:
        schema = json.loads((ROOT / "schemas/workflow-session-record.schema.json").read_text())
        modes = {branch["properties"]["prompt_delivery"]["properties"]["seed_delivery_mode"]["const"] for branch in schema["properties"]["task_sequence"]["oneOf"]}
        self.assertTrue({"lazy-one-task-at-a-time", "preseeded-composite"}.issubset(modes))

    def test_functional_task_count_is_independent_of_audit_acceptance(self) -> None:
        checkpoints = [{"order": 1}, {"order": 2}]
        self.assertEqual(runner.functional_task_count(expected_tasks=2, task_checkpoints=checkpoints, final_verifier_code=0), 2)
        self.assertEqual(runner.functional_task_count(expected_tasks=2, task_checkpoints=checkpoints, final_verifier_code=1), 0)


class ActiveAcceptanceContractTest(unittest.TestCase):
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
                self.assertGreaterEqual(len(set(production)), 5, task["id"])
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

    def test_active_sequences_use_token_savings_task_subsets(self) -> None:
        self.assertEqual(
            runner.active_sequence_ids(),
            [
                "fastify-maintenance-sequence-v1",
                "terraform-maintenance-sequence-v2",
                "beets-maintenance-sequence-v4",
            ],
        )
        expected_tasks = {
            "terraform-maintenance-sequence-v2": [
                "terraform-161ffe-tracing-context-regression",
                "terraform-520378-computed-block-capabilities-regression",
                "terraform-9ae470-objchange-validation-regression",
            ],
            "beets-maintenance-sequence-v4": [
                "beets-path-format-core-regression",
                "beets-multivalue-core-regression",
                "beets-tidal-metadata-sync-regression-v2",
            ],
        }
        for sequence_id, task_ids in expected_tasks.items():
            sequence = runner.load_sequence(sequence_id)
            self.assertEqual([task["id"] for task in sequence["tasks"]], task_ids)
            self.assertEqual([task["order"] for task in sequence["tasks"]], list(range(1, len(task_ids) + 1)))

    def test_active_sequences_bind_current_qualifications(self) -> None:
        expected = {
            "fastify-maintenance-sequence-v1": "qualification-composite-v5.json",
            "terraform-maintenance-sequence-v2": "qualification-composite-v6.json",
            "beets-maintenance-sequence-v4": "qualification-composite-v9.json",
        }
        for sequence_id in runner.active_sequence_ids():
            self.assertTrue(runner.load_sequence(sequence_id)["qualification_path"].endswith(expected[sequence_id]))

    def test_current_protocol_fingerprint_matches_runner(self) -> None:
        cases = {
            "fastify-maintenance-sequence-v1": "sources/evaluations/protocols/fastify-production-gpt-5.6-luna-xhigh-v7.json",
            "terraform-maintenance-sequence-v2": "sources/evaluations/protocols/hashicorp-terraform-token-savings-production-gpt-5.6-luna-xhigh-v8.json",
            "beets-maintenance-sequence-v4": "sources/evaluations/protocols/beetbox-beets-token-savings-production-gpt-5.6-luna-xhigh-v11.json",
        }
        for sequence_id, protocol_path in cases.items():
            seq = runner.load_sequence(sequence_id)
            protocol = json.loads((ROOT / protocol_path).read_text())
            expected = runner.baseline_protocol_fingerprint(seq)
            self.assertEqual(protocol["baseline_pool"]["protocol_fingerprint"], expected)
            self.assertEqual(protocol["baseline_pool"]["descriptor"], runner.baseline_protocol_descriptor(seq))

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
            protocol="sources/evaluations/protocols/hashicorp-terraform-token-savings-production-gpt-5.6-luna-xhigh-v8.json",
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
            protocol="sources/evaluations/protocols/hashicorp-terraform-token-savings-production-gpt-5.6-luna-xhigh-v8.json",
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
            protocol="sources/evaluations/protocols/hashicorp-terraform-token-savings-production-gpt-5.6-luna-xhigh-v8.json",
            prepare_only=True,
            no_provider=True,
            timeout_per_task=3600,
            docker_image=runner.DEFAULT_DOCKER_IMAGE,
        )
        with self.assertRaisesRegex(ValueError, "selected_execution|treatment_profile_id"):
            runner.validate_protocol_for_run(seq, "retrieval-leanctx", args)

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
        binary_a = {"executable_token": "rtk", "resolved_path": "/tmp/rtk", "realpath": "/tmp/rtk", "sha256": "a" * 64, "metadata": {}, "version": {"captured": True, "output": "rtk 1"}}
        binary_b = {"executable_token": "rtk", "resolved_path": "/tmp/rtk", "realpath": "/tmp/rtk", "sha256": "b" * 64, "metadata": {}, "version": {"captured": True, "output": "rtk 2"}}
        with tempfile.TemporaryDirectory() as tmp:
            protocol_path = Path(tmp) / "protocol.json"
            with mock.patch.object(runner, "docker_image_identity", return_value=image), mock.patch.object(runner, "executable_identity", return_value=binary_a):
                protocol_path.write_text(json.dumps(self.frozen_protocol_doc(protocol_path, seq, "terminal-rtk"), indent=2) + "\n")
            args = mock.Mock(protocol=str(protocol_path), prepare_only=True, no_provider=True, timeout_per_task=3600, docker_image=runner.DEFAULT_DOCKER_IMAGE)
            with mock.patch.object(runner, "docker_image_identity", return_value=image), mock.patch.object(runner, "executable_identity", return_value=binary_b):
                with self.assertRaisesRegex(ValueError, "selected_execution"):
                    runner.validate_protocol_for_run(seq, "terminal-rtk", args)

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
            "cumulative_token_usage": {"measurement_source": "unit", "total_provider_tokens": None, "pricing_basis": "unit"},
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
            {"schema_version": 1, "primary_metric": "cumulative provider-billed workflow tokens", "sessions": [session]},
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
        sequence = runner.load_sequence("fastify-maintenance-sequence-v1")
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
        sequence = runner.load_sequence("fastify-maintenance-sequence-v1")
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
