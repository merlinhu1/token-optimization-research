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
| `fastify-maintenance-sequence-v1` | `medium-fastify-fastify` | medium-project | [`94bcbcc6e2ef`](https://github.com/fastify/fastify.git) | 5 |
| `terraform-maintenance-sequence-v2` | `large-hashicorp-terraform` | large-project | [`e02391ad384c`](https://github.com/hashicorp/terraform.git) | 3 |
| `beets-maintenance-sequence-v4` | `medium-beetbox-beets` | medium-project | [`8ddae794d30e`](https://github.com/beetbox/beets.git) | 3 |

## Planned candidates and blockers

_None._

## Activation gate

Before changing a sequence to `active`, require:

- at least five causally related production files per primary task, or explicit smoke/calibration scope;
- behavioral seeded-fail/fixed-pass gates;
- a conflict-free composite seed whose task verifiers all fail at lane start;
- one parentless model-facing Git baseline with the fixed commit inaccessible;
- final-only concealed functional verification with no per-task controller gate;
- controller-only task, seed, verifier, and reference assets;
- cumulative provider usage capture, verifier integrity, isolation, and software-quality review.

A no-model prepare for a planned candidate is allowed:

```bash
SEQUENCE_ID=<planned-sequence-id>
python3 scripts/run_codex_workflow_evaluation.py   --sequence-id "$SEQUENCE_ID"   --profile-id baseline-bare-codex   --prepare-only   --skip-container-preflight   --skip-codex-preflight   --skip-dependency-install
```

`prepare-verification.json` must show every task preseeded, only task 1's prompt materialized, a clean true-root Git baseline, no fixed commit object or prior reflog, current composite qualification, and no model-visible seed or verifier assets.

## Paid execution

The active sequence list is non-empty. Freeze a protocol, run a no-model prepare, then run the canonical baseline first:

```bash
python3 scripts/run_sequential_workflow_matrix.py fastify-maintenance-sequence-v1 --prepare-only
python3 scripts/run_sequential_workflow_matrix.py fastify-maintenance-sequence-v1 --treatment-profile <profile-id>
```

Stop before treatment if the baseline fails any frozen gate.

## Active sequence details

### `fastify-maintenance-sequence-v1`

- Fixture: `medium-fastify-fastify`
- Primary metric: cumulative provider-billed workflow tokens
- Reset policy: Reset once before the lane; preseed all regressions into one concealed composite root; preserve source, Git, tool, index, cache, generated config, memory, and agent state across prompts; run concealed functional verification once at the end.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `fastify-max-param-length-regression` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-max-param-length-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-max-param-length-regression/verify.sh` |
| 2 | `fastify-handler-timeout-regression` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-handler-timeout-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-handler-timeout-regression/verify.sh` |
| 3 | `fastify-request-media-type-regression` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-request-media-type-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-request-media-type-regression/verify.sh` |
| 4 | `fastify-log-controller-regression` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-log-controller-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-log-controller-regression/verify.sh` |
| 5 | `fastify-content-type-semantics-regression` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-content-type-semantics-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-content-type-semantics-regression/verify.sh` |

### `terraform-maintenance-sequence-v2`

- Fixture: `large-hashicorp-terraform`
- Primary metric: cumulative provider-billed workflow tokens
- Reset policy: Reset once before the lane; preseed all regressions into one concealed composite root; preserve source, Git, tool, index, cache, generated config, memory, and agent state across prompts; run concealed functional verification once at the end.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `terraform-161ffe-tracing-context-regression` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-161ffe-tracing-context-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-161ffe-tracing-context-regression/verify.sh` |
| 2 | `terraform-520378-computed-block-capabilities-regression` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-520378-computed-block-capabilities-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-520378-computed-block-capabilities-regression/verify.sh` |
| 3 | `terraform-9ae470-objchange-validation-regression` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-9ae470-objchange-validation-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-9ae470-objchange-validation-regression/verify.sh` |

### `beets-maintenance-sequence-v4`

- Fixture: `medium-beetbox-beets`
- Primary metric: cumulative provider-billed workflow tokens
- Reset policy: Reset once before the lane; preseed all regressions into one concealed composite root; preserve source, Git, tool, index, cache, generated config, memory, and agent state across prompts; run concealed functional verification once at the end.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `beets-path-format-core-regression` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-path-format-core-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-path-format-core-regression/verify.sh` |
| 2 | `beets-multivalue-core-regression` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-multivalue-core-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-multivalue-core-regression/verify.sh` |
| 3 | `beets-tidal-metadata-sync-regression` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-tidal-metadata-sync-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-tidal-metadata-sync-regression/verify.sh` |

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
