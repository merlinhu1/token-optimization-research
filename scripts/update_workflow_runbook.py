#!/usr/bin/env python3
"""Render the maintained workflow-evaluation operator runbook."""
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
ARTIFACT_FILES = ("run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_map() -> dict[str, dict[str, Any]]:
    return {fixture["id"]: fixture for fixture in load_json(FIXTURES).get("fixtures", [])}


def active_sequences() -> list[dict[str, Any]]:
    return [
        sequence
        for sequence in load_json(SEQUENCES).get("sequences", [])
        if sequence.get("status") == "active"
    ]


def render_table(sequences: list[dict[str, Any]], fixtures: dict[str, dict[str, Any]]) -> str:
    lines = [
        "| Sequence | Fixture | Scale | Snapshot | Tasks |",
        "|---|---|---|---|---:|",
    ]
    if not sequences:
        lines.append("| _None_ |  |  |  | 0 |")
        return "\n".join(lines)
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
    if not sequences:
        return "_None._"
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
        for task in sorted(sequence.get("tasks", []), key=lambda item: item.get("order", 0)):
            chunks.append(
                f"| {task.get('order')} | `{task.get('id')}` | "
                f"`{task.get('prompt_path')}` | `{task.get('verifier_command')}` |"
            )
        chunks.append("")
    return "\n".join(chunks).rstrip()


def render() -> str:
    all_sequences = load_json(SEQUENCES).get("sequences", [])
    sequences = [sequence for sequence in all_sequences if sequence.get("status") == "active"]
    planned = [sequence for sequence in all_sequences if sequence.get("status") == "planned"]
    fixtures = fixture_map()
    active_fixture_ids = {str(sequence.get("fixture_id")) for sequence in sequences}
    missing_fixtures = sorted(active_fixture_ids - set(fixtures))
    if missing_fixtures:
        raise SystemExit(f"active sequences reference missing fixtures: {missing_fixtures}")

    artifact_lines = "\n".join(f"  {name}" for name in ARTIFACT_FILES)
    active_table = render_table(sequences, fixtures)
    active_details = render_tasks(sequences)
    candidate_lines = []
    for sequence in planned:
        blockers = sequence.get("readiness_blockers", [])
        reason = "; ".join(str(item) for item in blockers) if blockers else "readiness not yet established"
        candidate_lines.append(f"- `{sequence['id']}`: {reason}")
    candidate_text = "\n".join(candidate_lines) if candidate_lines else "_None._"

    if sequences:
        first_sequence = sequences[0]["id"]
        execution_text = f"""The active sequence list is non-empty. Freeze a protocol, run a no-model prepare, then run the canonical baseline first:

```bash
python3 scripts/run_codex_workflow_evaluation.py --sequence-id {first_sequence} --prepare-only
scripts/run_sequential_workflow_pair.sh {first_sequence}
```

Stop before treatment if the baseline fails any frozen gate."""
    else:
        execution_text = "Paid lane, pair, and matrix execution is disabled because no sequence is active. Planned sequences accept `--prepare-only` for fixture repair, but non-prepare runs fail before model execution."

    return f"""# Workflow Evaluation Runbook

This generated runbook reflects current workflow-sequence readiness.

It is rendered from `data/workflow-task-sequences.json` and `data/repository-fixtures.json` by `scripts/update_workflow_runbook.py`.

Do not hand-edit sequence status here. Update the registries, then run:

```bash
python3 scripts/update_workflow_runbook.py
python3 scripts/validate_repository.py
```

## Evidence boundary

A valid workflow run materializes one prompt and injects one regression at a time. Future regressions, seed patches, task fixtures, verifier assets, controller Git objects, fixed parents, and prior-stage reflogs must remain outside the model-visible surface.

Every active task must use causally related behavioral acceptance. Unrelated exact-source restoration guards are not valid complexity.

## Active sequences

{active_table}

## Planned candidates and blockers

{candidate_text}

## Activation gate

Before changing a sequence to `active`, require:

- at least five causally related production files per primary task, or explicit smoke/calibration scope;
- behavioral seeded-fail/fixed-pass gates;
- lazy one-task seed delivery with future regressions absent;
- a parentless model-facing Git baseline with fixed and prior-stage commits inaccessible;
- controller-only task, seed, verifier, and reference assets;
- cumulative provider usage capture, verifier integrity, isolation, and software-quality review.

A no-model prepare for a planned candidate is allowed:

```bash
SEQUENCE_ID=<planned-sequence-id>
python3 scripts/run_codex_workflow_evaluation.py \
  --sequence-id "$SEQUENCE_ID" \
  --profile-id baseline-bare-codex \
  --prepare-only \
  --skip-container-preflight \
  --skip-codex-preflight \
  --skip-dependency-install
```

`prepare-verification.json` must show only task 1 seeded, future seeds absent, a clean true-root Git baseline, no fixed commit object, no prior reflog, and no model-visible seed or verifier assets.

## Paid execution

{execution_text}

## Active sequence details

{active_details}

## Artifact contract

Each completed session keeps exactly four files:

```text
sources/evaluations/workflow-sessions/<session-id>/
{artifact_lines}
```

`run.json` contains metadata, frozen protocol path/id/SHA-256, baseline pool fingerprint, selected-execution descriptor and hash, immutable Docker image identity, treatment tool adapter identity when applicable, provider usage, seed-delivery/concealment claims, and per-task verifier exits.

`changes.diff` concatenates ordered task deltas, each relative to that task's concealed stage root.

`evidence.jsonl.gz` contains prompts, Codex events, setup logs, per-task deltas, seed-delivery and concealment reports, verifier output and integrity checks, provider-usage extraction, and tool-isolation audit output.

`manifest.sha256` hashes the other three files.

Controller Git objects, generated checkouts, dependency environments, Codex homes, caches, and split task artifacts are scratch state and must not remain beside the compact four files.

## Maintenance contract

- Session IDs and compact evidence are append-only.
- Deterministic verifier success is an execution gate, not an automatic software-quality score.
- Objective acceptance requires a recorded software-quality review.
- `python3 scripts/validate_repository.py` checks generated-runbook drift.
- Truth docs own durable claims; this runbook is generated operator procedure.
"""


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
