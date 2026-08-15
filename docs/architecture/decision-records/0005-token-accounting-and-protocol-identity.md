# ADR 0005: Bind Token Comparisons to Protocol Identity

## Status

Accepted. The first-valid-sample rule this document assumed is superseded by
[`0007-ranked-reporting-and-median-sampling.md`](0007-ranked-reporting-and-median-sampling.md);
protocol-identity minting is unchanged.

## Context

A single monotonic provider receipt and a compatible baseline binding are what separate
accounting integrity from a causal efficiency claim. Without them, a token delta can come from
a changed task rather than a changed tool.

Token comparisons therefore use one final monotonic cumulative provider snapshot per distinct
thread and compare only compatible baseline pools. Those counters are telemetry inputs. The sole
reported metric is weighted token cost:

`fresh_input_tokens + 0.1 * cached_input_tokens + 6 * output_tokens`

Reasoning tokens are a subset of output tokens and are not added again. Raw provider totals are
never a primary, secondary, comparison, ranking, or presentation metric.

## Decision

- Decision (2026-08-13): A behaviorally inert seed or a model-facing prompt change mints new
  qualification and protocol identities. Completed sessions and their protocol bytes remain
  historical, and treatment gates close until the revised contract receives its own pilot.
- Decision (2026-08-15): Weighted token cost is the repository's only token evaluation metric.
  Provider counters remain auditable telemetry solely to calculate and verify that value.
- Decision (2026-08-15): Lifecycle V1 task acceptance adds one narrow essential-behavior smoke
  to feature and refactor tasks while review tasks remain compile-only. This verifier-contract
  change mints new qualification and protocol identities without changing prompt bytes or
  weighted-token sample-retention eligibility.
- Decision (2026-08-15): New Codex CLI and OpenCode protocols use GPT-5.6 Sol at medium effort;
  new Claude Code protocols use direct-Anthropic Claude Opus 5 at medium effort. High-effort
  conditions remain historical only because excess deliberation can increase trajectory
  divergence. A model or effort change mints a new protocol identity.

## Consequences

- Editing a task prompt is not a cosmetic change: it re-freezes protocols and invalidates any
  replication authority still bound to the previous protocol bytes.
- Completed runs stay valid as evidence for the task bytes they actually ran against, and are
  not authorization for a corrected contract.
- A corrected task family reopens the pilot requirement before any paid treatment.

This is the rule behind the Lifecycle V1 r1 replication authority refusing to load after the
2026-08-13 task-family correction: the authority names superseded protocol identities, so
`plan_workflow_jobs` blocks rather than planning against them. See
`sources/evaluations/audits/lifecycle-v1-corrected-task-family-readiness-20260813.json`.

## Provenance

Migrated 2026-08-14 from `docs/truthmark/engineering/research/token-accounting.md` when the
Truthmark workflow was removed. Operational detail lives in
[`../../evaluations/design/token-and-quality-policy.md`](../../evaluations/design/token-and-quality-policy.md)
and `AGENTS.md`.
