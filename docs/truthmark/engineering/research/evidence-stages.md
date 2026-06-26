---
status: active
truth_kind: engineering-contract
last_reviewed: 2026-06-26
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
- `benchmark-audit` requires benchmark harness, task, scoring, token accounting, and raw-output evidence to be inspected.
- `reproduction` requires an independent target-workload run with provider-billed accounting and software-quality gates.
- Report claims must name or imply only the evidence stage that has actually been reached.
- Stack recommendations stay hypotheses until benchmark-audit or reproduction evidence exists.

## Engineering Decisions

- Decision (2026-06-26): The repository uses four evidence stages: `lead`, `source-logic`, `benchmark-audit`, and `reproduction`.
- Decision (2026-06-26): Source-logic is decision-bearing only for prioritization and stack-hypothesis formation.
- Decision (2026-06-26): Benchmark and reproduction wording requires benchmark or reproduction artifacts.

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
- ../../../../templates/tool-dossier.md
