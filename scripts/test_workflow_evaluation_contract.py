from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import run_codex_workflow_evaluation as runner
from scripts import run_sequential_workflow_matrix as matrix
from scripts import validate_repository


ROOT = Path(__file__).resolve().parents[1]
SEQUENCE_ID = "fastify-maintenance-sequence-v1"


class SeedDeliveryContractTest(unittest.TestCase):
    def test_conflicted_three_way_seed_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Fixture Test"], cwd=repo, check=True)
            source = repo / "value.txt"
            source.write_text("base\n")
            subprocess.run(["git", "add", "value.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
            source.write_text("seed\n")
            patch = Path(tmp) / "seed.patch"
            patch.write_text(subprocess.run(["git", "diff", "--full-index", "--binary"], cwd=repo, check=True, text=True, capture_output=True).stdout)
            subprocess.run(["git", "reset", "--hard", "-q", "HEAD"], cwd=repo, check=True)
            source.write_text("current\n")
            subprocess.run(["git", "add", "value.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "diverged"], cwd=repo, check=True)

            with self.assertRaisesRegex(RuntimeError, "seed patch"):
                runner.apply_seed_patch(repo, patch, Path(tmp) / "apply.log")

    def test_pending_seed_that_is_not_forward_applicable_rejects_stage(self) -> None:
        states = iter([
            {"forward_applicable": False, "reverse_applicable": True},
            {"forward_applicable": False, "reverse_applicable": False},
        ])
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            runner, "seed_patch_application_state", side_effect=lambda *_: next(states)
        ):
            result = runner.verify_seed_delivery_stage({}, Path(tmp), Path(tmp), 1, [2])

        self.assertFalse(result["pending_seed_patches_forward_applicable"])
        self.assertFalse(result["passed"])

    def test_controller_assets_are_reported_if_copied_into_model_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            controller = root / "tasks" / "task-01"
            repo.mkdir(parents=True)
            controller.mkdir(parents=True)
            (controller / "verify.sh").write_text("secret verifier\n")
            (repo / "verify.sh").write_text("secret verifier\n")
            with mock.patch.object(runner, "seed_patch_application_state", return_value={"forward_applicable": True, "reverse_applicable": True}):
                result = runner.verify_seed_delivery_stage({}, repo, root, 1, [])
        self.assertFalse(result["passed"])
        self.assertEqual(result["model_repo_seed_or_verifier_assets"], ["verify.sh"])

    def test_declared_concealed_paths_are_rejected_if_present(self) -> None:
        seq = {"tasks": [{"order": 1, "model_concealed_paths": ["test/handler-timeout.test.js"]}]}
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            runner, "seed_patch_application_state", return_value={"forward_applicable": True, "reverse_applicable": True}
        ):
            root = Path(tmp)
            repo = root / "repo"
            controller = root / "tasks" / "task-01"
            (repo / "test").mkdir(parents=True)
            controller.mkdir(parents=True)
            (controller / "seed-regression.patch").write_text("")
            (repo / "test/handler-timeout.test.js").write_text("acceptance\n")
            result = runner.verify_seed_delivery_stage(seq, repo, root, 1, [])
        self.assertFalse(result["passed"])
        self.assertEqual(result["model_concealed_paths_present"], ["test/handler-timeout.test.js"])


class VerifierContractTest(unittest.TestCase):
    def test_repeated_verifier_outputs_are_stage_specific(self) -> None:
        seq = {"tasks": [{"id": "a", "order": 1}, {"id": "b", "order": 2}]}
        record = {"target": {"repository_path": "repo"}}
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(runner.fixture, "run_backend") as run_backend:
            root = Path(tmp)
            (root / "repo").mkdir()
            run_backend.return_value.returncode = 0
            result = runner.run_one_verifier(seq, 2, record, root / "home", root, "image", stage_order=4)
        self.assertTrue(result["verifier_output"].endswith("verifier-after-task-04-task-02.txt"))
        self.assertTrue(str(run_backend.call_args.kwargs["stdout_path"]).endswith("verifier-after-task-04-task-02.txt"))

    def test_any_completed_stage_verifier_failure_rejects_acceptance(self) -> None:
        completed = [
            {"verifier_exit_code": 0},
            {"verifier_exit_code": 1},
        ]
        self.assertTrue(any(item["verifier_exit_code"] != 0 for item in completed))


class FastifyAcceptanceContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        workflow = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        cls.sequence = next(item for item in workflow["sequences"] if item["id"] == SEQUENCE_ID)

    def test_acceptance_is_hidden_behavioral_and_each_seed_spans_five_sources(self) -> None:
        self.assertEqual(self.sequence["acceptance_design"], "behavioral")
        for task in self.sequence["tasks"]:
            self.assertGreater(len(task.get("model_concealed_paths", [])), 0, task["id"])
            verifier = (ROOT / task["verifier_command"]).read_text()
            self.assertIn("node <<'NODE'", verifier)
            self.assertNotIn("node --test test/", verifier)
            self.assertNotRegex(verifier, r"(?m)^\s*grep\s")
            patch = ROOT / Path(task["prompt_path"]).parent / "seed-regression.patch"
            changed = validate_repository.patch_paths(patch)
            production = [path for path in changed if validate_repository.is_production_path(path)]
            self.assertGreaterEqual(len(set(production)), 5, task["id"])
            self.assertEqual(set(changed), set(production), task["id"])

    def test_qualification_records_concealed_paths_absent(self) -> None:
        qualification = json.loads((ROOT / self.sequence["qualification_path"]).read_text())
        records = {item["task_id"]: item for item in qualification["tasks"]}
        for task in self.sequence["tasks"]:
            self.assertEqual(records[task["id"]]["model_concealed_paths"], sorted(task["model_concealed_paths"]))
            self.assertEqual(records[task["id"]]["expected_model_concealed_paths"], runner.expected_task_concealed_paths(task))
            self.assertEqual(records[task["id"]]["omitted_expected_model_concealed_paths"], [])
            self.assertIs(records[task["id"]]["declared_concealment_matches_expected"], True)
            self.assertIs(records[task["id"]]["model_concealed_absent"], True)

    def test_expected_concealment_omission_is_rejected(self) -> None:
        task = {
            "upstream_test_paths": ["test/internals/errors.test.js"],
            "compatibility_rebased_test_paths": ["test/types/request.tst.ts"],
            "model_concealed_paths": ["test/internals/errors.test.js"],
        }
        self.assertEqual(runner.omitted_expected_concealment(task), ["test/types/request.tst.ts"])

    def test_qualification_production_files_match_patch_exactly(self) -> None:
        qualification = json.loads((ROOT / self.sequence["qualification_path"]).read_text())
        records = {item["task_id"]: item for item in qualification["tasks"]}
        for task in self.sequence["tasks"]:
            patch = ROOT / Path(task["prompt_path"]).parent / "seed-regression.patch"
            self.assertEqual(records[task["id"]]["production_files"], [path for path in validate_repository.patch_paths(patch) if validate_repository.is_production_path(path)])

    def test_active_readiness_surfaces_are_consistent(self) -> None:
        fixtures = json.loads((ROOT / "data/repository-fixtures.json").read_text())
        medium = json.loads((ROOT / "data/medium-project-candidates.json").read_text())
        fixture = next(item for item in fixtures["fixtures"] if item["id"] == "medium-fastify-fastify")
        candidate = next(item for item in medium["candidates"] if item["id"] == "medium-fastify-fastify")
        self.assertEqual(self.sequence["status"], "active")
        self.assertEqual(self.sequence["readiness_blockers"], [])
        self.assertEqual(fixture["status"], "qualified-fixture")
        self.assertEqual(fixture["qualification_status"], "active-reproduction-flow")
        self.assertEqual(candidate["qualification_status"], "active-reproduction-flow")

        errors: list[str] = []
        validate_repository.validate_fixture_sequence_status_consistency(
            {"sequences": [self.sequence]},
            {"fixtures": [fixture]},
            {"candidates": []},
            {"candidates": [candidate]},
            errors,
        )
        self.assertEqual(errors, [])


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

    def test_current_protocol_fingerprint_matches_runner(self) -> None:
        seq = runner.load_sequence(SEQUENCE_ID)
        protocol = json.loads((ROOT / "sources/evaluations/protocols/fastify-production-gpt-5.6-terra-medium-v3.json").read_text())
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
            protocol="sources/evaluations/protocols/fastify-production-gpt-5.6-terra-medium-v3.json",
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
            protocol="sources/evaluations/protocols/fastify-production-gpt-5.6-terra-medium-v3.json",
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
            protocol="sources/evaluations/protocols/fastify-production-gpt-5.6-terra-medium-v3.json",
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
                    "seed_delivery_mode": "lazy-one-task-at-a-time",
                    "future_seed_regressions_visible": False,
                },
                "leakage_controls": {
                    "seed_origin_concealed": True,
                    "seed_patches_model_visible": False,
                    "git_baseline_true_root_per_task": True,
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


class MatrixLifecycleContractTest(unittest.TestCase):
    def test_failed_lane_cannot_publish(self) -> None:
        self.assertFalse(matrix.publication_allowed(False, [{"exit_code": 1}]))
        self.assertFalse(matrix.publication_allowed(True, [{"exit_code": 0}]))
        self.assertTrue(matrix.publication_allowed(False, [{"exit_code": 0}]))

    def test_missing_baseline_collapses_treatments_to_one_baseline_lane(self) -> None:
        jobs = matrix.plan_workflow_jobs(
            [SEQUENCE_ID],
            ["terminal-rtk", "terminal-codegraph"],
            baseline_state=lambda _sequence: "missing",
            profile_state=lambda _sequence, _profile: "missing",
        )
        self.assertEqual(jobs, [(SEQUENCE_ID, "baseline-bare-codex")])

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
