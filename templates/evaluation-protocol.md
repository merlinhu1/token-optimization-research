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
- Sole token metric: weighted token cost (`fresh input + 0.1 × cached input + 6 × output`)
- Measurement source: provider API or provider-backed agent log
- Fresh input tokens:
- Cached input tokens:
- Cache-write tokens:
- Output tokens:
- Reasoning tokens:
- Weighted token cost:

## Model-behavior diagnostics

- Per-task acceptance verifiers (compile all tasks; one essential smoke for feature/refactor tasks; review tasks compile-only):
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
9. Compare weighted token cost only within a compatible baseline pool; never report a raw-token comparison.
10. Record invalid or incomplete experiments with explicit reason codes; distinguish them from model-behavior failures.

## Results

- Summary:
- Weighted token-cost result:
- Model-behavior diagnostics:
- State behavior result:
- Operational result:
- Negative findings:
- Follow-up experiments:
