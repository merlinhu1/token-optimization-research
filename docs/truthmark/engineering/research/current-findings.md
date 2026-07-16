---
status: active
truth_kind: engineering-behavior
last_reviewed: 2026-07-14
---

# Current Findings

## Purpose

This doc owns the compact current-findings layer for the research repository.

It gives future agents a bounded place to find durable conclusions without rereading every dossier.

## Scope

This doc summarizes current phase, durable conclusions, limitations, and backlog interpretation.

Detailed evidence remains in reports, dossiers, structured data, and evaluation artifacts.

## Product Truth Links

- None. Current findings summarize repository research state, not product behavior.

## Current Implementation Behavior

- The repository is in Phase 2 readiness work.
- Phase 1 established 42 source-logic dossiers and a compatibility-safe stack report.
- As of 2026-07-01, all 42 tool dossiers have pinned source-snapshot metadata and pass dossier-quality validation.
- The 2026-06-28 corrective knowledge-graph and agent-memory leads were promoted from `lead` to `source-logic` on 2026-06-29.
- Phase 2 focuses on persistent workflow simulation, provider-billed token accounting, quality standards, and a broader source-logic stack hypothesis portfolio.
- Terraform, Beets, and Fastify are the three current primary-objective workflows. Beets is the only currently accepted bare baseline; Fastify's latest paid artifact is invalid-fixture calibration evidence and Terraform's latest paid artifact is quality-rejected.
- Active checkout-generated qualification must prove that every selected regression merges into one composite broken start, every selected verifier fails on that broken state, and the complete cumulative verifier passes on the fixed snapshot.
- Current Beets lifecycle V2 baseline `baseline-beets-20260715-p-d248be3bdc63-r0` passed 3/3 tasks and independent quality review at 5/5 with 17,594,536 provider tokens.
- Current Fastify maintenance V1 session `baseline-fastify-20260715-p-d1be8ed202a8-r2` passed the original 5/5 controller gates with 78,911,126 provider tokens, but is excluded as `invalid-fixture`: its prompt required a shutdown-refusal message identifying server closing while acceptance additionally required the undisclosed `request aborted` compatibility identifier. V7 now discloses that identifier and the exact visible focused test.
- Current Terraform maintenance V2 session `baseline-terraform-20260716-p-300d6cfe45d8-r0` passed the original 3/3 controller gates with 17,918,550 provider tokens but is quality-rejected because the submission dropped `ComputedBlocksAllowed` across gRPC wrapper boundaries. V8 adds a fixed-pass, seed-fail, rejected-candidate-fail boundary probe before any future execution.
- The verifier snapshots used by Fastify fingerprints `57a82a0dca61` and `d8a06f2ef78f` were invalid for objective scoring: hidden checks required exact messages, internal symbols, object identity, and exact serialization that the prompts did not require; the Content-Type prompt explicitly disallowed an identity requirement. Their live comparison was withdrawn and their artifacts remain in Git history.
- Post-hoc replay against corrected prompt-aligned behavioral gates passes 5/5 surfaces for superseded GPT-5.5 high session `baseline-fastify-20260713-p-d8a06f2ef78f-r0` and 4/5 for superseded GPT-5.6 Luna xhigh session `baseline-fastify-20260713-p-57a82a0dca61-r0`; this proved the original 0/5 classifications invalid.
- Independent source review rejected intermediate Fastify baseline `baseline-fastify-20260713-p-a9c642bc016a-r0` at 2/5 quality and 3/5 objective tasks. A fresh provider execution repaired all five disclosed surfaces and was replayed after removing one unstated message assertion, but final-tree review found `kLogController` undefined in both bare and Lowfat implementations. Both score 3/5; the bare run remains quality-rejected hard evidence, while the paired Lowfat token delta is now forensic only because the treatment used prohibited external retrieval and pass-through commands.
- Independent source review also found the old Beets Tidal verifier did not enforce required `MediaAttributes.popularity`; the old pool and zero-use treatment were retired. Corrected baseline `baseline-beets-20260713-p-7aaac4b8a309-r0` passes 3/3 tasks at 4/5 quality with 6,400,224 provider tokens.
- Initial Terraform and Beets Lowfat treatment runs invoked Lowfat zero times. They are valid zero-use outcomes: no invocation occurred, no invocation was forced, and no Lowfat effect is attributed.
- The later Lowfat arm predeclared prompted/preferred documented direct use. That is a valid estimand and is not retroactively invalidated by the later natural-use principle. Fastify and Terraform are causally excluded because only treatment used prohibited external retrieval. Beets remains valid one-complete-workflow-replicate screening evidence for preferred direct use: +42.25% provider tokens with accepted baseline/treatment quality. Across the arm, 544 of 655 prefixes targeted pass-through commands, limiting mechanism attribution. See `docs/research/lowfat-three-lane-evaluation.md`.
- Native Lowfat automatic shell integration has not been evaluated. Binary-on-PATH exposure is insufficient. `terminal-lowfat` is retained as a provenance-only historical preferred-direct profile; `terminal-lowfat-shell-integrated-v0.8.0` is blocked until `lowfat shell-init` is implemented and preflighted in the actual model shell. The runner disables Codex web search and model-shell networking and rejects web/network-client evidence.
- Obsolete workflow definitions, qualifications, protocols, tasks, rejected sessions, and historical calibration artifacts are retained only where needed for explicit forensic provenance; Git history remains the archive.
- The active runner pre-seeds every regression before provider execution, discloses prompts sequentially in one persistent lane, captures operational checkpoints without hidden functional gates, and runs every concealed task verifier after the final prompt without short-circuiting. Structured per-task outcomes determine `tasks_passed`.
- Primary objective claims require reproduction run records on medium-project or large-project fixtures in the cumulative schema.
- Stack findings are hypotheses until benchmark-audit or reproduction evidence exists; Phase 1 now routes multiple candidate stacks and comparators rather than selecting a single default stack.
- Lead-stage backlog items are not decision evidence.
- Raw discovery and source-inspection artifacts remain provenance, not canonical conclusion prose.

## Core Rules

- Keep current findings short and evidence-stage calibrated.
- Link to the owning report or data file for details.
- Record limitations when a finding depends only on source-logic.
- Prefer updating this doc after durable conclusions change, not after every note.

## Engineering Decisions

- Decision (2026-06-26): This doc is the summary layer for durable current findings.
- Decision (2026-06-26): It should not duplicate every report section or dossier claim.
- Decision (2026-06-29): Corrective coverage leads can support report upgrades only after source-logic dossiers exist; they remain benchmark/reproduction hypotheses until measured.

## Rationale

Future agents need a compact orientation layer.

The detailed research corpus remains the evidence base.

## Non-Goals

- This doc does not replace the Phase 1 report.
- This doc does not store benchmark results.
- This doc does not manage raw `sources/**` artifacts.

## Maintenance Notes

- Update this doc when `README.md`, `docs/research/roadmap.md`, or the Phase report changes the active research direction.
- Update this doc when a tool moves to a stronger evidence stage.
- Keep durable findings aligned with `evidence-stages.md`.

## Source References

- ../../../../README.md
- ../../../../docs/research/roadmap.md
- ../../../../docs/research/hard-lane-evidence.md
- ../../../../docs/reports/phase-1-compatibility-safe-token-saving-stacks.md
- ../../../../data/repositories.json
- ../../../../data/tool-analysis-backlog.json
