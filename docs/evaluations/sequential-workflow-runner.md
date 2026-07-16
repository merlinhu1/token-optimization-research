# Warm-state workflow lane runner

This page documents runner details. The maintained operator runbook is `docs/evaluations/workflow-evaluation-runbook.md`, rendered from the active workflow registries.

## What this runner does

`scripts/run_codex_workflow_evaluation.py` runs one profile on one active multi-task sequence from `data/workflow-task-sequences.json`.

The primary lane measures cumulative provider usage after model and tool state warm up:

1. merge every qualified regression against the same pinned fixed snapshot before provider execution;
2. conceal the fixed snapshot and commit the composite broken tree as one parentless model-facing root;
3. materialize and send task 1 only;
4. capture its provider events and cumulative source checkpoint without running a controller verifier;
5. resume the same Codex thread with each later prompt while preserving source, tool, index, cache, profile, and agent state;
6. after every prompt completes, run the complete concealed verifier suite once against the cumulative final repository;
7. extract cumulative provider tokens and retain the ordered checkpoints plus final diff.

Future prompts remain controller-only until their turn. Future regression code is present from lane start. The model container does not mount task fixtures, seed patches, controller Git objects, or verifier scripts. Controller verifier hashes are checked during the lane, but functional verification provides no intermediate feedback and never truncates a lane.

The matrix takes a global production lock before provider-capable planning, publishes nothing from a failed lane, retains only bounded compact failure evidence, and removes disposable lane checkouts unless `--keep-lanes` is set.

## Activation and prerequisites

Fastify, Terraform, and Beets are the active primary sequences after behavioral fixture qualification. Provider-backed execution requires an explicit frozen protocol and operator authorization; fixture validation uses `--prepare-only`.

An active sequence must have:

- causally related behavioral tasks;
- standalone seeded-fail/fixed-pass evidence for every task;
- a deterministic conflict-free composite seed;
- evidence that every task verifier fails against the composite broken start;
- evidence that every verifier passes against the fixed snapshot;
- clean model-facing concealment and verifier isolation.

For an activated sequence, verify the runner and container from the repository root:

```bash
python3 scripts/run_codex_workflow_evaluation.py --list-sequences
docker image inspect token-eval-codex:latest >/dev/null
```

Frozen protocols bind qualification bytes, execution-harness hashes, Dockerfile hash, inspected image identity, and task-directory bytes. Runtime setup rejects stale bindings before provider spend. `scripts/refresh_workflow_contracts.py` validates qualification evidence and never invents qualification results.

## No-model prepare gate

Run `--prepare-only` after any fixture, verifier, prompt, runner, or isolation change. `prepare-verification.json` must prove:

- every declared regression was merged into the composite broken start;
- only `task-prompts/task-01.md` was materialized;
- task fixtures, seed patches, and verifier scripts remain controller-only;
- the model-facing Git repository has one clean parentless commit and no remote;
- the fixed snapshot object is absent from the model-facing object database and reflog;
- qualification proves composite-seeded failure and full-fixed cumulative success.

Preparation does not call the model and does not authorize a paid run.

## Runtime acceptance

There are no per-task hidden functional gates. Between prompts, the controller stops only for operational invalidity such as a nonzero Codex process exit, missing thread identity, verifier-integrity corruption, isolation failure, or unrecoverable runtime failure.

A provider-backed lane is eligible for the token-usage objective when:

- every scheduled prompt completed in the same thread;
- provider usage is complete and warning-free;
- verifier integrity and tool isolation pass;
- compact evidence is recoverable.

Concealed verifier outcomes and source-quality reviews remain diagnostic evidence about the sampled model behavior. They do **not** gate token accounting or baseline reuse. Keep the first operationally valid sample for each frozen protocol and replicate; never rerun merely because the model produced imperfect code or received a sub-perfect review score. Rerun only when the fixture/contract was invalid or the provider execution was operationally incomplete.

## Compact artifacts

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json              # protocol identity, total usage, operational checkpoints, final verifier result
  changes.diff          # ordered cumulative checkpoints plus final cumulative diff
  evidence.jsonl.gz     # prompts, provider events, setup, composite seed, integrity, final verifier, audit
  manifest.sha256       # hashes for the other three files
```

Do not publish materialized checkouts, virtual environments, Codex homes, caches, controller Git objects, or split logs.

## Common problems

### Stale protocol

After any bound runner, prompt, verifier, qualification, schema, runtime, or task-directory change:

```bash
python3 scripts/refresh_workflow_contracts.py
```

Refresh only after qualification has been regenerated from a clean pinned checkout.

### Composite seed conflict

A conflict means two independently-authored regressions cannot coexist unambiguously. Repair or replace the fixture tasks and regenerate qualification. Do not fall back to injecting a patch over model-authored work.

### Missing Codex authentication or image

Use lane preflight output. Do not publish copied Codex homes. Build the standard image with the documented fixture Dockerfile when its pinned identity is intentionally changed.

## Validation

```bash
python3 scripts/test_workflow_evaluation_contract.py
python3 scripts/validate_repository.py
git diff --check
truthmark check --json
truthmark index --json
```

A current record uses sequential prompt disclosure, `preseeded-composite` seed delivery, `final-only` controller verification, one true-root baseline at lane start, and persistent repository/tool/agent state through the complete lane.
