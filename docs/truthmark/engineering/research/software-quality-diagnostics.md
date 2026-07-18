---
status: active
truth_kind: engineering-contract
last_reviewed: 2026-07-16
---

# Software Quality Diagnostics

## Purpose

Define software-quality evidence as diagnostic context for the repository's primary objective: provider-reported workflow token usage.

## Scope

This contract covers concealed-verifier outcomes, optional source review, quality scores, and the boundary between sampled model behavior and experiment invalidity.

## Current Implementation Behavior

- Workflow records retain structured verifier outcomes for every task.
- `quality_review_status` and `quality_score` are optional diagnostics.
- Runner, matrix, and repository validation accept operationally valid provider samples without requiring verifier success or review.
- Baseline reuse keeps the first valid sample for each causal protocol fingerprint and replicate.

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

- Verifier and review outcomes describe the model behavior observed in a retained sample.
- Model quality does not gate token accounting, baseline reuse, or baseline/treatment pairing.
- Keep the first operationally valid provider sample for each frozen causal protocol and replicate, even when its verifier fails or review score is low.
- Never rerun merely to obtain passing code or a better review score; that selects on model performance and biases token evidence.
- Exclude and rerun only for fixture/contract invalidity, missing or corrupt provider usage, broken isolation/integrity, or operationally incomplete prompt execution.
- Record verifier pass/fail/blocked status and structured task outcomes without converting them into eligibility gates.
- Independent review is optional diagnostic evidence. Unreviewed runs keep `quality_score: null` but remain token-eligible when execution integrity is valid.
- Prompt and verifier requirements target disclosed public behavior, compatibility, or safety—not canonical private symbols or one hidden implementation shape.
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
