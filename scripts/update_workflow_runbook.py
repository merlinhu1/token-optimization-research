#!/usr/bin/env python3
"""Render the maintained human runbook for the active workflow-evaluation matrix."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "evaluations" / "workflow-evaluation-runbook.md"
SEQUENCES = ROOT / "data" / "workflow-task-sequences.json"
FIXTURES = ROOT / "data" / "repository-fixtures.json"
EXPECTED_ACTIVE_FIXTURES = {
    "large-hashicorp-terraform",
    "large-orchardcms-orchardcore",
    "medium-fastify-fastify",
    "medium-beetbox-beets",
}
ARTIFACT_FILES = ("run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_map() -> dict[str, dict[str, Any]]:
    return {fixture["id"]: fixture for fixture in load_json(FIXTURES).get("fixtures", [])}


def active_sequences() -> list[dict[str, Any]]:
    sequences = [
        sequence
        for sequence in load_json(SEQUENCES).get("sequences", [])
        if sequence.get("status") == "active"
    ]
    return sequences


def render_table(sequences: list[dict[str, Any]], fixtures: dict[str, dict[str, Any]]) -> str:
    lines = [
        "| Sequence | Fixture | Scale | Snapshot | Tasks |",
        "|---|---|---|---|---:|",
    ]
    for sequence in sequences:
        fixture_id = sequence["fixture_id"]
        fixture = fixtures.get(fixture_id, {})
        snapshot = sequence.get("initial_snapshot", {})
        upstream = snapshot.get("upstream") or fixture.get("source", {}).get("url") or ""
        commit = snapshot.get("commit") or fixture.get("source", {}).get("commit") or ""
        snapshot_text = f"[`{commit[:12]}`]({upstream})" if upstream and commit else (f"`{commit[:12]}`" if commit else "")
        lines.append(
            "| "
            f"`{sequence['id']}` | "
            f"`{fixture_id}` | "
            f"{sequence.get('fixture_scale', fixture.get('fixture_scale', ''))} | "
            f"{snapshot_text} | "
            f"{len(sequence.get('tasks', []))} |"
        )
    return "\n".join(lines)


def render_tasks(sequences: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for sequence in sequences:
        chunks.append(f"### `{sequence['id']}`")
        chunks.append("")
        chunks.append(f"- Fixture: `{sequence['fixture_id']}`")
        chunks.append(f"- Primary metric: {sequence.get('primary_metric', '')}")
        chunks.append(f"- Reset policy: {sequence.get('reset_policy', '')}")
        chunks.append("")
        chunks.append("| Order | Task | Prompt | Verifier |")
        chunks.append("|---:|---|---|---|")
        for task in sorted(sequence.get("tasks", []), key=lambda task: task.get("order", 0)):
            chunks.append(
                f"| {task.get('order')} | `{task.get('id')}` | "
                f"`{task.get('prompt_path')}` | `{task.get('verifier_command')}` |"
            )
        chunks.append("")
    return "\n".join(chunks).rstrip()


def render() -> str:
    sequences = active_sequences()
    fixtures = fixture_map()
    active_fixture_ids = {str(sequence.get("fixture_id")) for sequence in sequences}
    if active_fixture_ids != EXPECTED_ACTIVE_FIXTURES:
        raise SystemExit(
            "active workflow fixture set drifted: "
            f"expected {sorted(EXPECTED_ACTIVE_FIXTURES)}, found {sorted(active_fixture_ids)}"
        )
    if len(sequences) != 4:
        raise SystemExit(f"expected exactly four active workflow sequences, found {len(sequences)}")
    missing_fixtures = sorted(active_fixture_ids - set(fixtures))
    if missing_fixtures:
        raise SystemExit(f"active sequences reference missing fixtures: {missing_fixtures}")

    artifact_lines = "\n".join(f"  {name}" for name in ARTIFACT_FILES)
    runbook = f"""# Workflow Evaluation Runbook

This is the maintained human-facing runbook for the active four-workflow evaluation matrix.

It is rendered from `data/workflow-task-sequences.json` and `data/repository-fixtures.json` by `scripts/update_workflow_runbook.py`.

Do not hand-edit active sequence tables in this file; update the machine registries first, then run:

```bash
python3 scripts/update_workflow_runbook.py
python3 scripts/validate_repository.py
```

## Canonical sources

- Active sequences: `data/workflow-task-sequences.json`
- Fixture contracts: `data/repository-fixtures.json`
- Completed sessions: `data/workflow-sessions.json`
- Single-sequence runner: `scripts/run_codex_workflow_evaluation.py`
- Matrix runner: `scripts/run_sequential_workflow_matrix.py`
- Artifact contract: `templates/workflow-session-record.json`

## Evidence boundary

The primary evidence path is continuous workflow simulation.

Single-task isolated runs and tiny calibration fixtures are not the default matrix and do not support positive workflow-level claims.

A positive reproduction claim needs paired baseline and treatment sessions on the same sequence, runtime, provider, model condition, prompt-disclosure policy, and verifier set.

## Active four-workflow matrix

{render_table(sequences, fixtures)}

## Running a smoke prepare

Use `--prepare-only` to verify fixture construction, task prompt sanitization, and seed-origin concealment without spending model tokens.

```bash
python3 scripts/run_codex_workflow_evaluation.py \\
  --sequence-id terraform-maintenance-sequence-v1 \\
  --profile-id baseline-bare-codex \\
  --prepare-only \\
  --skip-container-preflight \\
  --skip-codex-preflight \\
  --skip-dependency-install \\
  --session-id smoke-terraform-sequential-runner

rm -rf sources/evaluations/workflow-sessions/smoke-terraform-sequential-runner
```

Expected smoke properties:

- The generated task prompt for order 1 contains task 1 only.
- Future task prompts are not visible before their turn.
- The materialized repository has no upstream remote that reveals the fix.
- The visible baseline commit is the workflow broken-start state.

## Running one lane

Baseline lane:

```bash
python3 scripts/run_codex_workflow_evaluation.py \\
  --sequence-id terraform-maintenance-sequence-v1 \\
  --profile-id baseline-bare-codex \\
  --timeout-per-task 1800
```

Treatment lane:

```bash
python3 scripts/run_codex_workflow_evaluation.py \\
  --sequence-id terraform-maintenance-sequence-v1 \\
  --profile-id retrieval-leanctx \\
  --timeout-per-task 1800
```

## Running paired lanes

Run the paired baseline plus LeanCTX lanes for one sequence:

```bash
scripts/run_sequential_workflow_pair.sh terraform-maintenance-sequence-v1
```

Use a different replicate or timeout when needed:

```bash
REPLICATE_INDEX=1 scripts/run_sequential_workflow_pair.sh \\
  beets-maintenance-sequence-v1 \\
  --timeout-per-task 2400
```

## Running the active matrix

Dry-run the matrix plan:

```bash
scripts/run_sequential_workflow_matrix.py --dry-run
```

Run all active flows with the conservative default concurrency:

```bash
scripts/run_sequential_workflow_matrix.py
```

Run all four active flows concurrently only when provider quota and host resources allow it:

```bash
scripts/run_sequential_workflow_matrix.py --max-parallel 4
```

Smoke two flows without model spend:

```bash
scripts/run_sequential_workflow_matrix.py \\
  terraform-maintenance-sequence-v1 \\
  fastify-maintenance-sequence-v1 \\
  --max-parallel 2 \\
  --prepare-only \\
  --skip-container-preflight \\
  --skip-codex-preflight \\
  --skip-dependency-install
```

## Active sequence details

{render_tasks(sequences)}

## Artifact contract

Each completed session keeps exactly four files in its session directory:

```text
sources/evaluations/workflow-sessions/<session-id>/
{artifact_lines}
```

`run.json` contains summary metadata, provider usage, and per-task verifier exits.

`changes.diff` contains the final code changes produced by the agent.

`evidence.jsonl.gz` contains recoverable raw streams such as prompts, Codex events, setup logs, verifier output, provider usage extraction, and tool-isolation audit output.

`manifest.sha256` hashes the other three files.

Do not commit materialized runtime state such as `project/`, `project/repo/`, `.venv/`, `__pycache__/`, `codex-homes/`, split task transcripts, or split verifier/setup logs.

## Maintenance contract

- Update `data/workflow-task-sequences.json` and `data/repository-fixtures.json` before updating this runbook.
- Run `python3 scripts/update_workflow_runbook.py` after registry changes.
- `python3 scripts/validate_repository.py` runs `scripts/update_workflow_runbook.py --check` and fails on drift.
- Truth docs own durable claims; this runbook is the operator procedure generated from the current registries.
- Retired calibration artifacts such as `sources/evaluations/fixture-corpus/v1/` and `sources/evaluations/phase-2-experiment-suite-v1/` should not reappear as active workflow architecture.
"""
    return runbook


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the checked-in runbook is stale")
    args = parser.parse_args()

    rendered = render()
    if args.check:
        current = RUNBOOK.read_text(encoding="utf-8") if RUNBOOK.exists() else ""
        if current != rendered:
            print(f"{RUNBOOK.relative_to(ROOT)} is stale; run python3 scripts/update_workflow_runbook.py", file=sys.stderr)
            return 1
        return 0
    RUNBOOK.parent.mkdir(parents=True, exist_ok=True)
    RUNBOOK.write_text(rendered, encoding="utf-8")
    print(f"wrote {RUNBOOK.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
