# Token usage and software quality standards

## Accounting policy

The project measures **token use only**. It does not estimate or report monetary cost.

Token claims must name their accounting boundary:

| Boundary | Definition | Accepted use |
|---|---|---|
| `artifact_estimated` | Tokenizer estimate for one static artifact before and after transformation. | Reducer sanity checks only. |
| `request_estimated` | Estimated tokens for one model request when provider records are unavailable. | Local diagnosis only. |
| `provider_reported_request` | Provider-reported usage for one request, including cache components when exposed. | Request diagnosis. |
| `provider_reported_task` | Provider-reported usage across one task. | Optional workflow diagnosis. |
| `workflow_session_total` | Provider-reported usage across the complete persistent task sequence, including model-visible setup, retries, and corrections. | Primary metric. |

The canonical metric is `workflow_session_total`. Estimated artifact/request counts cannot establish a workflow saving.

## Required token fields

Record these when the provider exposes them:

| Field | Meaning |
|---|---|
| `fresh_input_tokens` | Non-cached input tokens. |
| `cached_input_tokens` | Cache-read input tokens. |
| `cache_write_tokens` | Cache-write tokens. |
| `output_tokens` | Visible model output tokens. |
| `reasoning_tokens` | Provider-reported reasoning tokens. |
| `total_provider_tokens` | Provider total or reconstructed total with formula recorded. |
| `tokens_per_accepted_task` | Workflow total divided by structured accepted-task count. |
| `measurement_source` | Provider event/log source used for extraction. |
| `accounting_basis` | Provider-reported token-volume boundary and any reconstruction rule. |

No monetary-cost field is required or produced.

## Derived metrics

Use explicit formulas:

- `workflow_token_change = treatment_total_provider_tokens - baseline_total_provider_tokens`
- `workflow_token_reduction_ratio = 1 - treatment_total_provider_tokens / baseline_total_provider_tokens`
- `tokens_per_accepted_task = total_provider_tokens / structured_accepted_task_count`
- `artifact_reduction_ratio = 1 - transformed_artifact_tokens / raw_artifact_tokens`

A positive artifact reduction ratio is not sufficient for a positive workflow result.

## Structured task outcomes

Every concealed verifier runs against the final cumulative repository, regardless of earlier failures. Record for each task:

- `task_id` and `order`;
- agent operational exit and declared-completion state;
- `verifier_exit_code`;
- `verifier_passed`;
- `accepted`.

`tasks_passed` is the count of tasks whose structured `accepted` value is true. Missing outcomes fail closed; the aggregate verifier exit is not used to synthesize all-or-zero task counts.

### Estimand-aligned acceptance

The research objective is provider-reported workflow token usage under fair, disclosed software-engineering tasks. Deterministic correctness is an eligibility gate for that token comparison, not a source-reconstruction benchmark.

A verifier may enforce disclosed observable behavior, compatibility, safety, and explicitly public structural contracts. It must not require canonical human-facing prose, local parameter names, source identity, or one implementation shape unless that exact requirement is disclosed in the prompt and necessary to the task. Test cases may remain controller-only; acceptance requirements may not be hidden. Controller-only test paths must not collide with files in the fixed project snapshot.

If a production run exposes a prompt/verifier/fixture mismatch, preserve its artifacts and provider usage for audit, mark it `evaluation_validity: invalid-fixture` and `status: excluded`, and prohibit baseline reuse or token comparison. Repair the contract under a new version and fingerprint rather than changing the historical result.

## Software-quality standard

Token improvement is eligible only after correctness and independent quality are classified.

| Quality dimension | Required check |
|---|---|
| Functional correctness | Structured concealed outcomes cover every task on the final cumulative repository. |
| Diagnostic fidelity | Repair/review tasks preserve the failure type, relevant location, and actionable evidence when required. |
| Code quality | Final diff is minimal, conventional, and does not bypass validation. |
| Maintainability | New abstractions, config, and generated files are justified. |
| Safety/security | Trust boundaries, secrets, permissions, and sandbox changes are reviewed when touched. |
| Reviewability | Final diff, verifier output, provider usage, and treatment evidence are inspectable. |

Use the five-point quality scale only after deterministic outcomes are recorded and an independent review is complete:

| Score | Meaning |
|---:|---|
| 0 | Unusable or no accepted task outcome. |
| 1 | Partial progress with major missing requirements. |
| 2 | Material production-quality or compatibility defects. |
| 3 | Acceptable implementation with no major blocker. |
| 4 | Good, minimal, production-compatible implementation. |
| 5 | Robust, minimal, and clearly stronger than the baseline result. |

Before review, use `quality_review_status: not-reviewed`, `quality_score: null`, and do not accept the run for an objective claim.

## Lean metric policy

Required records intentionally exclude metrics that cost substantial storage, prompting, or manual review without changing the core conclusion. Latency, setup/index time, turns, tool calls, stale-context incidents, overfeeding, and rediscovery are optional diagnostics, not publication gates.

Do not ask the agent for extra reporting to collect these metrics. When a specific failure requires diagnosis, derive what is already available from raw controller/provider events.

## Replication and reporting

- One replicate is one complete multi-task workflow execution.
- A single replicate is retained and labeled screening evidence; it is not confused with a single task.
- Additional compatible replicates add evidence rather than replace earlier runs.
- Pair baseline and treatment by comparison identity and replicate index.
- Run additional replicates as token budget permits; report every observed pair rather than waiting months before exposing evidence.
- Report individual pair effects first. Add median and range when repeated pairs exist.
- Never rank treatments from incomparable protocols or quality-rejected token deltas.
- Keep failed and excluded sessions with explicit reasons.
