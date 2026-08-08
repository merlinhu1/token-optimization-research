---
status: active
truth_kind: engineering-workflow
doc_type: workflow
source_of_truth:
  - ../../../../docs/methodology/README.md
  - ../../../../docs/research/tool-research-strategy.md
last_reviewed: 2026-08-08
---

# Methodology And Reporting Workflow

## Purpose

This doc owns the durable workflow for turning token-optimization research into reviewable reports.

It keeps methodology, report prose, claim auditing, and prior-art framing aligned.

## Scope

This doc covers report-writing and methodology maintenance.

Benchmark protocol details, quality diagnostics, and stack compatibility are owned by neighboring truth docs.

## Current Implementation Behavior

- Reports use evidence stages from `AGENTS.md` and methodology docs.
- Repo-local skills under `.agents/skills/` define the report-quality review workflow.
- The repository validator checks structural files and retired terminology.
- Discovery coverage audits are required before claiming a candidate set is complete, primary, recommended, or representative.
- High-signal leads discovered by coverage audits stay visible in repository data and backlog even when they remain non-decision-bearing `lead` evidence.
- Repositories without auditable source versioning are excluded from valid candidate sets until refreshed against a pinned source snapshot.
- The generated Phase 2 report includes a supplemental Claude Code baseline model-selection section. It derives weighted token cost (`fresh + 0.1×cached + 6×output`) for Sonnet 5 and Opus 5 from pinned registry session IDs, compares it with the matched Codex/OpenCode baselines, and excludes these baseline-only runs from treatment aggregates.

## Product Truth Links

- None. This repository is a research workspace, not a product with user-facing feature promises.

## Triggers

- A phase report, research report, or methodology document changes.
- A reusable report template or paper-writing prompt changes.
- A local research skill changes report-writing expectations.

## Inputs

- Source-logic dossiers and structured data provide primary evidence.
- Benchmark-audit and reproduction artifacts provide stronger evidence when available.
- Prior-art links provide context, not substitutes for software evidence.

## Execution Model

Use repo-local skills before report handoff.

Write claims from evidence first, then polish prose.

## Steps

1. Identify the report thesis and target evidence stage.
2. Map major claims to source-logic, benchmark-audit, reproduction, or limitation evidence.
3. Exclude unversioned or unpinned repositories from candidate recommendations; keep them as limitations or refresh targets.
4. Weaken, move, or remove unsupported claims.
5. Keep prior-art framing citation-light and mechanism-grouped.
6. Pair decision tables with limitations and falsification conditions.
7. Plan figures and tables only after metrics or structural evidence exists.

## Outputs

- Reports that distinguish hypotheses from measured findings.
- Methodology docs that future agents can apply without session memory.
- Claim wording that survives `claim-evidence-auditor` review.

## Engineering Decisions

- Decision (2026-06-26): Practical software evidence has higher decision weight than citation volume.
- Decision (2026-06-26): Research reports should summarize evidence classes instead of dumping raw provenance ledgers.
- Decision (2026-06-26): Negative findings and exclusions are part of the research record.
- Decision (2026-06-28): Discovery coverage is a separate quality gate from source inspection depth; high-signal leads must be visible before stack candidates are called complete or primary.
- Decision (2026-06-30): Candidate recommendations require auditable source versioning; unpinned historical inspections are refresh targets, not valid candidates.

## Rationale

The repo is a practical software-research workspace.

Its main quality risk is over-scoped claims, not lack of prose polish.

## Non-Goals

- This doc does not define benchmark token accounting.
- This doc does not require citation-heavy literature reviews.
- This doc does not make raw `sources/**` artifacts canonical truth docs.

## Maintenance Notes

- Update this doc when report templates, paper prompts, or methodology skills change.
- Use `scientific-report-reviewer` after major reports.
- Use `claim-evidence-auditor` before promoting conclusions.

## Source References

- ../../../../docs/methodology/README.md
- ../../../../docs/methodology/report-writing-patterns.md
- ../../../../templates/report.md
- ../../../../templates/claim-entry.md
- ../../../../prompts/researcher.md
- ../../../../prompts/paper-writer.md
- ../../../../.agents/skills/claim-evidence-auditor.md
- ../../../../.agents/skills/scientific-report-reviewer.md
- ../../../../.agents/skills/citation-light-prior-art-mapper.md
- ../../../../.agents/skills/figure-table-planner.md

## Engineering Decisions

Research reports must distinguish mechanism, compatibility, benchmark, reproduction, and recommendation claims and must preserve claim-evidence traceability.
