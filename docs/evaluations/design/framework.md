# Evaluation framework

## Purpose

This framework measures **weighted token cost** across realistic software-engineering workflows. Correctness, verifier outcomes, and final software quality are reported as separate diagnostics; they do not determine which operationally valid token samples count.

Monetary cost estimation is out of scope. Token use is the resource metric.

## Practical objective

The program should answer:

> For a normal-user treatment configuration, how does weighted token cost change relative to the compatible retained baseline?

The answer must be scoped to the frozen workflow, model condition, and treatment estimand. The project does not need a language-by-language matrix to be useful.

## Primary workflow coverage

The target lifecycle workflow is one persistent sequence containing:

1. **Feature implementation** — add user-visible behavior under existing project conventions.
2. **Behavior-preserving refactor** — improve structure without changing required behavior.
3. **Code review and correction** — inspect a realistic cumulative change, identify acceptance-critical defects, and correct them when required.

Optional lanes may cover maintenance regression repair, diagnosis, migration, build repair, or documentation. The active Fastify and Beets sequences are Lifecycle V2 production evidence: each task pre-seeds an authentic semantic regression and presents a normal engineering objective that expects a complete correct implementation through repository discovery. All tasks require controller-only affected-component compilation plus one narrow essential-behavior smoke, and the workflow ends with project-wide compilation. Broader tests, behavioral fidelity, style, exact source shape, and source review are diagnostics. The agent is never instructed to optimize for the internal acceptance policy. These sequences remain scoped workflow samples rather than the whole target population.

## Primary evaluation unit

The canonical unit is a `workflow_session`:

- one repository fixture and initial snapshot;
- one ordered multi-task sequence;
- one baseline or treatment profile;
- one runtime/model condition;
- persistent repository, agent, and permitted tool state across tasks;
- weighted token cost across the complete sequence.

**One replicate is one complete workflow session, not one task.** A three-task workflow executed once has three task outcomes and one replicate.

Baseline and treatment sessions start from the same frozen inputs. State resets before a session, not between tasks, unless the sequence intentionally models a reset.

## Evidence progression

| Stage | Required evidence | Decision use |
|---|---|---|
| `source-logic` | Representative implementation inspected; mechanism, fallbacks, state, and compatibility mapped. | Candidate qualification. |
| `benchmark-audit` | Existing harness, scoring, accounting, raw output, and exclusions inspected. | Protocol design and background evidence. |
| `reproduction` | Frozen workflow execution with provider token accounting, structured task-verifier diagnostics, isolation, and recoverable artifacts; independent review is optional context. | Scoped token evidence. |

A single reproduction is screening evidence. A scoped estimate requires a pre-registered sample of N odd replicates reported as a median with its spread; see [ADR 0007](../../architecture/decision-records/0007-ranked-reporting-and-median-sampling.md). The record still does not pretend a sample of two workloads is a population estimate, but it does publish the ordering those samples support.

## Lean decision metrics

Canonical records require only evidence that directly changes the token-versus-correctness conclusion:

| Group | Required evidence |
|---|---|
| Token use | Weighted token cost (`fresh + 0.1 × cached + 6 × output`) as the sole metric; provider counters retained only as calculation/audit telemetry. |
| Task outcome | Operational exit, agent-declared completion, concealed-verifier exit, and accepted status for every task. |
| Model-behavior diagnostics | Concealed-verifier outcomes for every task; optional independent review status, quality score, critical failures, and final diff/status. |
| Treatment validity | Frozen treatment profile, documented installation/configuration evidence, and tool-isolation audit. Observed use is optional descriptive telemetry. |
| Integrity | Frozen protocol, source/runtime identities, compact artifacts, and checksums. |

The following are not required decision metrics: monetary cost, latency, setup/index timing, broad turn/tool-call telemetry, manually scored stale-context incidents, overfeeding notes, or rediscovery counts. Raw event evidence may be inspected for a targeted diagnosis without expanding every canonical record.

Operational retry count remains attached to a task because retries directly contribute to measured token use.

## Concealed verification contract

1. Every task has a controller-owned verifier or an explicitly declared non-deterministic review contract.
2. All concealed task verifiers run against the final cumulative repository, even when an earlier verifier fails.
3. The controller emits one structured result per task: task ID, order, verifier exit code, pass/fail, and accepted status.
4. `tasks_passed` is derived from those structured outcomes; it is never inferred as all-or-zero from one aggregate exit code.
5. Missing or duplicate structured results fail closed.
6. Independent source-quality review remains separate from prompt/verifier correctness.

## Treatment estimands

Treatment configuration is part of the causal question. Lifecycle-v0 production execution uses **available/natural-use** profiles: faithfully install every tool-author-recommended normal integration surface and allow it to operate naturally. That normal surface may include product-authored instructions, rules, skills, hooks, wrappers, proxies, MCP exposure, or other host integration. Evaluator-authored treatment-tool steering is forbidden, but neutrality must never remove, suppress, or contradict product-authored guidance. Server-only, guidance-free, or otherwise reduced setups are explicit ablations rather than canonical product treatments.

Lifecycle V2 prompts state the observable symptom and expected behavior while leaving repository search, file selection, and implementation strategy to the agent. They must not prescribe target files, symbols, implementation steps, controller checks, or stop conditions. Compatible baseline and treatment sessions receive identical prompt bytes and must not require or prefer treatment-tool invocation.

Prompted preferred/direct-use and mandatory-use profiles describe distinct historical estimands, but they are not runnable production profiles in lifecycle v0 and must not be proposed as a remedy for low or unobserved explicit invocation. Historical records retain their original labels rather than being silently rewritten.

An explicit model-issued command count is not a universal uptake metric. Integrations may act through hooks, wrappers, proxies, instruction layers, or host/tool-result transformations. Infer mechanism activity only from instrumentation that is complete for the frozen integration contract; otherwise report the assignment-level token comparison without converting command-string absence into a no-effect claim.

## Protocol identity and cumulative evidence

Evidence is append-only:

- New compatible runs add evidence; they are not replacement runs.
- A prior run is excluded only for a demonstrated defect in its frozen contract, isolation, accounting, or artifacts.
- Negative, failed, and zero-use sessions remain recorded.
- Protocol files retain full implementation hashes for provenance.
- Comparison-pool identity is derived only from causal/model-visible inputs: fixture and seed, prompts, verifiers, model condition, treatment configuration, runtime image, and isolation.
- Reporting, registry, validator, or schema-only code changes do not split a comparison pool.
- A causal input change mints a new comparison identity; earlier evidence remains valid under its original scope.

This permits statistical evidence to accumulate over months without making every framework repair a forced rerun.

## Interpretation rules

1. Compare weighted token cost for compatible complete workflow sessions first; do not condition the metric on task acceptance.
2. Report token components separately when available; do not convert them to money.
3. Report correctness and independently reviewed quality as diagnostic outcomes alongside the token result, not as sample-selection gates.
4. Hard-lane correctness and token efficiency are separate outcomes.
5. A treatment is valid when it is installed and configured according to its documented normal-user instructions and the lane remains isolated. The estimand is availability/configuration (intent-to-treat); observed invocation is not required and must not gate, filter, or trigger reruns.
6. Overlapping surface owners are invalid unless the overlap is explicitly disabled and verified.
7. Single-replicate results are labeled screening evidence, not erased.
8. Additional replicates should be paired to the same comparison identity and accumulated as budget permits.
9. Candidate/profile expansion stays paused until framework consolidation is complete; candidate reduction follows consolidation.

## Storage

`data/workflow-sessions.json` is the compact decision index. Recoverable evidence lives under `sources/evaluations/workflow-sessions/<session-id>/`. Historical single-run records in `data/evaluations.json` remain debugging or sanity evidence unless a report explicitly says otherwise.
