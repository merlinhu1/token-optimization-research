# Phase 2 benchmark and evaluation plan

## Objective

Determine whether a declared AI-agent treatment reduces cumulative provider-reported token use over a persistent software-engineering workflow while preserving structured task correctness and independent software quality.

Monetary cost estimation is excluded.

## Current program order

1. **Complete:** consolidate and freeze the evaluation framework.
2. **Complete:** reconcile historical treatment estimands and result dispositions.
3. **Complete for the first screen:** reduce the runnable treatment portfolio to `retrieval-codegraph`; defer every other unexecuted candidate.
4. **Complete:** replace the invalid calibration contract with executable-qualified `beets-lifecycle-sequence-v2`.
5. **In progress:** complete and independently review the current production baselines for Beets lifecycle V2, Fastify maintenance V1, and Terraform maintenance V2.
6. After baseline eligibility is established per lane, freeze and run matched treatments only where the baseline passed independent quality review; accumulate later replicates only as token budget permits.

Do not add or reactivate profiles without a concrete mechanism gap or first-screen evidence.

## Workflow portfolio

### Current production maintenance lanes

Fastify maintenance V1 and Terraform maintenance V2 are current production workflows. Existing and future compatible executions accumulate evidence for that task class; failed independent quality review excludes a run from comparison without retiring the lane.

### Current production lifecycle lane

Qualify one persistent sequence containing:

| Order | Task | Acceptance focus |
|---:|---|---|
| 1 | Feature implementation | Required behavior, compatibility, tests, and project conventions. |
| 2 | Behavior-preserving refactor | Preserved behavior, reduced structural debt, and minimal diff. |
| 3 | Code review and correction | Correct findings against the cumulative change; acceptance-critical defects corrected. |

This single lifecycle triad is intended to cover common software-engineering work without multiplying experiments by language. Repository choice is based on verifier quality and realistic project structure, not language coverage.

Optional lanes may cover repair, diagnosis, migration, build/typecheck, or documentation when a candidate mechanism specifically targets them.

## Framework freeze gate

Before any paid run, the frozen contract must prove:

- conflict-free seed application and a qualified initial state;
- exact prompt, seed, and verifier bytes;
- future-prompt concealment and controller-only verifier assets;
- no controller-only path collides with a file in the fixed project snapshot;
- acceptance checks enforce only disclosed observable/public contracts, never canonical prose or undisclosed local names;
- model/runtime/treatment identity;
- model shell/network and treatment isolation;
- every task verifier runs without short-circuiting;
- structured task-result parsing fails closed on missing/duplicate outcomes;
- the complete fixed state passes every acceptance point;
- compact artifact creation and checksum recovery work;
- reporting-only runner changes cannot split the comparison pool.

Protocol qualification and mutation testing use no provider tokens and should absorb framework risk before a months-long evidence program begins.

## Treatment estimands

Profiles must state one of:

- normal integration available for natural use;
- documented direct use preferred through model-facing guidance;
- mandatory-use policy;
- integrated broad owner.

The profile must install the corresponding normal integration. Merely mounting a binary cannot be described as automatic shell integration. Historical prompted/direct-use evidence remains valid for that narrow estimand when isolation is valid.

## Lean run design

1. Freeze fixture, sequence, prompts, seeds, verifiers, comparison identity, and selected treatment.
2. Start baseline and treatment from the same frozen inputs.
3. Reset repository, profile home, tool state, and agent home before each complete session.
4. Preserve permitted state between tasks.
5. Deliver one task prompt at a time.
6. Permit the treatment exactly as declared; block overlapping tools and external retrieval unless part of both arms.
7. Capture provider token events and controller artifacts without asking the model for extra reporting.
8. Run all concealed verifiers once against the final cumulative repository.
9. Emit structured per-task results and derive `tasks_passed` from them.
10. Perform independent source-quality review.
11. Append the compact record and checksum-valid artifact bundle.

## Required decision evidence

- provider token components and total;
- per-task operational, declared-completion, verifier, and accepted state;
- independent quality score and critical failures;
- treatment installation/configuration and isolation audit, with optional descriptive use telemetry;
- frozen protocol and recoverable artifacts.

Latency, money, setup/index time, turns, tool calls, and broad behavior annotations are not required. They may be derived from existing raw events only when diagnosing a concrete result.

## Replication policy

One replicate means one complete multi-task workflow execution.

- Record each run immediately.
- A valid single replicate is screening evidence, not a single-task result and not discarded.
- New compatible runs add evidence; they do not replace earlier runs.
- Pair baseline and treatment by comparison identity and replicate index.
- Add replicates over time as token budget allows.
- Report each pair. Add median and range once repeated pairs exist.
- Do not demand an expensive full matrix before publishing a scoped status such as `single-run-screening` or `insufficient-evidence`.

## Advancement rule

A treatment may support a positive token-efficiency conclusion only when:

- operational execution completes;
- agent-declared completion is recorded;
- every task has a structured verifier outcome;
- correctness is no worse than the comparison baseline;
- independent quality is accepted and no critical failure exists;
- the declared treatment was correctly installed and configured according to its normal documented instructions;
- treatment isolation and provider-token accounting are trustworthy;
- the comparison baseline is compatible;
- the claim states replicate count and workflow scope.

Hard-lane correctness improvement may be reported separately even when token use increases or production quality remains rejected.
