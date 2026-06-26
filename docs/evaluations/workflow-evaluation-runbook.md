# Workflow Evaluation Runbook

This is the maintained human-facing runbook for the active four-workflow evaluation matrix.

It is rendered from `data/workflow-task-sequences.json` and `data/repository-fixtures.json` by `scripts/update_workflow_runbook.py`.

Do not hand-edit active sequence tables in this file; update the machine registries first, then run:

```bash
python3 scripts/update_workflow_runbook.py
python3 scripts/validate_repository.py
```

## Canonical sources

- Active sequences: `data/workflow-task-sequences.json`
- Fixture contracts: `data/repository-fixtures.json`
- Completed sessions: `data/workflow-sessions.json`
- Single-sequence runner: `scripts/run_codex_workflow_evaluation.py`
- Matrix runner: `scripts/run_sequential_workflow_matrix.py`
- Artifact contract: `templates/workflow-session-record.json`

## Evidence boundary

The primary evidence path is continuous workflow simulation.

Single-task isolated runs and tiny calibration fixtures are not the default matrix and do not support positive workflow-level claims.

A positive reproduction claim needs paired baseline and treatment sessions on the same sequence, runtime, provider, model condition, prompt-disclosure policy, and verifier set.

## Active four-workflow matrix

| Sequence | Fixture | Scale | Snapshot | Tasks |
|---|---|---|---|---:|
| `terraform-maintenance-sequence-v1` | `large-hashicorp-terraform` | large-project | [`e02391ad384c`](https://github.com/hashicorp/terraform.git) | 5 |
| `orchardcore-maintenance-sequence-v1` | `large-orchardcms-orchardcore` | large-project | [`91cd8a4bfcaf`](https://github.com/OrchardCMS/OrchardCore.git) | 5 |
| `fastify-maintenance-sequence-v1` | `medium-fastify-fastify` | medium-project | [`94bcbcc6e2ef`](https://github.com/fastify/fastify.git) | 5 |
| `beets-maintenance-sequence-v1` | `medium-beetbox-beets` | medium-project | [`8ddae794d30e`](https://github.com/beetbox/beets.git) | 5 |

## Running a smoke prepare

Use `--prepare-only` to verify fixture construction, task prompt sanitization, and seed-origin concealment without spending model tokens.

```bash
python3 scripts/run_codex_workflow_evaluation.py \
  --sequence-id terraform-maintenance-sequence-v1 \
  --profile-id baseline-bare-codex \
  --prepare-only \
  --skip-container-preflight \
  --skip-codex-preflight \
  --skip-dependency-install \
  --session-id smoke-terraform-sequential-runner

rm -rf sources/evaluations/workflow-sessions/smoke-terraform-sequential-runner
```

Expected smoke properties:

- The generated task prompt for order 1 contains task 1 only.
- Future task prompts are not visible before their turn.
- The materialized repository has no upstream remote that reveals the fix.
- The visible baseline commit is the workflow broken-start state.

## Running one lane

Baseline lane:

```bash
python3 scripts/run_codex_workflow_evaluation.py \
  --sequence-id terraform-maintenance-sequence-v1 \
  --profile-id baseline-bare-codex \
  --timeout-per-task 1800
```

Treatment lane:

```bash
python3 scripts/run_codex_workflow_evaluation.py \
  --sequence-id terraform-maintenance-sequence-v1 \
  --profile-id retrieval-leanctx \
  --timeout-per-task 1800
```

## Running paired lanes

Run the paired baseline plus LeanCTX lanes for one sequence:

```bash
scripts/run_sequential_workflow_pair.sh terraform-maintenance-sequence-v1
```

Use a different replicate or timeout when needed:

```bash
REPLICATE_INDEX=1 scripts/run_sequential_workflow_pair.sh \
  beets-maintenance-sequence-v1 \
  --timeout-per-task 2400
```

## Running the active matrix

Dry-run the matrix plan:

```bash
scripts/run_sequential_workflow_matrix.py --dry-run
```

Run all active flows with the conservative default concurrency:

```bash
scripts/run_sequential_workflow_matrix.py
```

Run all four active flows concurrently only when provider quota and host resources allow it:

```bash
scripts/run_sequential_workflow_matrix.py --max-parallel 4
```

Smoke two flows without model spend:

```bash
scripts/run_sequential_workflow_matrix.py \
  terraform-maintenance-sequence-v1 \
  fastify-maintenance-sequence-v1 \
  --max-parallel 2 \
  --prepare-only \
  --skip-container-preflight \
  --skip-codex-preflight \
  --skip-dependency-install
```

## Active sequence details

### `terraform-maintenance-sequence-v1`

- Fixture: `large-hashicorp-terraform`
- Primary metric: cumulative provider-billed workflow tokens
- Reset policy: Reset once before the session; preserve repository, tool, index, cache, generated config, memory, and agent state between tasks.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `terraform-38739-sensitive-policy-paths-regression` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-38739-sensitive-policy-paths-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-38739-sensitive-policy-paths-regression/verify.sh` |
| 2 | `terraform-38745-config-parser-concurrency-regression` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-38745-config-parser-concurrency-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-38745-config-parser-concurrency-regression/verify.sh` |
| 3 | `terraform-38747-config-loader-watchstop-race-regression` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-38747-config-loader-watchstop-race-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-38747-config-loader-watchstop-race-regression/verify.sh` |
| 4 | `terraform-38775-policy-state-close-order-regression` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-38775-policy-state-close-order-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-38775-policy-state-close-order-regression/verify.sh` |
| 5 | `terraform-38781-policy-callback-deferred-resources-regression` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-38781-policy-callback-deferred-resources-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/hashicorp-terraform/tasks/terraform-38781-policy-callback-deferred-resources-regression/verify.sh` |

### `orchardcore-maintenance-sequence-v1`

- Fixture: `large-orchardcms-orchardcore`
- Primary metric: cumulative provider-billed workflow tokens
- Reset policy: Reset once before the session; preserve repository, tool, index, cache, generated config, memory, and agent state between tasks.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `orchard-base64-string-decode-regression` | `sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-base64-string-decode-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-base64-string-decode-regression/verify.sh` |
| 2 | `orchard-base64-stream-position-regression` | `sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-base64-stream-position-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-base64-stream-position-regression/verify.sh` |
| 3 | `orchard-email-address-validation-regression` | `sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-email-address-validation-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-email-address-validation-regression/verify.sh` |
| 4 | `orchard-json-array-merge-union-regression` | `sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-json-array-merge-union-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-json-array-merge-union-regression/verify.sh` |
| 5 | `orchard-result-success-state-regression` | `sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-result-success-state-regression/agent-prompt.txt` | `sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-result-success-state-regression/verify.sh` |

### `fastify-maintenance-sequence-v1`

- Fixture: `medium-fastify-fastify`
- Primary metric: cumulative provider-billed workflow tokens
- Reset policy: Reset once before the session; preserve repository, tool, index, cache, generated config, memory, and agent state between tasks.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `fastify-query-schema-alias-regression` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-query-schema-alias-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-query-schema-alias-regression/verify.sh` |
| 2 | `fastify-response-2xx-serializer-regression` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-response-2xx-serializer-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-response-2xx-serializer-regression/verify.sh` |
| 3 | `fastify-trust-proxy-last-header-regression` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-trust-proxy-last-header-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-trust-proxy-last-header-regression/verify.sh` |
| 4 | `fastify-has-route-method-case-regression` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-has-route-method-case-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-has-route-method-case-regression/verify.sh` |
| 5 | `fastify-reply-hijack-state-regression` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-reply-hijack-state-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-reply-hijack-state-regression/verify.sh` |

### `beets-maintenance-sequence-v1`

- Fixture: `medium-beetbox-beets`
- Primary metric: cumulative provider-billed workflow tokens
- Reset policy: Reset once before the session; preserve repository, tool, index, cache, generated config, memory, and agent state between tasks.

| Order | Task | Prompt | Verifier |
|---:|---|---|---|
| 1 | `beets-pathformats-query-key-regression` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-pathformats-query-key-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-pathformats-query-key-regression/verify.sh` |
| 2 | `beets-hidden-dotfile-regression` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-hidden-dotfile-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-hidden-dotfile-regression/verify.sh` |
| 3 | `beets-color-uncolorize-regression` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-color-uncolorize-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-color-uncolorize-regression/verify.sh` |
| 4 | `beets-human-bytes-boundary-regression` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-human-bytes-boundary-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-human-bytes-boundary-regression/verify.sh` |
| 5 | `beets-template-escape-character-regression` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-template-escape-character-regression/agent-prompt.txt` | `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-template-escape-character-regression/verify.sh` |

## Artifact contract

Each completed session keeps exactly four files in its session directory:

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json
  changes.diff
  evidence.jsonl.gz
  manifest.sha256
```

`run.json` contains summary metadata, provider usage, and per-task verifier exits.

`changes.diff` contains the final code changes produced by the agent.

`evidence.jsonl.gz` contains recoverable raw streams such as prompts, Codex events, setup logs, verifier output, provider usage extraction, and tool-isolation audit output.

`manifest.sha256` hashes the other three files.

Do not commit materialized runtime state such as `project/`, `project/repo/`, `.venv/`, `__pycache__/`, `codex-homes/`, split task transcripts, or split verifier/setup logs.

## Maintenance contract

- Update `data/workflow-task-sequences.json` and `data/repository-fixtures.json` before updating this runbook.
- Run `python3 scripts/update_workflow_runbook.py` after registry changes.
- `python3 scripts/validate_repository.py` runs `scripts/update_workflow_runbook.py --check` and fails on drift.
- Truth docs own durable claims; this runbook is the operator procedure generated from the current registries.
- Retired calibration artifacts such as `sources/evaluations/fixture-corpus/v1/` and `sources/evaluations/phase-2-experiment-suite-v1/` should not reappear as active workflow architecture.
