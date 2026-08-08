# Immediately usable evaluation flows

## Directory convention

Completed workflow sessions keep exactly four files in the session directory:

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json
  changes.diff
  evidence.jsonl.gz
  manifest.sha256
```

Use `data/workflow-sessions.json` for compact workflow-session records. Keep raw logs out of reports unless summarized; recoverable raw evidence lives inside `evidence.jsonl.gz`, not as split transcript/log directories.

## Flow 1: run a continuous workflow simulation

Use this for primary evidence about individual tools and compatibility-safe stacks.

1. Select a `task_sequence_id` from `data/workflow-task-sequences.json`.
2. Reset the repository, profile home, tool state, indexes, caches, and agent home once before the session.
3. Activate exactly one baseline or treatment profile.
4. Run tasks in the sequence order without resetting repository or tool state between tasks.
5. Capture provider events, task checkpoints, verifier output, and diff/status into the compact evidence bundle without asking the model for extra reporting.
6. Preserve indexes, caches, generated config, memory, and agent/tool home across tasks unless the sequence explicitly models a reset.
7. Run every concealed task verifier after the last task, without short-circuiting, and emit structured per-task outcomes.
8. Derive `tasks_passed` from those structured outcomes.
9. Aggregate cumulative provider-reported tokens across all tasks; do not estimate money.
10. Write the compact bundle and append metadata to `data/workflow-sessions.json`; add an independent source-quality review only as optional diagnostic context.

Minimum token condition: treatment and baseline are compatible, operationally valid provider samples. Report the cumulative token delta as the primary outcome and structured correctness/quality alongside it without gating or replacing either sample.

## Flow 2: run a workflow ablation

Use this for attribution after a full/default treatment has a workflow result.

1. Start from the same initial snapshot and task sequence as the full treatment.
2. Disable or replace one component or surface before the session begins.
3. Run the full ordered sequence with the same persistent-state policy.
4. Compare cumulative tokens, structured task outcomes, and final quality against the full treatment and baseline.

Minimum pass condition: the ablation explains which component changed cumulative workflow token usage without introducing uncontrolled surface overlap.

## Flow 3: run a sanity check

Use this only for install, isolation, diagnostic-preservation, or runner validation.

1. Define the exact sanity question before running the check.
2. Run the smallest fixture or artifact needed to answer that question.
3. Capture raw and transformed artifacts when relevant.
4. Verify required diagnostics, profile isolation, provider-usage extraction, or reset behavior.
5. Label the result `sanity-check` and do not use it to rank tools.

Minimum pass condition: the artifact, runner, or profile behaves as required for future workflow-session evidence.

## Flow 4: benchmark-audit an existing repository benchmark

Use this when a cited repository already contains a harness or published results.

1. Identify benchmark files, task definitions, result files, and scoring code.
2. Record whether token accounting is estimated, provider-reported, or product self-reported.
3. Inspect how failed, timed-out, or excluded runs are handled.
4. Inspect whether quality gates are deterministic or subjective.
5. Record baseline parity: same model, same prompt, same allowed tools, same max turns.
6. Decide whether the dossier can move from `source-logic` to `benchmark-audit`.

Output:

- updated dossier benchmark section;
- raw notes under `sources/evaluations/<evaluation-id>/benchmark-audit.md`;
- compact evidence record labeled `benchmark_audit`.
