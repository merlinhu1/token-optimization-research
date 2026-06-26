# Technique evaluation protocol template

## Technique or stack

- Workflow session ID:
- Technique/tool/stack IDs:
- Evidence stage target: benchmark-audit | reproduction
- Evidence type: workflow-simulation | workflow-ablation | sanity-check
- Surface under test:
- Hypothesis:
- Expected conflict set:
- Expected stackable surfaces:

## Workload

- Task sequence ID:
- Ordered task IDs:
- Repository fixture and initial snapshot:
- Agent/model/provider/model condition:
- Baseline profile ID:
- Treatment profile ID:
- Session turn/time/tool budget:
- State policy: reset before session; persist between tasks unless explicitly modeled otherwise

## Token accounting

- Accounting boundary: workflow_session_total | provider_billed_task | provider_billed_request | request_estimated | artifact_estimated
- Primary metric: cumulative provider-billed workflow tokens
- Measurement source: provider API | local agent log | ccusage | tokbench | tokenizer | manual count
- Fresh input tokens:
- Cached input tokens:
- Cache-write tokens:
- Output tokens:
- Reasoning tokens:
- Total provider tokens:
- Estimated cost:
- Tokens per accepted task:

## Software quality gates

- Per-task deterministic verifiers:
- Final repository verifier:
- Static checks:
- Diagnostic facts that must survive:
- Human quality rubric additions:
- Critical failure conditions:

## Procedure

1. Freeze fixture, initial snapshot, task sequence, and prompts.
2. Reset repository, agent state, memory, indexes, hooks, generated config, and temporary directories once before the session.
3. Activate baseline or treatment profile and record enabled/disabled surfaces.
4. Run the ordered task sequence without resetting between tasks.
5. Capture per-task transcript, usage, verifier output, quality result, raw artifacts, and transformed artifacts.
6. Preserve session state between tasks and record useful reuse, repeated rediscovery, stale-context incidents, and overfeeding.
7. Run final repository verifier and quality review.
8. Compare cumulative provider-billed workflow usage and quality outcomes.
9. Record failed and excluded sessions with reason codes.

## Results

- Summary:
- Cumulative token/cost result:
- Quality result:
- State behavior result:
- Operational result:
- Negative findings:
- Follow-up experiments:
