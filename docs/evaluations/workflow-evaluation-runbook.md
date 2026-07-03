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
| `fastify-lifecycle-sequence-v0` | `medium-fastify-fastify` | medium-project | [`94bcbcc6e2ef`](https://github.com/fastify/fastify.git) | 3 |
| `beets-lifecycle-sequence-v0` | `medium-beetbox-beets` | medium-project | [`9acb1ecff6c7`](https://github.com/beetbox/beets.git) | 3 |
| `terraform-lifecycle-sequence-v0` | `large-hashicorp-terraform` | large-project | [`e02391ad384c`](https://github.com/hashicorp/terraform.git) | 3 |

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

Freeze one protocol per active lane, run no-model preparation for all current production lanes, then run each canonical baseline:

```bash
python3 scripts/run_sequential_workflow_matrix.py fastify-lifecycle-sequence-v0 --prepare-only
python3 scripts/run_sequential_workflow_matrix.py beets-lifecycle-sequence-v0 --prepare-only
python3 scripts/run_sequential_workflow_matrix.py terraform-lifecycle-sequence-v0 --prepare-only
python3 scripts/run_sequential_workflow_matrix.py fastify-lifecycle-sequence-v0
python3 scripts/run_sequential_workflow_matrix.py beets-lifecycle-sequence-v0
python3 scripts/run_sequential_workflow_matrix.py terraform-lifecycle-sequence-v0
```

After a lane has a reviewed reusable baseline, launch its matched treatment with `python3 scripts/run_sequential_workflow_matrix.py <sequence-id> --treatment-profile <profile-id>`. Stop before treatment if that lane's baseline fails any frozen gate.

## Active sequence details

### `fastify-lifecycle-sequence-v0`

- Fixture: `medium-fastify-fastify`
- Primary metric: cumulative provider-reported workflow tokens
- Reset policy: Reset once before the lane; preseed the missing feature, behavior-preserving structural debt, and flawed review candidate into one concealed composite root; preserve repository, Git, tool, index, cache, generated configuration, memory, and agent state across prompts; run every concealed verifier after the final prompt.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `fastify-lifecycle-feature-v0` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-lifecycle-feature-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-lifecycle-feature-v0/verify.sh` |
| 2 | `fastify-lifecycle-refactor-v0` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-lifecycle-refactor-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-lifecycle-refactor-v0/verify.sh` |
| 3 | `fastify-lifecycle-review-v0` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-lifecycle-review-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-lifecycle-review-v0/verify.sh` |

### `beets-lifecycle-sequence-v0`

- Fixture: `medium-beetbox-beets`
- Primary metric: cumulative provider-reported workflow tokens
- Reset policy: Reset once before the lane; preseed the missing feature, behavior-preserving structural debt, and flawed review candidate into one concealed composite root; preserve repository, Git, tool, index, cache, generated configuration, memory, and agent state across prompts; run every concealed verifier after the final prompt.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `beets-lifecycle-feature-v0` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-feature-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-feature-v0/verify.sh` |
| 2 | `beets-lifecycle-refactor-v0` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-refactor-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-refactor-v0/verify.sh` |
| 3 | `beets-lifecycle-review-v0` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-review-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-lifecycle-review-v0/verify.sh` |

### `terraform-lifecycle-sequence-v0`

- Fixture: `large-hashicorp-terraform`
- Primary metric: cumulative provider-reported workflow tokens
- Reset policy: Reset once before the lane; preseed the missing feature, behavior-preserving structural debt, and flawed review candidate into one concealed composite root; preserve repository, Git, tool, index, cache, generated configuration, memory, and agent state across prompts; run every concealed verifier after the final prompt.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `terraform-lifecycle-feature-v0` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-lifecycle-feature-v0/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-lifecycle-feature-v0/verify.sh` |
| 2 | `terraform-lifecycle-refactor-v0` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-lifecycle-refactor-v0/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-lifecycle-refactor-v0/verify.sh` |
| 3 | `terraform-lifecycle-review-v0` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-lifecycle-review-v0/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-lifecycle-review-v0/verify.sh` |

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
