from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import run_codex_workflow_evaluation as runner
from scripts import validate_repository


ROOT = Path(__file__).resolve().parents[1]
SEQUENCE_ID = "fastify-maintenance-sequence-v1"


class SeedConflictContractTest(unittest.TestCase):
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


class FastifyAcceptanceContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        workflow = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
        cls.sequence = next(item for item in workflow["sequences"] if item["id"] == SEQUENCE_ID)

    def test_acceptance_is_behavioral_and_each_seed_spans_five_sources(self) -> None:
        self.assertEqual(self.sequence["acceptance_design"], "behavioral")
        for task in self.sequence["tasks"]:
            verifier = (ROOT / task["verifier_command"]).read_text()
            self.assertNotIn("source-invariant", verifier.lower())
            self.assertNotRegex(verifier, r"(?m)^\s*grep\s")
            patch = ROOT / Path(task["prompt_path"]).parent / "seed-regression.patch"
            changed = [
                line.removeprefix("+++ b/")
                for line in patch.read_text().splitlines()
                if line.startswith("+++ b/") and line != "+++ b/dev/null"
            ]
            production = [path for path in changed if path in {"fastify.js", "fastify.d.ts"} or path.startswith(("lib/", "types/"))]
            self.assertGreaterEqual(len(set(production)), 5, task["id"])
            self.assertEqual(set(changed), set(production), task["id"])

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


if __name__ == "__main__":
    unittest.main()
