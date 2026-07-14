# Workflow Evaluation Runbook

This generated runbook reflects current workflow-sequence readiness.

It is rendered from `data/workflow-task-sequences.json`, `data/repository-fixtures.json`, `data/evaluation-profiles.json`, `data/evaluation-agent-runtimes.json`, and `data/workflow-sessions.json` by `scripts/update_workflow_runbook.py`.

Do not hand-edit execution status here. Update the registries, then run:

```bash
python3 scripts/update_workflow_runbook.py
python3 scripts/validate_repository.py
```

## Evidence boundary

A valid low-complexity workflow pre-seeds every regression and its focused model-visible acceptance test into one qualified composite broken root, then materializes one prompt at a time. Each prompt supplies one exact mechanical old-to-new edit command plus only its focused validation command; Beets uses the locked project environment and Terraform exports the pinned Go toolchain path explicitly. Seed patch files, controller scripts, and fixed parents remain outside the model-visible surface; final verification repeats only the commands and behavior disclosed in each prompt. Product-effect eligibility also requires parity with the pinned official Codex integration and positive treatment-assignment evidence; MCP configuration/listing alone is insufficient.

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
- final-only execution of focused acceptance whose complete behavior and command are model-visible;
- controller-only seed patch files and fixed references, with no undisclosed acceptance assertions;
- cumulative provider usage capture, verifier integrity, isolation, structured verifier diagnostics, and optional source review;
- a machine-validated independent pilot audit with every required incident count equal to zero before any treatment protocol can be frozen, prepared, or run.

A no-model prepare for a frozen candidate is allowed:

```bash
SEQUENCE_ID=fastify-lifecycle-sequence-v0
python3 scripts/run_sequential_workflow_matrix.py "$SEQUENCE_ID" --workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high --prepare-only
```

`prepare-verification.json` must show every task preseeded, only task 1's prompt materialized, a clean true-root Git baseline, no fixed commit object or prior reflog, current composite qualification, no controller seed/verifier files in the model root, and the declared focused acceptance tests visible.

## Paid execution

Current runnable treatment profiles: `artifact-ponytail-codex-plugin-v1`, `behavior-caveman-codex-skill-v1`, `codescope-codex-product-v1`, `headroom-default-codex`, `integrated-leanctx-codex-hybrid-v1`, `integrated-token-savior-codex-product-v2`, `retrieval-cartog-codex-product-v2`, `retrieval-codegraph-codex-mcp-v1`, `retrieval-graphify-codex-skill-v1`, `retrieval-jcodemunch-codex-mcp-v2`, `retrieval-serena-codex-mcp-v1`, `retrieval-sigmap-codex-live-v1`, `swarmvault-codex-product-v1`, `terminal-rtk-codex-instructions-v1`, `terminal-snip-codex-hook-v1`, `terminal-tokenjuice-codex-hook-v1`. Historical profiles marked `historical-profile` are occupied evidence identities and cannot be rerun in place.

Reusable, zero-incident-audited baselines exist for `fastify-lifecycle-sequence-v0` (r0, r1, r2), `beets-lifecycle-sequence-v0` (r0, r1, r3), `terraform-lifecycle-sequence-v0` (r0, r1, r2). No current treatment protocol is frozen, so no paid treatment command is published. Choose one compatible profile, freeze and validate its protocol provider-free, certify the resulting exact tree, and then execute the rendered dry-run verbatim before requesting paid execution:

```bash
SEQUENCE_ID=fastify-lifecycle-sequence-v0
PROFILE_ID=replace-with-compatible-profile-id
python3 scripts/refresh_workflow_contracts.py --sequence-id "$SEQUENCE_ID" --profile-id "$PROFILE_ID" --workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high
python3 scripts/validate_repository.py
python3 scripts/run_sequential_workflow_matrix.py "$SEQUENCE_ID" --treatment-profile "$PROFILE_ID" --workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high --dry-run

SEQUENCE_ID=beets-lifecycle-sequence-v0
PROFILE_ID=replace-with-compatible-profile-id
python3 scripts/refresh_workflow_contracts.py --sequence-id "$SEQUENCE_ID" --profile-id "$PROFILE_ID" --workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high
python3 scripts/validate_repository.py
python3 scripts/run_sequential_workflow_matrix.py "$SEQUENCE_ID" --treatment-profile "$PROFILE_ID" --workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high --dry-run

SEQUENCE_ID=terraform-lifecycle-sequence-v0
PROFILE_ID=replace-with-compatible-profile-id
python3 scripts/refresh_workflow_contracts.py --sequence-id "$SEQUENCE_ID" --profile-id "$PROFILE_ID" --workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high
python3 scripts/validate_repository.py
python3 scripts/run_sequential_workflow_matrix.py "$SEQUENCE_ID" --treatment-profile "$PROFILE_ID" --workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high --dry-run
```

Earlier active-default baseline pools are retained but are not reusable for the current contract generation: `beets-lifecycle-sequence-v0` pool `b440da225a3a` (r0, r1, r2, r3), `fastify-lifecycle-sequence-v0` pool `769d40697529` (r0, r1, r2, r3), `terraform-lifecycle-sequence-v0` pool `ded8609b4172` (r0, r1, r2, r3).

Non-default model-comparison baselines are tracked separately: `beets-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `82943cffbb9a` (r0), `beets-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `8a88427b8c16` (r0), `beets-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `be9d43b94b02` (r0, r1, r2), `fastify-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `bd9fd65385d9` (r0, r1, r2), `fastify-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `e3f3816c31d8` (r0), `terraform-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `5caa11b3fa2b` (r0), `terraform-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `6dbcb1227f80` (r0), `terraform-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `ca21cbff5ed5` (r0, r1, r2). They do not satisfy active-default baseline requirements or define treatment-pair reuse.

Retain the first operationally valid provider sample for each protocol and replicate. Stop only when a sample is fixture-invalid or operationally incomplete; verifier and review outcomes are diagnostic.

## Active sequence details

### `fastify-lifecycle-sequence-v0`

- Fixture: `medium-fastify-fastify`
- Primary metric: cumulative provider-reported workflow tokens
- Reset policy: Reset once before the lane; preseed the missing feature, behavior-preserving structural debt, flawed review candidate, and declared focused acceptance tests into one composite root; preserve repository, Git, tool, index, cache, generated configuration, memory, and agent state across prompts; repeat every disclosed verifier command after the final prompt.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `fastify-lifecycle-feature-v0` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/baseline-v3/fastify-lifecycle-feature-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/baseline-v3/fastify-lifecycle-feature-v0/verify.sh` |
| 2 | `fastify-lifecycle-refactor-v0` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/baseline-v3/fastify-lifecycle-refactor-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/baseline-v3/fastify-lifecycle-refactor-v0/verify.sh` |
| 3 | `fastify-lifecycle-review-v0` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/baseline-v3/fastify-lifecycle-review-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/baseline-v3/fastify-lifecycle-review-v0/verify.sh` |

### `beets-lifecycle-sequence-v0`

- Fixture: `medium-beetbox-beets`
- Primary metric: cumulative provider-reported workflow tokens
- Reset policy: Reset once before the lane; preseed the missing feature, behavior-preserving structural debt, flawed review candidate, and declared focused acceptance tests into one composite root; preserve repository, Git, tool, index, cache, generated configuration, memory, and agent state across prompts; repeat every disclosed verifier command after the final prompt.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `beets-lifecycle-feature-v0` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/baseline-v4/beets-lifecycle-feature-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/baseline-v4/beets-lifecycle-feature-v0/verify.sh` |
| 2 | `beets-lifecycle-refactor-v0` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/baseline-v4/beets-lifecycle-refactor-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/baseline-v4/beets-lifecycle-refactor-v0/verify.sh` |
| 3 | `beets-lifecycle-review-v0` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/baseline-v4/beets-lifecycle-review-v0/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/baseline-v4/beets-lifecycle-review-v0/verify.sh` |

### `terraform-lifecycle-sequence-v0`

- Fixture: `large-hashicorp-terraform`
- Primary metric: cumulative provider-reported workflow tokens
- Reset policy: Reset once before the lane; preseed the missing feature, behavior-preserving structural debt, flawed review candidate, and declared focused acceptance tests into one composite root; preserve repository, Git, tool, index, cache, generated configuration, memory, and agent state across prompts; repeat every disclosed verifier command after the final prompt.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `terraform-lifecycle-feature-v0` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/baseline-v4/terraform-lifecycle-feature-v0/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/baseline-v4/terraform-lifecycle-feature-v0/verify.sh` |
| 2 | `terraform-lifecycle-refactor-v0` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/baseline-v4/terraform-lifecycle-refactor-v0/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/baseline-v4/terraform-lifecycle-refactor-v0/verify.sh` |
| 3 | `terraform-lifecycle-review-v0` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/baseline-v4/terraform-lifecycle-review-v0/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/baseline-v4/terraform-lifecycle-review-v0/verify.sh` |

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
