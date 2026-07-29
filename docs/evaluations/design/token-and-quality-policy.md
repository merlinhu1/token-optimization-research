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

Every controller verifier runs against the final cumulative repository, regardless of earlier failures. The active Lifecycle V1 generation keeps one affected-component compile command per task and one final project-wide compile command controller-only and injects no acceptance-test assets. Per-task component compilation and final project compilation are the sole internal pass/fail gates; tests, behavior, style, and source-review quality are diagnostics only. Historical Baseline V2/V3/V4 assertions remain immutable evidence for their executed protocols. Record for each task:

- `task_id` and `order`;
- agent operational exit and declared-completion state;
- `verifier_exit_code`;
- `verifier_passed`;
- `accepted`.

`tasks_passed` is the count of tasks whose structured `accepted` value is true. Missing outcomes fail closed; the aggregate verifier exit is not used to synthesize all-or-zero task counts.

### Estimand-aligned eligibility

The research objective is provider-reported workflow token usage under fair, disclosed software-engineering tasks. An operationally complete, integrity-valid provider run is eligible regardless of whether the sampled model passes the controller verifiers.

Lifecycle V1 prompts describe complete software-engineering objectives and expect the agent to implement them correctly through normal repository search, related-code inspection, and relevant validation. They do not disclose controller scoring or compile commands. Compatible baseline and treatment sessions must use identical prompt bytes and internal verifier commands and must not require or prefer treatment-tool invocation. Historical **Solution-directed task assistance** generations remain valid only for their frozen protocols.

The Lifecycle V1 verifier internally enforces affected-component compilation plus the frozen project-wide compile command after task 3. Unit tests, behavioral fidelity, style, maintainability, and source review may still be recorded, but they are diagnostics and cannot change task pass/fail or select which provider-token sample counts. This internal quality-assessment policy must not be presented as an instruction to the agent.

Repair prompt/verifier/fixture mismatches in the sole v0 contract. Mark runs produced by an invalid fixture `evaluation_validity: invalid-fixture` and exclude them. Never replace an otherwise valid run merely because model output failed or received a low review score.

## Software-quality diagnostics

Correctness and independent quality are classified to interpret each token sample; they do not determine whether the provider usage is retained.

| Quality dimension | Diagnostic check |
|---|---|
| Functional correctness | Lifecycle V1 records affected-component compilation as the acceptance gate; broader behavior and tests are diagnostic. |
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
