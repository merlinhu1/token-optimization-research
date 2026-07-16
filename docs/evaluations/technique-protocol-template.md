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
- Tokens per verifier-passing task, diagnostic only:

## Model-behavior diagnostics

- Per-task deterministic verifiers:
- Final repository verifier:
- Static checks:
- Diagnostic facts that must survive:
- Optional source-review rubric:
- Fixture/contract invalidity conditions:

## Procedure

1. Freeze fixture, initial snapshot, task sequence, prompts, provider/model condition, and accounting boundary.
2. Reset repository, agent state, memory, indexes, hooks, generated config, and temporary directories once before the session.
3. Activate baseline or treatment profile and record enabled/disabled surfaces.
4. Run the ordered task sequence without resetting between tasks.
5. Capture provider events, structured per-task verifier outcomes, final diff/status, treatment/isolation evidence, and recoverable artifacts without extra model reporting.
6. Preserve declared session state between tasks.
7. Retain the first operationally complete, integrity-valid provider sample. Do not rerun because of verifier or review outcomes.
8. Record verifier results and any optional source review as diagnostics.
9. Compare cumulative provider-reported workflow token use only within a compatible baseline pool.
10. Record invalid or incomplete experiments with explicit reason codes; distinguish them from model-behavior failures.

## Results

- Summary:
- Cumulative provider-token result:
- Model-behavior diagnostics:
- State behavior result:
- Operational result:
- Negative findings:
- Follow-up experiments:
