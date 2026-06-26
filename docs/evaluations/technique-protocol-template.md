# Technique evaluation protocol template

## Technique or stack

- Evaluation ID:
- Technique/tool/stack IDs:
- Evidence stage target: benchmark-audit | reproduction
- Surface under test:
- Hypothesis:
- Expected conflict set:
- Expected stackable surfaces:

## Workload

- Task ID:
- Task class:
- Repository fixture and commit:
- Agent/model/provider:
- Baseline profile ID:
- Treatment profile ID:
- Turn/time/tool budget:

## Token accounting

- Accounting boundary: artifact_estimated | request_estimated | provider_billed_request | provider_billed_task | session_total
- Measurement source: provider API | local agent log | ccusage | tokbench | tokenizer | manual count
- Fresh input tokens:
- Cached input tokens:
- Cache-write tokens:
- Output tokens:
- Reasoning tokens:
- Estimated cost:

## Software quality gates

- Deterministic verifier:
- Static checks:
- Diagnostic facts that must survive:
- Human quality rubric additions:
- Critical failure conditions:

## Procedure

1. Freeze fixture and task prompt.
2. Capture baseline transcript, usage, verifier output, and quality result.
3. Reset repository, agent state, memory, indexes, hooks, and generated config.
4. Activate treatment profile and record enabled/disabled surfaces.
5. Run the same task with the same model/provider and budget where possible.
6. Capture treatment transcript, usage, verifier output, quality result, raw artifacts, and transformed artifacts.
7. Compare operation-level, task-level, provider-billed, and quality outcomes separately.
8. Record failed and excluded runs with reason codes.

## Results

- Summary:
- Token/cost result:
- Quality result:
- Operational result:
- Negative findings:
- Follow-up experiments:
