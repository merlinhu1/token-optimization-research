# Sequential workflow runner manual

This page is the human rerun recipe for continuous workflow evaluations.

## What this runner does

`scripts/run_codex_workflow_evaluation.py` runs one profile on one active workflow sequence from `data/workflow-task-sequences.json`.

The runner discloses tasks sequentially:

1. show Codex task 1 only;
2. run task 1 verifier;
3. resume the same Codex thread with task 2 only after task 1 passes;
4. repeat until all tasks pass or one gate fails;
5. extract cumulative provider tokens from the concatenated Codex JSONL events.

Do not use older all-tasks-visible workflow artifacts for decision evidence.

## Prerequisites

From the repository root:

```bash
python3 scripts/run_codex_workflow_evaluation.py --list-sequences
docker image inspect token-eval-codex:latest >/dev/null
```

Codex auth must be available through the source Codex home copied into the isolated run home. The default is:

```text
/opt/data/home/.codex
```

Override it when needed:

```bash
--source-codex-home /path/to/.codex
```

The runner performs container and Codex preflights by default. Do not skip those for real evaluation runs.

## Smoke prepare without model spend

Use this only to verify fixture construction, prompt sanitization, and seed-origin concealment:

```bash
python3 scripts/run_codex_workflow_evaluation.py \
  --sequence-id requests-maintenance-sequence-v1 \
  --profile-id baseline-bare-codex \
  --prepare-only \
  --skip-container-preflight \
  --skip-codex-preflight \
  --skip-dependency-install \
  --session-id smoke-requests-sequential-runner

rm -rf sources/evaluations/workflow-sessions/smoke-requests-sequential-runner
```

Expected smoke properties:

- `task-prompts/task-01.md` contains task 1 only;
- there are no references to task 2+ in task 1's prompt;
- `project/repo` has no `origin` remote;
- `project/repo` has a clean git status;
- the visible commit is `workflow broken-start baseline`.

## Run one lane

```bash
python3 scripts/run_codex_workflow_evaluation.py \
  --sequence-id requests-maintenance-sequence-v1 \
  --profile-id baseline-bare-codex \
  --timeout-per-task 1800
```

Treatment lane:

```bash
python3 scripts/run_codex_workflow_evaluation.py \
  --sequence-id requests-maintenance-sequence-v1 \
  --profile-id retrieval-leanctx \
  --timeout-per-task 1800
```

## Run the paired baseline plus LeanCTX lanes

Preferred human rerun command:

```bash
scripts/run_sequential_workflow_pair.sh requests-maintenance-sequence-v1
```

With a different replicate or timeout:

```bash
REPLICATE_INDEX=1 scripts/run_sequential_workflow_pair.sh \
  flask-maintenance-sequence-v1 \
  --timeout-per-task 2400
```

The pair script runs repository validation, whitespace diff checks, and Truthmark check/index after both lanes complete.

## Run multiple flows in parallel

Use the matrix wrapper when you want to run more than one workflow flow at the same time. It materializes one isolated checkout per flow under `/opt/data/eval-workflow-lanes/`, runs each flow's paired baseline plus LeanCTX lanes inside that checkout, then copies workflow-session artifacts back and merges the produced records into `data/workflow-sessions.json`.

Dry-run the plan:

```bash
scripts/run_sequential_workflow_matrix.py --dry-run
```

Run all active flows with two concurrent flow lanes, the conservative default:

```bash
scripts/run_sequential_workflow_matrix.py
```

Run all four active flows concurrently if provider quota and host resources allow it:

```bash
scripts/run_sequential_workflow_matrix.py --max-parallel 4
```

Smoke the parallel wrapper without model spend:

```bash
scripts/run_sequential_workflow_matrix.py \
  requests-maintenance-sequence-v1 \
  flask-maintenance-sequence-v1 \
  --max-parallel 2 \
  --prepare-only \
  --skip-container-preflight \
  --skip-codex-preflight \
  --skip-dependency-install
```

Run a real subset:

```bash
scripts/run_sequential_workflow_matrix.py \
  requests-maintenance-sequence-v1 \
  flask-maintenance-sequence-v1 \
  --max-parallel 2
```

The matrix wrapper exists because running four pair scripts directly from the same checkout is not safe: those processes would race on `data/workflow-sessions.json`, workflow artifact directories, copied Codex homes, tool caches, and temporary Truthmark outputs.

## Active sequence IDs

Check live IDs with:

```bash
python3 scripts/run_codex_workflow_evaluation.py --list-sequences
```

Current active sequences are expected to include:

- `django-maintenance-sequence-v1`
- `terraform-maintenance-sequence-v1`
- `requests-maintenance-sequence-v1`
- `flask-maintenance-sequence-v1`

## Artifacts to inspect

Each completed run keeps exactly four files in its session directory:

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json              # summary, metadata, token usage, per-task verifier exits
  changes.diff          # final code changes produced by the agent
  evidence.jsonl.gz     # compressed raw stream: prompts, Codex events, logs, verifier output
  manifest.sha256       # hashes for the other three files
```

Do not commit materialized runtime state such as `project/`, `project/repo/`, `.venv/`, `__pycache__/`, `codex-homes/`, split task transcripts, or split verifier/setup logs. The runner may create those while executing, but successful runs compact them into `evidence.jsonl.gz` and remove the scratch tree before returning.

The registry is updated at:

```text
data/workflow-sessions.json
```

When both baseline and treatment exist for the same experiment group, a comparison JSON is written under:

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
  -f sources/evaluations/large-projects/container/Dockerfile \
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

Hermes foreground terminal calls cap at 600 seconds. Humans running from a normal shell can use longer shell sessions, but agent-driven long runs should use background execution or the pair script per lane.

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
  "future_tasks_visible": false
}
```

and seed-origin concealment is enabled.
