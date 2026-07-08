# Continuous workflow simulation

## Purpose

Continuous workflow simulation is the primary Phase 2 evidence path for token-optimization claims. It measures cumulative provider-billed token usage across a realistic persistent project session.

The goal is to determine whether a baseline or treatment profile gets an ordered sequence of repository tasks to green with fewer provider-billed tokens while preserving task success and final repository quality.

## Core rule

Reset before the session, not between tasks. Feed tasks to the agent one at a time.

A valid workflow session preserves these across the ordered task sequence:

- repository working tree;
- tool indexes and caches;
- generated profile files;
- agent home and runtime config;
- memory/state stores enabled by the active profile;
- accumulated task artifacts unless the protocol explicitly models cleanup.

The agent must not see future task prompts, future verifier commands, or future task identifiers before the current task verifier has passed. A valid runner starts or resumes the same agent session for task 1, runs the task 1 verifier, then resumes that same session with task 2 only after task 1 passes, and so on. Composite prompts that expose all tasks up front are sanity/debug artifacts only, not primary workflow reproduction evidence.

## Leakage controls

Issue-derived regression fixtures must not expose the answer path as a visible git diff or public issue lookup key. Model-facing workflow repositories should commit the broken-start state as the local baseline, remove upstream remotes, use neutral task aliases such as `task-01`, and sanitize task prompts so they do not mention fixed upstream commits, public issue numbers, or that a regression patch removed the production fix. Raw setup artifacts may retain the original task IDs and seed-patch provenance outside the model-facing repository.

The stronger long-term fixture design is to build tasks from pre-fix bases plus hidden acceptance tests instead of production-code reverse patches. Until then, seed-origin concealment is required for objective workflow runs.

## Primary metric

The primary metric is cumulative provider-billed workflow usage:

```text
workflow_session_total = sum(provider-billed usage for all model-visible work in the session)
```

Record fresh input, cached input, cache-write, output, reasoning when available, total provider tokens, and cost. Report tokens per accepted task as a derived metric.

## Quality constraint

A treatment only supports a positive claim when it reduces cumulative provider-billed workflow tokens or cost and preserves quality.

Quality requires:

- per-task verifier success where available;
- final repository verifier success where available;
- no critical safety, diagnostic, stale-context, or reversibility failure;
- final diff/status and transcript reviewability.

## Workflow session contract

A workflow session binds:

- `session_id`;
- `experiment_group_id`;
- repository fixture and initial snapshot;
- task sequence ID;
- profile ID;
- runtime/model condition;
- state policy;
- per-task results;
- cumulative token usage;
- final software-quality result;
- operational reproducibility evidence.

Baseline and treatment sessions are directly comparable only when they use the same repository fixture, initial snapshot, task sequence, runtime, provider, model, model condition, and quality gates.

## Evidence boundaries

| Evidence type | Role |
|---|---|
| `workflow-simulation` | Primary evidence for tool or stack ranking. |
| `workflow-ablation` | Attribution evidence after a full/default profile has workflow evidence. |
| `sanity-check` | Install, profile-isolation, usage-capture, diagnostic-preservation, and runner checks only. |

Sanity checks do not rank tools.

## Artifact layout

```text
sources/evaluations/workflow-sessions/<session-id>/
  workflow-session-record.json
  environment.json
  profile-manifest.json
  cumulative-provider-usage.json
  final-git-status.txt
  final-diff.patch
  final-verifier-output.txt
  quality-review.md
  task-01-<task-id>/
    prompt.md
    transcript.jsonl
    provider-usage.json
    verifier-output.txt
    task-result.json
```

## Initial research experiments

Human rerun recipe: use `docs/evaluations/sequential-workflow-runner.md`; prefer `scripts/run_sequential_workflow_pair.sh <sequence-id>` for one paired baseline plus LeanCTX rerun, or `scripts/run_sequential_workflow_matrix.py --max-parallel 4` for isolated parallel reruns of all four active flows.

Start with one medium-project task sequence before running a matrix:

1. `baseline-bare-codex` on the full persistent sequence.
2. One treatment profile on the same sequence and model condition.
3. Compare cumulative provider tokens, tokens per accepted task, pass rate, correction turns, repeated reads, stale-context incidents, and final quality.
4. Expand only after the record shape, artifacts, and validation are reliable.

Candidate first treatments:

- LeanCTX as the broad/persistent-context candidate;
- CodeGraph or Serena as narrower retrieval comparators;
- Headroom default Codex integration as a broad compression/proxy candidate.
