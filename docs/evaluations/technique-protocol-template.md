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

- Accounting boundary: complete persistent workflow session
- Primary metric: cumulative provider-reported workflow tokens
- Measurement source: provider API or provider-backed agent log
- Fresh input tokens:
- Cached input tokens:
- Cache-write tokens:
- Output tokens:
- Reasoning tokens:
- Total provider tokens:
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
5. Capture provider events, structured per-task verifier outcomes, final diff/status, treatment/isolation evidence, and recoverable artifacts without extra model reporting.
6. Preserve declared session state between tasks.
7. Run every concealed task verifier after the lane, then complete independent quality review.
8. Compare cumulative provider-reported workflow token use and quality outcomes.
9. Record failed and excluded sessions with reason codes.

## Results

- Summary:
- Cumulative provider-token result:
- Quality result:
- State behavior result:
- Operational result:
- Negative findings:
- Follow-up experiments:
