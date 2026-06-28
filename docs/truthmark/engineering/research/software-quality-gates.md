---
status: active
truth_kind: engineering-contract
last_reviewed: 2026-07-09
---

# Software Quality Gates

## Purpose

This doc owns the durable software-quality gates for token-optimization evaluations.

It prevents token reduction from being counted as success when quality, diagnostics, or reviewability degrade.

## Scope

This doc covers correctness, diagnostics, maintainability, safety, and reviewability gates.

Token-accounting mechanics are owned by `token-accounting.md`.

## Current Implementation Behavior

- Evaluation docs require token savings to be paired with software-quality evidence.
- The evaluator prompt and templates ask for verifier, diagnostic, maintainability, safety, and reviewability records.
- Workflow runners record deterministic verifier success separately from software-quality review status.

## Product Truth Links

- None. This is an engineering research contract, not product truth.

## Contract Surface

- Quality gates for benchmark-audit and reproduction evaluation records.

## Inputs

- Code diffs, verifier output, diagnostic logs, run records, safety observations, and review notes.

## Outputs

- Quality scores, pass/fail or blocked status, diagnostic-preservation notes, and invalidation reasons.


## Contract

- Evaluation success requires task completion, not only lower token use.
- Relevant verifier commands should be recorded with pass, fail, or blocked status.
- Critical diagnostic lines must remain recoverable when output is compacted.
- Diffs should be minimal, focused, and reviewable.
- Evaluation artifacts should preserve reset or uninstall paths for installed tools and profiles.
- Safety review includes secrets, permissions, network behavior, and credential handling.
- Quality scoring should explain partial success and under-solving.
- Deterministic verifier success does not assign an ordinal quality score.
- Unreviewed runs keep `quality_score` null and remain ineligible for objective acceptance.
- Objective acceptance requires a recorded review, score at least 4, and no critical failures.

## Engineering Decisions

- Decision (2026-06-26): Token savings must be paired with software-quality gates.
- Decision (2026-06-26): Diagnostic preservation is an evaluation concern, not just a tooling convenience.
- Decision (2026-06-26): A failed verifier or unreviewable diff can invalidate an apparent token-saving result.
- Decision (2026-07-09): Mechanical acceptance is a functional execution gate; software-quality scores require an explicit review.

## Rationale

Aggressive context reduction can hide root-cause evidence or shorten work by skipping necessary investigation.

Quality gates keep benchmark results useful for real coding agents.

## Non-Goals

- This doc does not define every benchmark fixture.
- This doc does not replace project-specific test suites.
- This doc does not score a run without run artifacts.

## Maintenance Notes

- Update this doc when quality scoring or diagnostic preservation rules change.
- Use `practical-software-quality-reviewer` after benchmark or reproduction runs.
- Keep this doc aligned with `docs/evaluations/token-usage-and-quality-standards.md`.

## Source References

- ../../../../docs/evaluations/token-usage-and-quality-standards.md
- ../../../../docs/evaluations/evaluation-framework.md
- ../../../../docs/evaluations/immediately-usable-flows.md
- ../../../../templates/evaluation-record.md
- ../../../../templates/evaluation-run-record.json
- ../../../../prompts/evaluator.md
- ../../../../.agents/skills/practical-software-quality-reviewer.md
