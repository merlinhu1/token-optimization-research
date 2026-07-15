# Evaluation framework

## Purpose

This framework determines whether an AI-agent intervention reduces **cumulative provider-reported token use** across a realistic software-engineering workflow without reducing correctness or final software quality.

Monetary cost estimation is out of scope. Token use is the resource metric.

## Practical objective

The program should answer:

> For a normal-user treatment configuration, does the intervention reduce total provider token use per correctness-accepted workflow while preserving software quality?

The answer must be scoped to the frozen workflow, model condition, and treatment estimand. The project does not need a language-by-language matrix to be useful.

## Primary workflow coverage

The target lifecycle workflow is one persistent sequence containing:

1. **Feature implementation** — add user-visible behavior under existing project conventions.
2. **Behavior-preserving refactor** — improve structure without changing required behavior.
3. **Code review and correction** — inspect a realistic cumulative change, identify acceptance-critical defects, and correct them when required.

Optional lanes may cover maintenance regression repair, diagnosis, migration, build repair, or documentation. The existing Fastify, Terraform, and Beets sequences are maintenance-regression evidence. They remain valid within that scope; they are not treated as the whole target population.

## Primary evaluation unit

The canonical unit is a `workflow_session`:

- one repository fixture and initial snapshot;
- one ordered multi-task sequence;
- one baseline or treatment profile;
- one runtime/model condition;
- persistent repository, agent, and permitted tool state across tasks;
- cumulative provider token use across the complete sequence.

**One replicate is one complete workflow session, not one task.** A three-task workflow executed once has three task outcomes and one replicate.

Baseline and treatment sessions start from the same frozen inputs. State resets before a session, not between tasks, unless the sequence intentionally models a reset.

## Evidence progression

| Stage | Required evidence | Decision use |
|---|---|---|
| `source-logic` | Representative implementation inspected; mechanism, fallbacks, state, and compatibility mapped. | Candidate qualification. |
| `benchmark-audit` | Existing harness, scoring, accounting, raw output, and exclusions inspected. | Protocol design and background evidence. |
| `reproduction` | Frozen workflow execution with provider token accounting, structured task verification, independent quality review, isolation, and recoverable artifacts. | Scoped treatment evidence. |

A single reproduction is screening evidence. Confidence grows through additional compatible replicates; the record does not pretend that one run is a population estimate.

## Lean decision metrics

Canonical records require only evidence that directly changes the token-versus-correctness conclusion:

| Group | Required evidence |
|---|---|
| Token use | Fresh input, cached input, cache-write, output, reasoning, and total provider tokens when exposed; accounting source and reconstruction formula. |
| Task outcome | Operational exit, agent-declared completion, concealed-verifier exit, and accepted status for every task. |
| Final quality | Independent review status, quality score, critical failures, final diff/status. |
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

Treatment configuration is part of the causal question:

- **available/natural-use** — install the normal integration and allow the agent to use it naturally;
- **preferred/direct-use** — explicitly tell the agent to use the documented direct interface;
- **mandatory-policy** — require use and measure the complete policy;
- **integrated owner** — use a broader product-owned integration.

None is automatically invalid. Each must be predeclared and labeled. A prompted direct-use result cannot be presented as evidence for an unprompted automatic integration.

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

1. Compare cumulative provider token use per accepted workflow first.
2. Report token components separately when available; do not convert them to money.
3. Lower token use is not positive when correctness or independently reviewed quality is worse.
4. Hard-lane correctness rescue and token efficiency are separate outcomes.
5. A treatment is valid when it is installed and configured according to its documented normal-user instructions and the lane remains isolated. The estimand is availability/configuration (intent-to-treat); observed invocation is not required and must not gate, filter, or trigger reruns.
6. Overlapping surface owners are invalid unless the overlap is explicitly disabled and verified.
7. Single-replicate results are labeled screening evidence, not erased.
8. Additional replicates should be paired to the same comparison identity and accumulated as budget permits.
9. Candidate/profile expansion stays paused until framework consolidation is complete; candidate reduction follows consolidation.

## Storage

`data/workflow-sessions.json` is the compact decision index. Recoverable evidence lives under `sources/evaluations/workflow-sessions/<session-id>/`. Historical single-run records in `data/evaluations.json` remain debugging or sanity evidence unless a report explicitly says otherwise.
