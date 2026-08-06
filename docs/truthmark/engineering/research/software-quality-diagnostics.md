---
status: active
truth_kind: contract
doc_type: contract
source_of_truth:
  - ../../../../docs/evaluations/design/token-and-quality-policy.md
  - ../../../../scripts/run_codex_workflow_evaluation.py
last_reviewed: 2026-08-01
---

# Software Quality Diagnostics

## Purpose

Define software-quality evidence as diagnostic context for the repository's primary objective: provider-reported workflow token usage.

## Scope

This contract covers Lifecycle V1 compile acceptance, broader software-quality diagnostics, optional source review, quality scores, and the boundary between sampled model behavior and experiment invalidity.

## Current Implementation Behavior

- Workflow records retain structured affected-component compile outcomes for every task and one final project-wide compile outcome.
- Component compilation gates per-task acceptance; final project compilation gates workflow acceptance and treatment unlock.
- Unit tests, behavioral fidelity, style, maintainability, exact source shape, `quality_review_status`, and `quality_score` are optional diagnostics.
- Runner, matrix, and repository validation retain the first operationally valid provider token sample even when compilation or broader quality diagnostics fail.
- Baseline reuse for token accounting keeps that first valid sample; treatment launch still requires the Lifecycle V1 compile gate to pass.

## Product Truth Links

- None. This is an engineering research contract, not product behavior.

## Contract Surface

- `scripts/run_codex_workflow_evaluation.py`
- `scripts/run_sequential_workflow_matrix.py`
- `scripts/validate_repository.py`
- `data/workflow-sessions.json`

## Inputs

Provider execution status, structured verifier output, final diffs, isolation/integrity audits, and optional independent review notes.

## Outputs

Token-eligibility state plus separately recorded model-behavior diagnostics.

## Contract

- Lifecycle V1 compile outcomes determine task/workflow acceptance and treatment unlock; they do not determine token-sample retention.
- Broader tests and review outcomes describe the model behavior observed in a retained sample and never gate token accounting.
- Keep the first operationally valid provider sample for each frozen causal protocol and replicate, even when compilation fails or the review score is low.
- Never rerun merely to obtain compiling code or a better review score; that selects on model performance and biases token evidence.
- Exclude and rerun only for fixture/contract invalidity, missing or corrupt provider usage, broken isolation/integrity, or operationally incomplete prompt execution.
- Record component and project compile pass/fail status separately from optional broader quality diagnostics.
- Independent review is optional diagnostic evidence. Unreviewed runs keep `quality_score: null` but remain token-eligible when execution integrity is valid.
- Lifecycle V1 prompts state the requested engineering outcome and expect correct implementation; affected-component compile commands and scoring policy remain controller-only.
- Preserve diagnostics, final diffs, safety observations, and review notes so token effects can be interpreted alongside observed behavior.

## Rationale

The study estimates token usage, not model pass rate. Model behavior varies between sessions; rerunning failed outputs until they pass changes the sample and corrupts the token estimand.

## Compatibility Rules

The following invalidate the experiment rather than describe model quality:

- prompt/verifier mismatch or concealed undisclosed requirements;
- fixture corruption or wrong controller assets;
- incomplete provider usage;
- failed isolation or verifier-integrity audit;
- operational failure preventing completion of the full prompt sequence.

## Maintenance Notes

Keep this document aligned with the runner, matrix, validator, and token-accounting contract. Quality tooling may become stricter diagnostically without becoming a token-eligibility gate.

## Source References

- ../../../../docs/evaluations/design/token-and-quality-policy.md
- ../../../../docs/evaluations/operations/runner-reference.md
- ../../../../scripts/run_codex_workflow_evaluation.py
- ../../../../scripts/run_sequential_workflow_matrix.py

## Product Decisions

Provider-token eligibility and software-quality diagnostics remain separate: compile and verifier outcomes are retained alongside token accounting but do not justify hidden reruns or result selection.
