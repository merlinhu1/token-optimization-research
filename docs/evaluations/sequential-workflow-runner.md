# Sequential workflow runner manual

This page documents runner details. The maintained operator runbook is `docs/evaluations/workflow-evaluation-runbook.md`, rendered from the active workflow registries.

## What this runner does

`scripts/run_codex_workflow_evaluation.py` runs one profile on one active workflow sequence from `data/workflow-task-sequences.json`.

The runner delivers task state and prompts sequentially:

1. inject task 1's regression only and commit that state as a parentless model-facing root;
2. show Codex task 1 only;
3. run the hidden task 1 verifier and capture its task delta;
4. after a pass, inject task 2 only, preserve prior source fixes, and replace model-facing Git metadata with a new parentless root;
5. resume the same Codex thread with task 2 only;
6. repeat until all tasks pass or one gate fails;
7. extract cumulative provider tokens, retain ordered per-task deltas, and run the final behavioral verifier.

Future prompts and future regressions remain absent until their turn. The model container mounts the target repository and an isolated output directory, not the workflow run directory, task fixtures, seed patches, controller Git objects, or verifier scripts. The controller hashes verifier assets before execution and verifies both verifier integrity and true-root concealment before acceptance.

The matrix takes a global production lock before provider-capable planning, publishes nothing from a failed lane, retains only bounded compact failure evidence, and removes disposable lane checkouts unless `--keep-lanes` is set.

Do not use older all-tasks-visible or verifier-visible workflow artifacts for decision evidence.

## Activation and prerequisites

Fastify, Terraform, and Beets are the active primary sequences after behavioral fixture qualification. `--list-sequences` exposes all three, but provider-backed execution still requires an explicit frozen protocol and operator authorization; fixture validation uses `--prepare-only`.

A sequence may return to `active` only after it has causally related multi-file behavior, behavioral acceptance tests, standalone seeded-fail/fixed-pass evidence, and a clean lazy-seed prepare smoke.

For an activated sequence, verify the runner and container from the repository root:

```bash
python3 scripts/run_codex_workflow_evaluation.py --list-sequences
docker image inspect token-eval-codex:latest >/dev/null
```

Frozen protocols directly bind the qualification hash, execution-harness hashes, Dockerfile hash, inspected image ID, and RepoDigests for `token-eval-codex:latest`. Runtime setup re-inspects the tag and rejects changed image IDs before provider spend. `scripts/refresh_workflow_contracts.py` refuses stale qualification evidence and never rewrites it.

Codex auth is copied from the selected source Codex home into the isolated run home. Real evaluation runs must keep container, Codex, and dependency preflights enabled.

## No-model prepare gate

Run `--prepare-only` before model spend after a sequence is reactivated. The generated `prepare-verification.json` must prove all of these:

- only task 1's regression is present;
- future regressions remain absent and forward-applicable;
- only `task-prompts/task-01.md` is materialized;
- task fixtures, seed patches, and verifier scripts remain controller-only;
- the model-facing Git repository has one parentless commit and no remote;
- the fixed snapshot commit and earlier stage commits are absent from the model-facing object database and reflog;
- `git status --short` is clean.

During a paid run, the controller captures each task delta, injects only the next regression after the current verifier passes, and replaces model-facing Git metadata with a new true-root baseline. Source files, tool indexes, caches, generated configuration, the agent home, and the Codex thread persist.

## Paid execution gate

Do not run a lane or matrix while `--list-sequences` is empty. After a sequence is reactivated, use the maintained commands in `docs/evaluations/workflow-evaluation-runbook.md`. The matrix runs one missing baseline per sequence and will not schedule treatments until that baseline has quality score >= 4, no critical failures, and objective acceptance. Treatment protocols are frozen separately for each profile. Any failed execution, isolation, concealment, verifier-integrity, or quality gate stops that lane.

## Artifacts to inspect

Each completed run keeps exactly four files in its session directory:

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json              # summary, protocol/execution identity, metadata, token usage, per-task verifier exits
  changes.diff          # ordered task deltas, each relative to that task's concealed stage root
  evidence.jsonl.gz     # compressed raw stream: prompts, Codex events, logs, verifier output/integrity checks
  manifest.sha256       # hashes for the other three files
```

Do not commit materialized runtime state such as `project/`, `project/repo/`, `.venv/`, `__pycache__/`, `codex-homes/`, split task transcripts, or split verifier/setup logs. The runner may create those while executing, but successful runs compact them into `evidence.jsonl.gz` and remove the scratch tree before returning.

The registry is updated at:

```text
data/workflow-sessions.json
```

When reviewed canonical baseline and treatment records exist for the same frozen protocol fingerprint and replicate, a comparison JSON is written under:

```text
sources/evaluations/workflow-sessions/
```

## Common problems

### `codex` is not on the host PATH

The Docker-backed runner does not require host `codex` to be on PATH for real model execution, but host-side exploratory commands may fail. Use the runner's preflight output rather than assuming host PATH reflects container availability.

### Docker image missing

If this fails:

```bash
docker image inspect token-eval-codex:latest >/dev/null
```

build the standard evaluation image from the repository root before spending model tokens:

```bash
docker build \
  -f sources/evaluations/fixtures/container/Dockerfile \
  -t token-eval-codex:latest \
  .
```

### Codex auth missing

If preflight fails before a model run, check the `--source-codex-home` path and inspect:

```text
sources/evaluations/workflow-sessions/<session-id>/codex-preflight.json
```

Do not publish copied Codex homes. The runner deletes `codex-homes/` and redacts auth-home metadata after runs.

### Foreground timeout while manually wrapping commands

Hermes foreground terminal calls cap at 600 seconds. Humans running from a normal shell can use longer shell sessions, but agent-driven long runs should use background execution or the bounded-concurrency matrix.

## Validation after manual runs

```bash
python3 scripts/validate_repository.py
git diff --check
truthmark check --json >/tmp/truthcheck_sequential_workflow.json
truthmark index --json >/tmp/truthindex_sequential_workflow.json
```

A completed workflow-reproduction record is valid only if it records:

```json
"prompt_delivery": {
  "mode": "sequential-one-task-at-a-time",
  "future_tasks_visible": false,
  "future_prompts_materialized_lazily": true
},
"leakage_controls": {
  "task_directories_model_visible": false,
  "verifier_assets_model_visible": false,
  "verifier_integrity_passed": true
}
```

Seed-origin concealment must also be enabled. Deterministic verifier success records execution correctness only; objective acceptance remains false until `quality_review_status` is `reviewed`, `quality_score` is at least 4, and no critical failure is recorded.
