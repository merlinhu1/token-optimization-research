---
status: active
truth_kind: engineering-contract
last_reviewed: 2026-06-30
---

# Evidence Stages

## Purpose

This doc owns the durable evidence-stage contract for token-optimization research claims.

The contract keeps reports from treating discovery leads, source inspection, benchmark audits, and reproduction evidence as interchangeable.

## Scope

This doc covers evidence-stage names, decision weight, and claim wording boundaries.

It does not own individual tool dossiers or raw source artifacts.

## Current Implementation Behavior

- `AGENTS.md` names the active evidence-stage taxonomy.
- Repository data files store tool and evaluation records that use the taxonomy.
- The validator rejects retired evidence-stage terminology.
- The validator requires tool dossiers to state whether their inspected source snapshot is pinned or historically unpinned.

## Product Truth Links

- None. This is an engineering research contract, not product truth.

## Contract Surface

- Evidence-stage names in repository instructions, data files, dossiers, reports, and validation.

## Inputs

- Research claims, dossier records, evaluation records, report drafts, and validator rules.

## Outputs

- Calibrated claim wording and decision weight for each evidence stage.


## Contract

- `lead` is discovery or backlog evidence only.
- A lead is not decision evidence for stack recommendations.
- `source-logic` is the minimum decision-bearing stage.
- Source-logic requires inspected implementation behavior, not README claims alone.
- Source-logic dossiers must record source snapshot metadata.
- A pinned source-logic dossier records an immutable commit or commit prefix.
- A historical GitHub `HEAD` inspection without a recorded commit must be marked `unpinned-historical-inspection` until refreshed.
- A repository without auditable source versioning for the inspected source is not a valid candidate for recommendation, stack construction, benchmark-audit, or reproduction.
- `benchmark-audit` requires benchmark harness, task, scoring, token accounting, and raw-output evidence to be inspected.
- `reproduction` requires an independent target-workload run with provider-billed accounting and software-quality gates.
- Report claims must name or imply only the evidence stage that has actually been reached.
- Stack recommendations stay hypotheses until benchmark-audit or reproduction evidence exists.

## Engineering Decisions

- Decision (2026-06-26): The repository uses four evidence stages: `lead`, `source-logic`, `benchmark-audit`, and `reproduction`.
- Decision (2026-06-26): Source-logic is decision-bearing only for prioritization and stack-hypothesis formation.
- Decision (2026-06-26): Benchmark and reproduction wording requires benchmark or reproduction artifacts.
- Decision (2026-06-29): Tool dossiers distinguish pinned source snapshots from unpinned historical inspections; current upstream `HEAD` must not be substituted for an unrecorded historical commit.
- Decision (2026-06-30): Candidate validity requires auditable source versioning; unpinned historical dossiers can remain as limitations or refresh targets, not recommended components.

## Rationale

The repo studies practical agent tooling where README claims can be misleading.

Evidence stages keep polished research prose aligned with inspected or measured behavior.

## Non-Goals

- This doc does not rank individual tools.
- This doc does not replace dossier templates.
- This doc does not store raw provenance.

## Maintenance Notes

- Update this doc when `scripts/validate_repository.py` accepts a new evidence-stage schema.
- Update this doc when report standards change claim wording for evidence stages.
- Keep stage names synchronized with `AGENTS.md`.

## Source References

- ../../../../AGENTS.md
- ../../../../METHODOLOGY.md
- ../../../../data/repositories.json
- ../../../../data/evaluations.json
- ../../../../scripts/validate_repository.py
- ../../../../scripts/audit_dossier_snapshots.py
- ../../../../templates/tool-dossier.md
