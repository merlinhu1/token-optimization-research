# Token usage and software quality standards

## Token accounting standard

Token-saving claims must state the accounting boundary.

| Boundary | Definition | Accepted use |
|---|---|---|
| `artifact_estimated` | Tokenizer estimate for a static artifact before and after transformation. | Sanity checks and reducer debugging. |
| `request_estimated` | Estimated input/output tokens for one model request. | Local analysis when provider records are unavailable. |
| `provider_billed_request` | Provider-reported usage for one request, including cache fields when exposed. | Request-level cost diagnosis. |
| `provider_billed_task` | Sum of provider-reported usage across one complete task. | Per-task diagnostic inside a workflow session. |
| `workflow_session_total` | Sum of provider-reported usage across a persistent ordered task sequence, including setup visible to the model, retries, and follow-up corrections. | Primary Phase 2 metric. |

The primary Phase 2 token metric is `workflow_session_total` where provider records are available. `artifact_estimated`, `request_estimated`, and isolated `provider_billed_task` values are supporting diagnostics only.

## Required token fields

Each workflow session should capture these fields when available:

| Field | Meaning |
|---|---|
| `fresh_input_tokens` | Non-cached input tokens billed or reported as fresh. |
| `cached_input_tokens` | Cache-read input tokens, if provider exposes them. |
| `cache_write_tokens` | Cache-write tokens, if provider exposes them. |
| `output_tokens` | Visible model output tokens. |
| `reasoning_tokens` | Hidden reasoning tokens, if provider exposes them. |
| `total_provider_tokens` | Provider-reported total or reconstructed total with formula noted. |
| `estimated_cost_usd` | Cost using recorded model/pricing table and timestamp. |
| `tokens_per_accepted_task` | Total provider tokens divided by tasks that passed verifier/quality gates. |
| `measurement_source` | Provider API, local agent log, ccusage, tokbench, tokenizer, or manual artifact count. |

Sanity checks may additionally record `tool_result_tokens_estimated` and `transformed_tool_result_tokens_estimated` for artifact-level reducer diagnostics.

## Derived token metrics

Use explicit formulas:

- `workflow_billed_token_change = treatment_total_provider_tokens - baseline_total_provider_tokens`
- `workflow_billed_token_reduction_ratio = 1 - treatment_total_provider_tokens / baseline_total_provider_tokens`
- `tokens_per_accepted_task = total_provider_tokens / accepted_task_count`
- `cost_change_usd = treatment_cost_usd - baseline_cost_usd`
- `turn_change = treatment_turns - baseline_turns`
- `tool_call_change = treatment_tool_calls - baseline_tool_calls`
- `artifact_reduction_ratio = 1 - transformed_artifact_tokens / raw_artifact_tokens`

A positive artifact reduction ratio is not sufficient for a positive workflow result.

## Software quality standard

Every workflow needs explicit quality gates before token or cost savings can be accepted.

| Quality dimension | Required check |
|---|---|
| Functional correctness | The complete concealed verifier suite passes once against the final cumulative repository; no per-task hidden controller gate truncates the measured lane. |
| Diagnostic preservation | For failure-repair tasks, the treatment preserves the error type, failing file, relevant stack frame, and actionable message. |
| Code quality | Final diff is minimal for the task sequence, avoids unnecessary dependencies, preserves conventions, and does not bypass validation. |
| Maintainability | New abstractions, config, and generated files are justified by the session outcome. |
| Safety/security | Trust-boundary validation, secrets handling, permissions, and sandbox changes are reviewed when touched. |
| Reviewability | The final diff, transcript, provider usage, and tool-state changes are inspectable. |
| Reversibility | Tool installation, hooks, memory, indexes, and generated config have a reset or disable path after the session. |

## Quality scoring rubric

Use a five-point ordinal score only after deterministic gates are recorded and a software-quality review has been completed. A passing verifier records functional correctness; it must not automatically assign score 3, 4, or 5. Until review, record `quality_review_status: not-reviewed`, `quality_score: null`, and keep `accepted_for_objective` false.

| Score | Meaning |
|---:|---|
| 0 | Workflow failed, final verifier failed, or output is unusable. |
| 1 | Partial progress but important requirements or diagnostics are missing. |
| 2 | Tasks pass narrowly with quality, maintainability, stale-state, or recovery concerns. |
| 3 | Workflow passes with acceptable quality and no major review blockers. |
| 4 | Workflow passes with good quality, minimal unnecessary change, and clear recovery evidence. |
| 5 | Workflow passes, is minimal, robust, well-verified, and easier to review than baseline. |

A treatment is acceptable for Phase 2 only if it meets both criteria:

1. required per-task and final verifiers pass, or the quality score is at least 3 when no deterministic verifier exists;
2. no critical diagnostic, safety, stale-context, or reversibility failure is present.

## Statistical and reporting standard

- Compare baseline and treatment by workflow session totals first.
- Report median and range across repeated workflow sessions when cost permits.
- Pair sessions by task sequence, repository snapshot, profile controls, runtime, provider, model, and model condition.
- Keep failed and excluded sessions in the dataset with reason codes.
- Label sanity checks, maintainer-run results, external pilots, benchmark audits, and local workflow reproductions separately.
- Prefer effect sizes over rank-only claims.
