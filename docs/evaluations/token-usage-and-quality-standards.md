# Token usage and software quality standards

## Token accounting standard

Token-saving claims must state the accounting boundary.

| Boundary | Definition | Accepted use |
|---|---|---|
| `artifact_estimated` | Tokenizer estimate for a static artifact before and after transformation. | Micro-benchmark and reducer debugging. |
| `request_estimated` | Estimated input/output tokens for one model request. | Local analysis when provider records are unavailable. |
| `provider_billed_request` | Provider-reported usage for one request, including cache fields when exposed. | Request-level cost comparison. |
| `provider_billed_task` | Sum of provider-reported usage across a complete task. | Primary reproduction metric. |
| `session_total` | Full agent session usage, including setup, retries, and follow-up corrections. | Operational cost and budget analysis. |

The primary Phase 2 metric is `provider_billed_task` where provider records are available. `artifact_estimated` and `request_estimated` are supporting diagnostics only.

## Required token fields

Each run record should capture these fields when available:

| Field | Meaning |
|---|---|
| `fresh_input_tokens` | Non-cached input tokens billed or reported as fresh. |
| `cached_input_tokens` | Cache-read input tokens, if provider exposes them. |
| `cache_write_tokens` | Cache-write tokens, if provider exposes them. |
| `output_tokens` | Visible model output tokens. |
| `reasoning_tokens` | Hidden reasoning tokens, if provider exposes them. |
| `tool_result_tokens_estimated` | Estimated tool-output tokens before any compaction. |
| `transformed_tool_result_tokens_estimated` | Estimated tool-output tokens after compaction. |
| `total_provider_tokens` | Provider-reported total or reconstructed total with formula noted. |
| `estimated_cost_usd` | Cost using recorded model/pricing table and timestamp. |
| `measurement_source` | Provider API, local log, ccusage, tokbench, tokenizer, or manual artifact count. |

## Derived token metrics

Use explicit formulas:

- `artifact_reduction_ratio = 1 - transformed_artifact_tokens / raw_artifact_tokens`
- `fresh_input_change = treatment_fresh_input_tokens - baseline_fresh_input_tokens`
- `task_billed_token_change = treatment_total_provider_tokens - baseline_total_provider_tokens`
- `task_billed_token_reduction_ratio = 1 - treatment_total_provider_tokens / baseline_total_provider_tokens`
- `cost_change_usd = treatment_cost_usd - baseline_cost_usd`
- `turn_change = treatment_turns - baseline_turns`
- `tool_call_change = treatment_tool_calls - baseline_tool_calls`

A positive artifact reduction ratio is not sufficient for a positive task result.

## Software quality standard

Every task needs an explicit quality gate before token or cost savings can be accepted.

| Quality dimension | Required check |
|---|---|
| Functional correctness | Repository tests, task verifier, or executable reproduction script passes. |
| Diagnostic preservation | For failure-repair tasks, the treatment preserves the error type, failing file, relevant stack frame, and actionable message. |
| Code quality | Diff is minimal for the task, avoids unnecessary dependencies, preserves conventions, and does not bypass validation. |
| Maintainability | New abstractions, config, and generated files are justified by the task. |
| Safety/security | Trust-boundary validation, secrets handling, permissions, and sandbox changes are reviewed when touched. |
| Reviewability | The final diff and transcript are inspectable without hidden state. |
| Reversibility | Tool installation, hooks, memory, indexes, and generated config have a reset or disable path. |

## Quality scoring rubric

Use a five-point ordinal score only after deterministic gates are recorded.

| Score | Meaning |
|---:|---|
| 0 | Task failed, verifier failed, or output is unusable. |
| 1 | Partial progress but important requirements or diagnostics are missing. |
| 2 | Task passes narrowly with quality, maintainability, or recovery concerns. |
| 3 | Task passes with acceptable quality and no major review blockers. |
| 4 | Task passes with good quality, minimal unnecessary change, and clear recovery evidence. |
| 5 | Task passes, is minimal, robust, well-verified, and easier to review than baseline. |

A treatment is acceptable for Phase 2 only if it meets both criteria:

1. deterministic verifier passes or the quality score is at least 3 when no deterministic verifier exists;
2. no critical diagnostic, safety, or reversibility failure is present.

## Statistical and reporting standard

- Use at least three runs per baseline/treatment pair for stochastic agent tasks when cost permits.
- Report median and range; do not overinterpret mean values from small samples.
- Pair runs by task and repository snapshot.
- Keep failed and excluded runs in the dataset with reason codes.
- Label maintainer-run, external-pilot, and local-reproduction evidence separately.
- Prefer effect sizes over rank-only claims.
