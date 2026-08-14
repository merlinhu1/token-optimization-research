# ADR 0002: Grade Every Claim by Evidence Stage

## Status

Accepted

## Context

This repository studies practical agent tooling, where a product README can claim a large
reduction that no measurement supports. Without an explicit grading scheme, polished research
prose drifts away from what was actually inspected or measured, and a marketing claim and a
provider-metered result read the same in a report.

## Decision

- Decision (2026-06-26): The repository uses four evidence stages: `lead`, `source-logic`,
  `benchmark-audit`, and `reproduction`.
- Decision (2026-06-26): Source-logic is decision-bearing only for prioritization and
  stack-hypothesis formation.
- Decision (2026-06-26): Benchmark and reproduction wording requires benchmark or reproduction
  artifacts.
- Decision (2026-06-29): Tool dossiers distinguish pinned source snapshots from unpinned
  historical inspections; current upstream `HEAD` must not be substituted for an unrecorded
  historical commit.
- Decision (2026-06-30): Candidate validity requires auditable source versioning; unpinned
  historical dossiers can remain as limitations or refresh targets, not recommended components.
- Decision (2026-07-07): Reproduction evidence for recommendations is continuous workflow
  simulation with cumulative provider-billed accounting, not isolated single-task causal runs.

## Consequences

- A claim's wording is constrained by the artifacts behind it.
- Source inspection can rank work but cannot conclude an effect.
- An unpinned dossier is a refresh target, never a recommendation.

## Provenance

Migrated 2026-08-14 from `docs/truthmark/engineering/research/evidence-stages.md` when the
Truthmark workflow was removed. See
[`0006-repository-workflow-and-validation.md`](0006-repository-workflow-and-validation.md).
