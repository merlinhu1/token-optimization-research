---
name: benchmark-protocol-writer
description: Use before a lifecycle-v0 baseline or treatment run to freeze the token estimand, compatible execution condition, integrity controls, diagnostics, and compact artifacts.
---
# Benchmark Protocol Writer

## Purpose

Freeze the causal execution contract before provider use. The protocol prevents metric drift while keeping token-accounting eligibility separate from model-behavior diagnostics.

## Required protocol

Define:

1. **Hypothesis**: profile X changes cumulative provider tokens for frozen workflow Z.
2. **Evidence target**: `benchmark-audit` or `reproduction`.
3. **Lifecycle sequence**: sequence ID, pinned fixture/snapshot, ordered prompts, state policy, and time budget.
4. **Compatible baseline pool**: protocol fingerprint, model/provider condition, replicate index, and retained baseline session when one exists.
5. **Treatment identity**: profile, enabled surfaces, adapter command, binary/config hashes, isolation policy, and reset path.
6. **Token boundary**: complete provider-reported persistent workflow usage; capture fresh input, cached input, cache-write, output, reasoning, and total when available.
7. **Operational validity**: complete execution, thread continuity, warning-free usage, fixture/contract validity, verifier integrity, tool isolation, and compact-artifact integrity.
8. **Model-behavior diagnostics**: deterministic verifier outcomes, changed-area checks, optional source review, and critical findings. These fields do not gate token accounting or trigger reruns.
9. **Invalidity rules**: fixture defects, protocol mismatch, incomplete provider usage, broken isolation, corrupted evidence, or interrupted execution.

## Current surfaces

- `data/workflow-task-sequences.json`
- `data/workflow-sessions.json`
- `docs/evaluations/workflow-evaluation-runbook.md`
- `docs/evaluations/technique-protocol-template.md`
- `docs/evaluations/token-usage-and-quality-standards.md`
- `sources/evaluations/protocols/`
- `sources/evaluations/workflow-sessions/`

Use `scripts/run_sequential_workflow_matrix.py`. Never route lifecycle-v0 results through the older `data/evaluations.json` artifact model.

## After a run

Follow the `AGENTS.md` documentation lifecycle. Update authoritative registries, regenerate the runbook, reconcile active findings/status docs and prompts, delete superseded surfaces, validate, and inspect Git status for missing tests or untracked evidence.

## Pitfalls

- Running a treatment before freezing its compatible comparison identity.
- Rerunning an occupied protocol/replicate to obtain better verifier or review outcomes.
- Conditioning the primary token result on correctness diagnostics.
- Changing prompts or fixtures between paired sessions.
- Reporting prompt estimates instead of complete provider usage.
- Treating runner PATH preflight as proof that the model-visible environment can use a treatment tool.
- Combining samples across a harness, fixture, isolation, or causal protocol change.
