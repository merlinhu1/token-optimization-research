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
5. **Treatment identity**: profile, enabled surfaces, pinned tool-author installation guide, every author-recommended host surface (including product-authored guidance/rules/skills/hooks), adapter command, binary/config hashes, isolation policy, and reset path. Evaluator-authored treatment-tool steering is forbidden, but reduced or guidance-free setups must be named as ablations rather than canonical product treatments.
6. **Task assistance**: Active Lifecycle V1 prompts state complete software-engineering objectives, expect correct implementation, permit normal repository search/inspection and relevant validation, and do not disclose controller scoring or compile commands. Freeze identical prompt bytes across compatible baseline and treatment sessions; prompts must not require or prefer treatment-tool invocation. Historical Solution-directed task assistance remains valid only for its executed frozen V2/V3/V4 protocols.
7. **Token boundary**: complete provider-reported persistent workflow usage; capture fresh input, cached input, cache-write, output, reasoning, and total when available.
8. **Operational validity**: complete execution, thread continuity, warning-free usage, fixture/contract validity, verifier integrity, tool isolation, and compact-artifact integrity.
9. **Acceptance and diagnostics**: Lifecycle V1 affected-component and final project-wide compile outcomes gate task/workflow acceptance and treatment unlock. Unit tests, behavior, style, exact source shape, changed-area review, and optional source review are diagnostics; they do not gate token accounting or trigger reruns.
10. **Invalidity rules**: fixture defects, protocol mismatch, incomplete provider usage, broken isolation, corrupted evidence, or interrupted execution.

## Current surfaces

- `data/workflow-task-sequences.json`
- `data/workflow-sessions.json`
- `docs/evaluations/operations/runbook.md`
- `templates/evaluation-protocol.md`
- `docs/evaluations/design/token-and-quality-policy.md`
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
- Stripping tool-author-provided guidance in the name of neutrality; faithful canonical installation includes it, while evaluator-authored steering remains forbidden.
- Combining samples across a harness, fixture, isolation, or causal protocol change.
