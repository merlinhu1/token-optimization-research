# Workflow Evaluation Runbook

This generated runbook reflects current workflow-sequence readiness.

It is rendered from `data/workflow-task-sequences.json` and `data/repository-fixtures.json` by `scripts/update_workflow_runbook.py`.

Do not hand-edit sequence status here. Update the registries, then run:

```bash
python3 scripts/update_workflow_runbook.py
python3 scripts/validate_repository.py
```

## Evidence boundary

A valid workflow run pre-seeds every regression into one qualified composite broken root, then materializes one prompt at a time. Seed patches, task fixtures, verifier assets, controller Git objects, and fixed parents remain outside the model-visible surface; hidden functional verification runs only after all prompts complete.

Every active task must use causally related behavioral acceptance. Unrelated exact-source restoration guards are not valid complexity.

## Active sequences

| Sequence | Fixture | Scale | Snapshot | Tasks |
|---|---|---|---|---:|
| `beets-lifecycle-sequence-v2` | `medium-beetbox-beets` | medium-project | [`9acb1ecff6c7`](https://github.com/beetbox/beets.git) | 3 |

## Planned candidates and blockers

_None._

## Activation gate

Before changing a sequence to `active`, require:

- the smallest causally related production surface that satisfies explicit semantic acceptance, with no arbitrary changed-file minimum;
- behavioral seeded-fail/fixed-pass gates;
- a conflict-free composite seed whose task verifiers all fail at lane start;
- one parentless model-facing Git baseline with the fixed commit inaccessible;
- final-only concealed functional verification with no per-task controller gate;
- controller-only task, seed, verifier, and reference assets;
- cumulative provider usage capture, verifier integrity, isolation, and software-quality review.

A no-model prepare for a frozen candidate is allowed:

```bash
SEQUENCE_ID=<frozen-sequence-id>
python3 scripts/run_sequential_workflow_matrix.py --prepare-only "$SEQUENCE_ID"
```

`prepare-verification.json` must show every task preseeded, only task 1's prompt materialized, a clean true-root Git baseline, no fixed commit object or prior reflog, current composite qualification, and no model-visible seed or verifier assets.

## Paid execution

The active sequence list is non-empty. Freeze a protocol, run a no-model prepare, then run the canonical baseline first:

```bash
python3 scripts/run_sequential_workflow_matrix.py beets-lifecycle-sequence-v2 --prepare-only
python3 scripts/run_sequential_workflow_matrix.py beets-lifecycle-sequence-v2 --treatment-profile <profile-id>
```

Stop before treatment if the baseline fails any frozen gate.

## Active sequence details

### `beets-lifecycle-sequence-v2`

- Fixture: `medium-beetbox-beets`
- Primary metric: cumulative provider-reported workflow tokens
- Reset policy: Reset once before the lane; preseed the missing feature, the pre-refactor lazy storage implementation, and the authentic flawed review revision into one concealed composite root; preserve repository and agent state across prompts; run every concealed verifier after the final prompt.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `beets-lifecycle-multivalue-modify-feature-v2` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-multivalue-modify-feature-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-multivalue-modify-feature-v2/verify.sh` |
| 2 | `beets-lifecycle-lazy-model-storage-refactor-v2` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-lazy-model-storage-refactor-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-lazy-model-storage-refactor-v2/verify.sh` |
| 3 | `beets-lifecycle-ftintitle-review-v2` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-ftintitle-review-v2/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-ftintitle-review-v2/verify.sh` |

## Artifact contract

Each completed session keeps exactly four files:

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json
  changes.diff
  evidence.jsonl.gz
  manifest.sha256
```

`run.json` contains metadata, frozen protocol path/id/SHA-256, baseline pool fingerprint, selected-execution descriptor and hash, immutable Docker image identity, treatment tool adapter identity when applicable, provider usage, composite-seed/concealment claims, operational task checkpoints, and the final verifier result.

`changes.diff` concatenates ordered cumulative source checkpoints and the final diff relative to the one composite broken-start root.

`evidence.jsonl.gz` contains prompts, Codex events, setup logs, cumulative checkpoints, composite-seed and concealment reports, final verifier output and integrity checks, provider-usage extraction, and tool-isolation audit output.

`manifest.sha256` hashes the other three files.

Controller Git objects, generated checkouts, dependency environments, Codex homes, caches, and split task artifacts are scratch state and must not remain beside the compact four files.

## Maintenance contract

- Session IDs and compact evidence are append-only.
- Deterministic verifier success is an execution gate, not an automatic software-quality score.
- Objective acceptance requires a recorded software-quality review.
- `python3 scripts/validate_repository.py` checks generated-runbook drift.
- Truth docs own durable claims; this runbook is generated operator procedure.
