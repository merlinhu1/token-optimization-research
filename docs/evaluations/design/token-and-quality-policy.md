# Token usage and software quality standards

## Metric authority

The project always and only evaluates **weighted token cost**:

`weighted_token_cost = fresh_input_tokens + 0.1 × cached_input_tokens + 6 × output_tokens`

This is the sole token value used in results, comparisons, deltas, medians, rankings, charts, and
narrative claims. Reasoning tokens are already included in output tokens and are never added
again. Raw provider counters and reconstructed totals are internal telemetry inputs only: retain
them when needed to calculate or audit the weighted value, but never present or interpret a raw
token total as an evaluation metric. The project does not estimate or report monetary cost.

## Accounting boundary

Token claims must name their accounting boundary:

| Boundary | Definition | Accepted use |
|---|---|---|
| `artifact_estimated` | Tokenizer estimate for one static artifact before and after transformation. | Reducer sanity checks only. |
| `request_estimated` | Estimated tokens for one model request when provider records are unavailable. | Local diagnosis only. |
| `provider_reported_request` | Provider-reported usage for one request, including cache components when exposed. | Request diagnosis. |
| `provider_reported_task` | Provider-reported usage across one task. | Optional workflow diagnosis. |
| `workflow_session_weighted` | Weighted token cost across the complete persistent task sequence, including model-visible setup, retries, and corrections. | Sole evaluation metric. |

The canonical metric is `workflow_session_weighted`. Estimated artifact/request counts and raw provider totals cannot establish a workflow saving.

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
| `weighted_token_cost` | `fresh_input_tokens + 0.1 × cached_input_tokens + 6 × output_tokens`; the only reported token value. |
| `measurement_source` | Provider event/log source used for extraction. |
| `accounting_basis` | Provider telemetry boundary and the canonical weighted formula. |

No monetary-cost field is required or produced.

## Derived metrics

Use only weighted formulas:

- `workflow_weighted_change = treatment_weighted_token_cost - baseline_weighted_token_cost`
- `workflow_weighted_reduction_ratio = 1 - treatment_weighted_token_cost / baseline_weighted_token_cost`

Artifact/request token estimates are diagnostics, not evaluation metrics, and are not published as token results.

## Structured task outcomes

Every controller verifier runs against the final cumulative repository, regardless of earlier failures. The active Lifecycle V2 generation keeps its acceptance commands controller-only and injects no acceptance-test assets. Every task requires affected-component compilation plus one narrow essential-behavior smoke check, and the workflow ends with project-wide compilation. The smoke checks cover only the task's stated core behavior, admit coherent alternative implementations, and reject missing or seriously flawed repairs. Broader tests, behavior, style, and source-review quality are diagnostics only. Historical Baseline V2/V3/V4 assertions remain immutable evidence for their executed protocols. Record for each task:

- `task_id` and `order`;
- agent operational exit and declared-completion state;
- `verifier_exit_code`;
- `verifier_passed`;
- `accepted`.

`tasks_passed` is the count of tasks whose structured `accepted` value is true. Missing outcomes fail closed; the aggregate verifier exit is not used to synthesize all-or-zero task counts.

### Estimand-aligned eligibility

The research objective is weighted token cost calculated from provider telemetry under fair, disclosed software-engineering tasks. An operationally complete, integrity-valid provider run is eligible regardless of whether the sampled model passes the controller verifiers.

Lifecycle V2 prompts describe complete software-engineering objectives and expect the agent to implement them correctly through normal repository search, related-code inspection, and relevant validation. They do not disclose controller scoring or compile commands. Compatible baseline and treatment sessions must use identical prompt bytes and internal verifier commands and must not require or prefer treatment-tool invocation. Historical **Solution-directed task assistance** generations remain valid only for their frozen protocols.

The Lifecycle V2 verifier internally enforces per-task compilation and essential-behavior smoke plus the frozen project-wide compile command after the final prompt. Broader unit tests, behavioral fidelity beyond the essential smoke, style, maintainability, and source review may still be recorded, but they are diagnostics and cannot change task pass/fail or select which weighted-token sample counts. This internal quality-assessment policy must not be presented as an instruction to the agent.

Repair prompt/verifier/fixture mismatches in the sole v0 contract. Mark runs produced by an invalid fixture `evaluation_validity: invalid-fixture` and exclude them. Never replace an otherwise valid run merely because model output failed or received a low review score.

## Software-quality diagnostics

Correctness and independent quality are classified to interpret each token sample; they do not determine whether the provider usage is retained.

| Quality dimension | Diagnostic check |
|---|---|
| Functional correctness | Lifecycle V2 requires compilation and one essential-behavior smoke on every task; broader behavior/tests are diagnostic. |
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
- The **pilot gate** is unchanged and distinct from sampling: one first-valid qualifying run unlocks a campaign. Median-of-N governs the result sample, not the gate.
- **Replicate counts are chosen per protocol as the work warrants** ([ADR 0009](../../architecture/decision-records/0009-replicate-counts-are-chosen-not-registered.md)). There is no minimum, no parity requirement, no cap, and nothing to register in advance.
- A **single replicate is a screen, not an effect estimate**: it can support "not worth carrying forward", never a ranked effect size. State which claim you are making.
- **Where several replicates exist, the point estimate is the median weighted token cost** reported with its observed spread and its two-factor decomposition.
- Retain and publish all replicates, including verifier failures and low-quality outputs. A replicate is never dropped because its number is inconvenient.
- A replicate that fails **before** the provider boundary produced no measurement: replace it and retain its zero-spend receipt. A replicate whose agent performed badly produced a real token count and counts toward the median.
- **State how many replicates each arm holds** in every comparison. Optional stopping is managed by disclosure, so the count is part of the result.
- Pair baseline and treatment by comparison identity and explicit baseline binding. Raw `replicate_index` values are runtime-local; use a validated accepted-replicate ordinal when accepted labels differ across runtimes.
- Never compare across incomparable or fixture-invalid protocols. Do not discard a compatible pair because model quality differs.

## Ranking

Rankings are published. Withholding an ordering does not transfer uncertainty to the reader, it
transfers the judgement while pretending not to have one (see [ADR 0007](../../architecture/decision-records/0007-ranked-reporting-and-median-sampling.md)).

- A published ranking states its workload set, model conditions, N, and observed dispersion.
- Order tools by median delta against their matched baseline sample, within one workload and model condition.
- Where two tools' observed ranges overlap at the reported N, report them as **indistinguishable at that N** rather than ordering them.
- Aggregate across workloads only where the direction is consistent; where directions disagree, say so and rank per workload.
