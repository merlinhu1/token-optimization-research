# Workflow Evaluation Runbook

This generated runbook reflects current workflow-sequence readiness.

It is rendered from `data/workflow-task-sequences.json`, `data/repository-fixtures.json`, `data/evaluation-profiles.json`, `data/evaluation-agent-runtimes.json`, and `data/workflow-sessions.json` by `scripts/update_workflow_runbook.py`.

Do not hand-edit execution status here. Update the registries, then run:

```bash
python3 scripts/update_workflow_runbook.py
python3 scripts/validate_repository.py
```

## Evidence boundary

A valid workflow run pre-seeds every regression into one qualified composite broken root, then materializes one prompt at a time. Seed patches, task fixtures, verifier assets, controller Git objects, and fixed parents remain outside the model-visible surface; hidden functional verification runs only after all prompts complete. Product-effect eligibility also requires parity with the pinned official Codex integration and positive treatment-assignment evidence; MCP configuration/listing alone is insufficient.

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
- cumulative provider usage capture, verifier integrity, isolation, structured verifier diagnostics, and optional source review.

A no-model prepare for a frozen candidate is allowed:

```bash
SEQUENCE_ID=<frozen-sequence-id>
python3 scripts/run_sequential_workflow_matrix.py --prepare-only "$SEQUENCE_ID"
```

`prepare-verification.json` must show every task preseeded, only task 1's prompt materialized, a clean true-root Git baseline, no fixed commit object or prior reflog, current composite qualification, and no model-visible seed or verifier assets.

## Paid execution

Current runnable treatment profiles: `artifact-ponytail`, `behavior-caveman`, `codescope-codex-product-v1`, `headroom-default-codex`, `integrated-leanctx-codex-hybrid-v1`, `integrated-token-savior-mcp-v1`, `retrieval-cartog-mcp-v1`, `retrieval-codegraph-codex-mcp-v1`, `retrieval-graphify-codex-skill-v1`, `retrieval-jcodemunch-mcp-direct-v1`, `retrieval-serena-codex-mcp-v1`, `retrieval-sigmap-codex-live-v1`, `swarmvault-codex-product-v1`, `terminal-rtk-codex-instructions-v1`, `terminal-snip-codex-hook-v1`, `terminal-tokenjuice-codex-hook-v1`. Historical profiles marked `historical-profile` are occupied evidence identities and cannot be rerun in place.

Reusable baselines already exist for `fastify-lifecycle-sequence-v0` (r0, r1, r2), `beets-lifecycle-sequence-v0` (r0, r1, r2), `terraform-lifecycle-sequence-v0` (r0, r1, r2). Do not rerun them. Choose one compatible treatment profile and one intended lane:

```bash
SEQUENCE_ID=replace-with-one-active-sequence-id
PROFILE_ID=replace-with-compatible-profile-id
python3 scripts/run_sequential_workflow_matrix.py "$SEQUENCE_ID" --treatment-profile "$PROFILE_ID"
```

Non-default model-comparison baselines are tracked separately: `beets-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` (r0, r1), `fastify-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` (r0, r1), `terraform-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` (r0, r1). They do not satisfy active-default baseline requirements or define treatment-pair reuse.

Retain the first operationally valid provider sample for each protocol and replicate. Stop only when a sample is fixture-invalid or operationally incomplete; verifier and review outcomes are diagnostic.

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

- Session IDs and compact evidence are retained once a provider run is operationally valid.
- Deterministic verifier and source-review outcomes are diagnostic model-behavior evidence, not token-accounting gates.
- Reuse the first valid provider sample for each frozen protocol and replicate; never rerun to select for a pass.
- `python3 scripts/validate_repository.py` checks generated-runbook drift.
- Truth docs own durable claims; this runbook is generated operator procedure.
