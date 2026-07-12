#!/usr/bin/env python3
"""Render the maintained workflow-evaluation operator runbook."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_codex_workflow_evaluation as workflow  # type: ignore

RUNBOOK = ROOT / "docs" / "evaluations" / "operations" / "runbook.md"
SEQUENCES = ROOT / "data" / "workflow-task-sequences.json"
FIXTURES = ROOT / "data" / "repository-fixtures.json"
SESSIONS = ROOT / "data" / "workflow-sessions.json"
PROFILES = ROOT / "data" / "evaluation-profiles.json"
AGENT_RUNTIMES = ROOT / "data" / "evaluation-agent-runtimes.json"
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


def sequence_model_flags(sequence: dict[str, Any]) -> str:
    gate = sequence.get("mistake_gate", {})
    condition_id = gate.get("designated_model_condition")
    model = gate.get("model")
    effort = gate.get("reasoning_effort")
    if not all(isinstance(value, str) and value for value in (condition_id, model, effort)):
        return ""
    return (
        f"--workflow-model-condition-id {condition_id} "
        f"--workflow-model {model} --workflow-reasoning-effort {effort}"
    )


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

    session_records = load_json(SESSIONS).get("sessions", [])
    model_conditions = load_json(AGENT_RUNTIMES).get("model_conditions", [])
    active_default_condition_ids = [
        str(condition.get("id"))
        for condition in model_conditions
        if condition.get("status") == "active-default"
    ]
    if len(active_default_condition_ids) != 1:
        raise SystemExit(
            "runbook generation requires exactly one active-default model condition; "
            f"found {active_default_condition_ids}"
        )
    active_default_condition_id = active_default_condition_ids[0]
    runnable_profiles = sorted(
        profile["id"]
        for profile in load_json(PROFILES).get("profiles", [])
        if profile.get("status") == "screening-shortlist"
    )
    runnable_profile_text = ", ".join(f"`{profile_id}`" for profile_id in runnable_profiles) or "_None_"
    current_default_pool_fingerprints = {}
    for sequence in sequences:
        gate = sequence.get("mistake_gate")
        if sequence.get("task_family_generation") in {"baseline-v2", "baseline-v3"} and isinstance(gate, dict):
            current_protocol, _document = workflow.current_baseline_v2_protocol(sequence, gate, ROOT)
            current_default_pool_fingerprints[sequence["id"]] = current_protocol["baseline_pool_fingerprint"]
        else:
            current_default_pool_fingerprints[sequence["id"]] = workflow.baseline_protocol_fingerprint(sequence)
    current_baseline_condition_ids = {
        sequence["id"]: str(sequence.get("mistake_gate", {}).get("designated_model_condition") or active_default_condition_id)
        for sequence in sequences
    }
    reusable_baseline_replicates: dict[str, list[int]] = {}
    historical_default_baseline_replicates: dict[tuple[str, str], list[int]] = {}
    model_comparison_baseline_replicates: dict[tuple[str, str, str], list[int]] = {}
    for session in session_records:
        sequence_id = session.get("task_sequence", {}).get("sequence_id")
        replicate_index = session.get("replicate_index")
        condition_id = session.get("agent", {}).get("model_condition_id")
        pool_fingerprint = session.get("baseline_pool", {}).get("protocol_fingerprint")
        if (
            isinstance(sequence_id, str)
            and isinstance(replicate_index, int)
            and isinstance(condition_id, str)
            and isinstance(pool_fingerprint, str)
            and session.get("status") == "completed"
            and session.get("session_role") == "baseline"
            and session.get("interpretation", {}).get("accepted_for_objective") is True
        ):
            if (
                condition_id == current_baseline_condition_ids.get(sequence_id)
                and pool_fingerprint == current_default_pool_fingerprints.get(sequence_id)
            ):
                reusable_baseline_replicates.setdefault(sequence_id, []).append(replicate_index)
            elif condition_id == active_default_condition_id:
                historical_default_baseline_replicates.setdefault(
                    (sequence_id, pool_fingerprint), []
                ).append(replicate_index)
            else:
                model_comparison_baseline_replicates.setdefault(
                    (sequence_id, condition_id, pool_fingerprint), []
                ).append(replicate_index)
    reusable_baseline_sequences = set(reusable_baseline_replicates)
    pending_baselines = [
        sequence for sequence in sequences if sequence["id"] not in reusable_baseline_sequences
    ]
    retained_baselines = [
        sequence for sequence in sequences if sequence["id"] in reusable_baseline_sequences
    ]

    if sequences:
        chunks: list[str] = []
        chunks.append(
            f"Current runnable treatment profiles: {runnable_profile_text}. Historical profiles marked `historical-profile` are occupied evidence identities and cannot be rerun in place."
        )
        blocked_gates = []
        pilot_run_states: dict[str, tuple[bool, str]] = {}
        for sequence in sequences:
            gate_passed, gate_reason = workflow.baseline_v2_treatment_gate(sequence, ROOT)
            pilot_run_states[sequence["id"]] = workflow.baseline_v2_pilot_run_gate(sequence, ROOT)
            if not gate_passed:
                blocked_gates.append(f"`{sequence['id']}` ({gate_reason})")
        if blocked_gates:
            any_pilot_allowed = any(allowed for allowed, _reason in pilot_run_states.values())
            chunks.append(
                "Treatment protocol freezing, preparation, and execution are machine-blocked for "
                + ", ".join(blocked_gates)
                + (
                    ". Only an unoccupied designated baseline pilot identity may run before its independent zero-incident audit passes."
                    if any_pilot_allowed
                    else ". The designated pilot identities are occupied by immutable attempt evidence and their completed audits. Failed classifications are permanent for this generation; correcting a lane requires a new generation and new identities."
                )
            )
        if pending_baselines:
            prepare_commands = "\n".join(
                f"python3 scripts/run_sequential_workflow_matrix.py {sequence['id']} {sequence_model_flags(sequence)} --prepare-only".replace("  ", " ")
                for sequence in pending_baselines
            )
            runnable_pending = [
                sequence for sequence in pending_baselines
                if pilot_run_states.get(sequence["id"], (True, ""))[0]
            ]
            baseline_commands = "\n".join(
                f"python3 scripts/run_sequential_workflow_matrix.py {sequence['id']} {sequence_model_flags(sequence)}".rstrip()
                for sequence in runnable_pending
            )
            command_block = prepare_commands + (f"\n{baseline_commands}" if baseline_commands else "")
            chunks.append(
                "Provider-free preparation remains available for lanes without a reusable operational baseline; paid commands are listed only for unoccupied pilot identities:\n\n"
                f"```bash\n{command_block}\n```"
            )
        if retained_baselines:
            unlocked_baselines = []
            for sequence in retained_baselines:
                gate_passed, gate_reason = workflow.baseline_v2_treatment_gate(sequence, ROOT)
                if gate_passed:
                    unlocked_baselines.append((sequence, gate_reason))
            if unlocked_baselines:
                retained_ids = ", ".join(
                    f"`{sequence['id']}` ({', '.join(f'r{index}' for index in sorted(set(reusable_baseline_replicates[sequence['id']])))})"
                    for sequence, _reason in unlocked_baselines
                )
                freeze_blocks = []
                for sequence, _reason in unlocked_baselines:
                    flags = sequence_model_flags(sequence)
                    freeze_blocks.append(
                        f"SEQUENCE_ID={sequence['id']}\n"
                        "PROFILE_ID=replace-with-compatible-profile-id\n"
                        f"python3 scripts/refresh_workflow_contracts.py --sequence-id \"$SEQUENCE_ID\" --profile-id \"$PROFILE_ID\" {flags}\n"
                        "python3 scripts/validate_repository.py\n"
                        f"python3 scripts/run_sequential_workflow_matrix.py \"$SEQUENCE_ID\" --treatment-profile \"$PROFILE_ID\" {flags} --dry-run"
                    )
                chunks.append(
                    f"Reusable, zero-incident-audited baselines exist for {retained_ids}. No current treatment protocol is frozen, so no paid treatment command is published. Choose one compatible profile, freeze and validate its protocol provider-free, certify the resulting exact tree, and then execute the rendered dry-run verbatim before requesting paid execution:\n\n"
                    f"```bash\n{'\n\n'.join(freeze_blocks)}\n```"
                )
        if historical_default_baseline_replicates:
            historical_ids = ", ".join(
                f"`{sequence_id}` pool `{pool_fingerprint}` "
                f"({', '.join(f'r{index}' for index in sorted(set(replicates)))})"
                for (sequence_id, pool_fingerprint), replicates in sorted(
                    historical_default_baseline_replicates.items()
                )
            )
            chunks.append(
                "Earlier active-default baseline pools are retained but are not reusable for the current contract generation: "
                f"{historical_ids}."
            )
        if model_comparison_baseline_replicates:
            comparison_ids = ", ".join(
                f"`{sequence_id}` under `{condition_id}` pool `{pool_fingerprint}` "
                f"({', '.join(f'r{index}' for index in sorted(set(replicates)))})"
                for (sequence_id, condition_id, pool_fingerprint), replicates in sorted(
                    model_comparison_baseline_replicates.items()
                )
            )
            chunks.append(
                "Non-default model-comparison baselines are tracked separately: "
                f"{comparison_ids}. They do not satisfy active-default baseline requirements "
                "or define treatment-pair reuse."
            )
        chunks.append(
            "Retain the first operationally valid provider sample for each protocol and replicate. Stop only when a sample is fixture-invalid or operationally incomplete; verifier and review outcomes are diagnostic."
        )
        execution_text = "\n\n".join(chunks)
    else:
        execution_text = "Paid lane, pair, and matrix execution is disabled because no sequence is active. Planned sequences accept `--prepare-only` for fixture repair, but non-prepare runs fail before model execution."

    if sequences:
        prepare_sequence_id = sequences[0]["id"]
        prepare_model_flags = sequence_model_flags(sequences[0])
    else:
        prepare_sequence_id = "<frozen-sequence-id>"
        prepare_model_flags = "<frozen-model-condition-flags>"

    return f"""# Workflow Evaluation Runbook

This generated runbook reflects current workflow-sequence readiness.

It is rendered from `data/workflow-task-sequences.json`, `data/repository-fixtures.json`, `data/evaluation-profiles.json`, `data/evaluation-agent-runtimes.json`, and `data/workflow-sessions.json` by `scripts/update_workflow_runbook.py`.

Do not hand-edit execution status here. Update the registries, then run:

```bash
python3 scripts/update_workflow_runbook.py
python3 scripts/validate_repository.py
```

## Evidence boundary

A valid Baseline V3 workflow pre-seeds every regression and its focused model-visible acceptance test into one qualified composite broken root, then materializes one prompt at a time. Each prompt supplies one exact mechanical old-to-new edit command plus only its focused validation command; Beets uses the locked project environment and Terraform exports the pinned Go toolchain path explicitly. Seed patch files, controller scripts, and fixed parents remain outside the model-visible surface; final verification repeats only the commands and behavior disclosed in each prompt. Product-effect eligibility also requires parity with the pinned official Codex integration and positive treatment-assignment evidence; MCP configuration/listing alone is insufficient.

Every active task must use causally related behavioral acceptance. Unrelated exact-source restoration guards are not valid complexity.

## Active sequences

{active_table}

## Planned candidates and blockers

{candidate_text}

## Activation gate

Before changing a sequence to `active`, require:

- the smallest causally related production surface that satisfies explicit semantic acceptance, with no arbitrary changed-file minimum;
- behavioral seeded-fail/fixed-pass gates;
- a conflict-free composite seed whose task verifiers all fail at lane start;
- one parentless model-facing Git baseline with the fixed commit inaccessible;
- final-only execution of focused acceptance whose complete behavior and command are model-visible;
- controller-only seed patch files and fixed references, with no undisclosed acceptance assertions;
- cumulative provider usage capture, verifier integrity, isolation, structured verifier diagnostics, and optional source review;
- a machine-validated independent pilot audit with every required incident count equal to zero before any treatment protocol can be frozen, prepared, or run.

A no-model prepare for a frozen candidate is allowed:

```bash
SEQUENCE_ID={prepare_sequence_id}
python3 scripts/run_sequential_workflow_matrix.py "$SEQUENCE_ID" {prepare_model_flags} --prepare-only
```

`prepare-verification.json` must show every task preseeded, only task 1's prompt materialized, a clean true-root Git baseline, no fixed commit object or prior reflog, current composite qualification, no controller seed/verifier files in the model root, and the declared focused acceptance tests visible.

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

`run.json` contains metadata, frozen protocol path/id/SHA-256, baseline pool fingerprint, selected-execution descriptor and hash, immutable Docker image identity, treatment tool adapter identity when applicable, provider usage, composite-seed/concealment claims, operational task checkpoints, and the final verifier result.

`changes.diff` concatenates ordered cumulative source checkpoints and the final diff relative to the one composite broken-start root.

`evidence.jsonl.gz` contains prompts, Codex events, setup logs, cumulative checkpoints, composite-seed and concealment reports, final verifier output and integrity checks, provider-usage extraction, and tool-isolation audit output.

`manifest.sha256` hashes the other three files.

Controller Git objects, generated checkouts, dependency environments, Codex homes, caches, and split task artifacts are scratch state and must not remain beside the compact four files.

## Maintenance contract

- Session IDs and compact evidence are retained once a provider run is operationally valid.
- Deterministic verifier and source-review outcomes are diagnostic model-behavior evidence, not token-accounting gates.
- Reuse the first valid provider sample for each frozen protocol and replicate; never rerun to select for a pass.
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
