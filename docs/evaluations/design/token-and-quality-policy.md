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

Codex exec emits cumulative thread totals, not isolated turn deltas. For one persistent thread, the session total is the final `turn.completed.usage` snapshot and each task increment is the current snapshot minus the previous snapshot. For multiple distinct threads, sum one final snapshot per thread. Summing repeated snapshots from the same thread double-counts prior work and is forbidden.

## Required token fields

Record these when the provider exposes them:

| Field | Meaning |
|---|---|
| `fresh_input_tokens` | Non-cached input tokens. |
| `cached_input_tokens` | Cache-read input tokens. |
| `cache_write_tokens` | Provider-reported cache-write tokens; normalize to integer `0` for OpenAI Codex because its usage events expose cache reads but no cache-write category. |
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

Every controller verifier runs against the final cumulative repository, regardless of earlier failures. The historical Baseline V2 and active Baseline V3/V4 zero-mistake generations keep their complete focused acceptance assertions model-visible and check candidate copies against integrity-bound canonical bytes; earlier generations may use concealed assertions. Record for each task:

- `task_id` and `order`;
- agent operational exit and declared-completion state;
- `verifier_exit_code`;
- `verifier_passed`;
- `accepted`.

`tasks_passed` is the count of tasks whose structured `accepted` value is true. Missing outcomes fail closed; the aggregate verifier exit is not used to synthesize all-or-zero task counts.

### Estimand-aligned eligibility

The research objective is provider-reported workflow token usage under fair, disclosed software-engineering tasks. An operationally complete, integrity-valid provider run is eligible regardless of whether the sampled model passes the controller verifiers.

Solution-directed task assistance is permitted and preferred when it reduces irrelevant search, validation, and correction variance. The frozen prompt may disclose the intended solution path, exact focused checks, environment constraints, and stop condition, provided the same recipe is used for compatible baseline and treatment sessions and must not require or prefer treatment-tool invocation. This project does not use solution discovery as a model-intelligence outcome.

A verifier may enforce disclosed observable behavior, compatibility, safety, and explicitly public structural contracts. It must not require canonical prose, local parameter names, source identity, or one implementation shape unless that exact requirement is disclosed and necessary. Verifier outcomes are recorded as model-behavior diagnostics, not used to select which token samples count.

Repair prompt/verifier/fixture mismatches in the sole v0 contract. Mark runs produced by an invalid fixture `evaluation_validity: invalid-fixture` and exclude them. Never replace an otherwise valid run merely because model output failed or received a low review score.

## Software-quality diagnostics

Correctness and independent quality are classified to interpret each token sample; they do not determine whether the provider usage is retained.

| Quality dimension | Diagnostic check |
|---|---|
| Functional correctness | Structured concealed outcomes cover every task on the final cumulative repository. |
| Diagnostic fidelity | Repair/review tasks preserve actionable evidence when required. |
| Code quality | Final diff is conventional and does not bypass validation. |
| Maintainability | New abstractions, config, and generated files are assessed. |
| Safety/security | Trust boundaries, secrets, permissions, and sandbox changes are reviewed when touched. |
| Reviewability | Final diff, verifier output, provider usage, and treatment evidence remain inspectable. |

Quality scores are optional diagnostics after deterministic outcomes are recorded. Before review, use `quality_review_status: not-reviewed` and `quality_score: null`; the run remains eligible for the token objective when its execution and integrity are valid.

## Lean metric policy

Required records intentionally exclude metrics that cost substantial storage, prompting, or manual review without changing the core conclusion. Latency, setup/index time, turns, tool calls, stale-context incidents, overfeeding, and rediscovery are optional diagnostics, not publication gates.

Do not ask the agent for extra reporting to collect these metrics. When a specific failure requires diagnosis, derive what is already available from raw controller/provider events.

## Replication and reporting

- One replicate is one complete multi-task workflow execution.
- A single replicate is retained and labeled screening evidence; it is not confused with a single task.
- Retain the first operationally valid provider sample for each protocol/replicate; additional compatible replicates add evidence rather than replace earlier runs.
- Pair baseline and treatment by comparison identity and replicate index.
- Report every valid observed pair, including verifier failures and low-quality outputs, with those outcomes clearly labeled.
- Never rank treatments from incomparable or fixture-invalid protocols. Do not discard a compatible pair because model quality differs.
