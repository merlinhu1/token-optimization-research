# Workflow Evaluation Runbook

This generated runbook reflects current workflow-sequence readiness.

It is rendered from `data/workflow-task-sequences.json`, `data/repository-fixtures.json`, `data/evaluation-profiles.json`, `data/evaluation-agent-runtimes.json`, and `data/workflow-sessions.json` by `scripts/update_workflow_runbook.py`.

Do not hand-edit execution status here. Update the registries, then run:

```bash
python3 scripts/update_workflow_runbook.py
python3 scripts/validate_repository.py
```

## Evidence boundary

A valid Lifecycle V1 workflow pre-seeds three authentic semantic regressions from completed upstream behavior into one qualified composite start, then materializes one normal software-engineering prompt at a time. Each prompt states the requested outcome, permits repository search and related-code inspection, and expects a complete correct implementation without disclosing evaluator scoring or controller commands. Beets uses the locked project environment and Terraform binds the snapshot-required Go toolchain explicitly. Seed patch files, controller scripts, fixed parents, affected-component compile commands, and the final project-wide compile command remain outside the model-visible surface. Product-effect eligibility also requires parity with the pinned official integration and positive treatment-assignment evidence; configuration/listing alone is insufficient.

Internally, every active task uses compilation-only acceptance. Unit tests, behavioral fidelity, style, maintainability, and source review remain diagnostic and do not determine evaluator pass/fail. This internal policy must never be presented as an agent instruction.

## Active sequences

| Sequence | Fixture | Scale | Snapshot | Tasks |
|---|---|---|---|---:|
| `fastify-lifecycle-sequence-v1` | `medium-fastify-fastify` | medium-project | [`94bcbcc6e2ef`](https://github.com/fastify/fastify.git) | 3 |
| `beets-lifecycle-sequence-v1` | `medium-beetbox-beets` | medium-project | [`9acb1ecff6c7`](https://github.com/beetbox/beets.git) | 3 |
| `terraform-lifecycle-sequence-v1` | `large-hashicorp-terraform` | large-project | [`e02391ad384c`](https://github.com/hashicorp/terraform.git) | 3 |

## Planned candidates and blockers

_None._

## Activation gate

Before changing a sequence to `active`, require:

- one or two semantic production targets per task, restored to completed upstream behavior;
- standalone seed application and repair round-trips, with seeded compiler outcomes limited to 0 or 1 and repaired compilation succeeding;
- a conflict-free composite semantic seed whose controller compile outcomes are all 0 or 1 at lane start;
- one parentless model-facing Git baseline with the fixed commit inaccessible;
- prompts that state complete software objectives, permit repository discovery, and withhold controller scoring;
- no model-visible compile commands or injected acceptance-test assets;
- controller-only affected-component compile commands plus one frozen project-wide compile command;
- controller-only seed patch files and fixed references;
- cumulative provider usage capture, verifier integrity, isolation, structured compile outcomes, and optional quality diagnostics;
- a machine-validated compile-passing provider pilot before any treatment protocol can be frozen, prepared, or run.

A no-model prepare for a frozen candidate is allowed:

```bash
SEQUENCE_ID=fastify-lifecycle-sequence-v1
python3 scripts/run_sequential_workflow_matrix.py "$SEQUENCE_ID" --workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high --prepare-only
```

`prepare-verification.json` must show every task preseeded, only task 1's prompt materialized, a clean true-root Git baseline, no fixed commit object or prior reflog, current composite qualification including recorded seeded compiler outcomes and passing repaired/project-wide compilation boundaries, no controller seed/verifier files in the model root, no injected acceptance-test assets, and no controller compile command or scoring-policy disclosure in the current task prompt.

## Paid execution

Current runnable treatment profiles: `artifact-ponytail-codex-plugin-v1`, `behavior-caveman-codex-skill-v1`, `codescope-codex-product-v1`, `headroom-default-codex`, `integrated-leanctx-codex-hybrid-v1`, `integrated-token-savior-codex-product-v2`, `retrieval-cartog-codex-product-v2`, `retrieval-codegraph-codex-mcp-v1`, `retrieval-graphify-codex-skill-v1`, `retrieval-jcodemunch-codex-mcp-v2`, `retrieval-serena-codex-mcp-v1`, `retrieval-sigmap-codex-live-v1`, `swarmvault-codex-product-v1`, `terminal-rtk-claude-code-hook-v1`, `terminal-rtk-codex-instructions-v1`, `terminal-snip-codex-hook-v1`, `terminal-tokenjuice-codex-hook-v1`. Historical profiles marked `historical-profile` are occupied evidence identities and cannot be rerun in place.

Treatment protocol freezing, preparation, and execution are machine-blocked for `fastify-lifecycle-sequence-v1` (pilot audit is absent: sources/evaluations/audits/lifecycle-v1-pilot-compile-only.json), `beets-lifecycle-sequence-v1` (pilot audit is absent: sources/evaluations/audits/lifecycle-v1-pilot-compile-only.json), `terraform-lifecycle-sequence-v1` (pilot audit is absent: sources/evaluations/audits/lifecycle-v1-pilot-compile-only.json). Paid pilot execution is not authorized for `fastify-lifecycle-sequence-v1`, `beets-lifecycle-sequence-v1`, `terraform-lifecycle-sequence-v1`; provider-capable commands are suppressed until the explicit authorization authority is updated.

Provider-free preparation remains available for lanes without a reusable operational baseline; paid commands are listed only for unoccupied pilot identities:

```bash
python3 scripts/run_sequential_workflow_matrix.py fastify-lifecycle-sequence-v1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high --prepare-only
python3 scripts/run_sequential_workflow_matrix.py beets-lifecycle-sequence-v1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high --prepare-only
python3 scripts/run_sequential_workflow_matrix.py terraform-lifecycle-sequence-v1 --workflow-model-condition-id codex-openai-gpt-5-6-sol-high --workflow-model gpt-5.6-sol --workflow-reasoning-effort high --prepare-only
```

Earlier active-default baseline pools are retained but are not reusable for the current contract generation: `beets-lifecycle-sequence-v0` pool `b440da225a3a` (r0, r1, r2, r3), `fastify-lifecycle-sequence-v0` pool `769d40697529` (r0, r1, r2, r3), `terraform-lifecycle-sequence-v0` pool `ded8609b4172` (r0, r1, r2, r3).

Non-default model-comparison baselines are tracked separately: `beets-lifecycle-sequence-v0` under `claude-code-openrouter-gpt-5-6-sol-high` pool `2fd6c85014dc` (r0), `beets-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `82943cffbb9a` (r0), `beets-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `8a88427b8c16` (r0), `beets-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `be9d43b94b02` (r0, r1, r2), `beets-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `fcc8438d2077` (r0, r1, r3), `fastify-lifecycle-sequence-v0` under `claude-code-openrouter-gpt-5-6-sol-high` pool `2e0426814326` (r0), `fastify-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `bb0e89ed9794` (r0, r1, r2), `fastify-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `bd9fd65385d9` (r0, r1, r2), `fastify-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `e3f3816c31d8` (r0), `terraform-lifecycle-sequence-v0` under `claude-code-openrouter-gpt-5-6-sol-high` pool `938e4812b1d4` (r0), `terraform-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `5811b463c1e9` (r0, r1, r2), `terraform-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `5caa11b3fa2b` (r0), `terraform-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `6dbcb1227f80` (r0), `terraform-lifecycle-sequence-v0` under `codex-openai-gpt-5-6-sol-high` pool `ca21cbff5ed5` (r0, r1, r2). They do not satisfy active-default baseline requirements or define active-default treatment-pair reuse. OpenCode pools may define substrate-matched treatment reuse under their own frozen protocols.

Retain the first operationally valid provider sample for each protocol and replicate. Stop only when a sample is fixture-invalid or operationally incomplete; verifier and review outcomes are diagnostic.

## Active sequence details

### `fastify-lifecycle-sequence-v1`

- Fixture: `medium-fastify-fastify`
- Primary metric: cumulative provider-reported workflow tokens
- Reset policy: Each task reset reverses only its generation-local semantic production regression. No acceptance tests are injected. A controller-only affected-component compile command determines evaluator pass/fail and is not disclosed as the agent task objective.
- Final project compile: `find lib -type f -name '*.js' -print0 | sort -z | xargs -0 -n1 node --check && node --check fastify.js`

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `fastify-lifecycle-feature-v1` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v1/fastify-lifecycle-feature-v1/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v1/fastify-lifecycle-feature-v1/verify.sh` |
| 2 | `fastify-lifecycle-refactor-v1` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v1/fastify-lifecycle-refactor-v1/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v1/fastify-lifecycle-refactor-v1/verify.sh` |
| 3 | `fastify-lifecycle-review-v1` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v1/fastify-lifecycle-review-v1/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/task-generations/lifecycle-v1/fastify-lifecycle-review-v1/verify.sh` |

### `beets-lifecycle-sequence-v1`

- Fixture: `medium-beetbox-beets`
- Primary metric: cumulative provider-reported workflow tokens
- Reset policy: Each task reset reverses only its generation-local semantic production regression. No acceptance tests are injected. A controller-only affected-component compile command determines evaluator pass/fail and is not disclosed as the agent task objective.
- Final project compile: `uv run --offline --frozen python -c "import ast, pathlib; [ast.parse(p.read_text(), filename=str(p)) for root in ('beets', 'beetsplug') for p in pathlib.Path(root).rglob('*.py')]"`

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `beets-lifecycle-feature-v1` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v1/beets-lifecycle-feature-v1/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v1/beets-lifecycle-feature-v1/verify.sh` |
| 2 | `beets-lifecycle-refactor-v1` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v1/beets-lifecycle-refactor-v1/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v1/beets-lifecycle-refactor-v1/verify.sh` |
| 3 | `beets-lifecycle-review-v1` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v1/beets-lifecycle-review-v1/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/task-generations/lifecycle-v1/beets-lifecycle-review-v1/verify.sh` |

### `terraform-lifecycle-sequence-v1`

- Fixture: `large-hashicorp-terraform`
- Primary metric: cumulative provider-reported workflow tokens
- Reset policy: Each task reset reverses only its generation-local semantic production regression. No acceptance tests are injected. A controller-only affected-component compile command determines evaluator pass/fail and is not disclosed as the agent task objective.
- Final project compile: `export PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH; GOTOOLCHAIN=auto go test -run '^$' ./...`

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `terraform-lifecycle-feature-v1` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/lifecycle-v1/terraform-lifecycle-feature-v1/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/lifecycle-v1/terraform-lifecycle-feature-v1/verify.sh` |
| 2 | `terraform-lifecycle-refactor-v1` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/lifecycle-v1/terraform-lifecycle-refactor-v1/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/lifecycle-v1/terraform-lifecycle-refactor-v1/verify.sh` |
| 3 | `terraform-lifecycle-review-v1` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/lifecycle-v1/terraform-lifecycle-review-v1/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/task-generations/lifecycle-v1/terraform-lifecycle-review-v1/verify.sh` |

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
