---
status: active
truth_kind: engineering-behavior
last_reviewed: 2026-07-09
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
- Terraform, Beets, and Fastify are primary-objective workflows. Terraform and Beets form the accepted production pair; Fastify is a qualified five-task primary-objective hard lane whose strengthened failed run remains the token-usage baseline for treatment comparison.
- Active checkout-generated qualification must prove that every selected regression merges into one composite broken start, every selected verifier fails on that broken state, and the complete cumulative verifier passes on the fixed snapshot.
- The accepted Beets baseline passed the strengthened Tidal contract and quality review at 4/5 with 7,642,781 provider tokens. The accepted Terraform baseline passed quality review at 4/5 with 18,004,662 provider tokens. Together, the current-pool bare baselines total 25,647,443 provider tokens and are reusable for paired treatment.
- Fastify session `baseline-fastify-20260713-p-292cc70dff18-r0` completed and claimed all five tasks with 90,553,295 provider tokens, but was rejected at quality review (2/5) after focused upstream tests exposed nine failures. Because its verifier contract was superseded, it remains difficulty evidence rather than the current comparison anchor; compact evidence is recoverable from Git commit `e4be0b3`.
- The verifier snapshots used by Fastify fingerprints `57a82a0dca61` and `d8a06f2ef78f` were invalid for objective scoring: hidden checks required exact messages, internal symbols, object identity, and exact serialization that the prompts did not require; the Content-Type prompt explicitly disallowed an identity requirement. Their live comparison was withdrawn and their artifacts remain in Git history.
- Post-hoc replay against corrected prompt-aligned behavioral gates passes 5/5 surfaces for superseded GPT-5.5 high session `baseline-fastify-20260713-p-d8a06f2ef78f-r0` and 4/5 for superseded GPT-5.6 Luna xhigh session `baseline-fastify-20260713-p-57a82a0dca61-r0`; this proved the original 0/5 classifications invalid.
- Independent source review rejected intermediate Fastify baseline `baseline-fastify-20260713-p-a9c642bc016a-r0` at 2/5 quality and 3/5 objective tasks. A fresh provider execution repaired all five disclosed surfaces and was replayed after removing one unstated message assertion, but final-tree review found `kLogController` undefined in both bare and Lowfat implementations. Both score 3/5 and are quality-rejected hard evidence: bare 60,671,087 tokens; Lowfat 76,395,931 (+25.92%).
- Independent source review also found the old Beets Tidal verifier did not enforce required `MediaAttributes.popularity`; the old pool and zero-use treatment were retired. Corrected baseline `baseline-beets-20260713-p-7aaac4b8a309-r0` passes 3/3 tasks at 4/5 quality with 6,400,224 provider tokens.
- Initial Terraform and Beets Lowfat exposure runs invoked Lowfat zero times. They were removed from canonical tool-effectiveness evidence; the active Lowfat protocol now uses preferred guidance and treats zero model-initiated Lowfat commands as invalid tool-effectiveness evidence.
- Obsolete workflow definitions, qualifications, protocols, tasks, rejected sessions, and historical calibration artifacts were removed from the live tree; Git history is the archive. The production contract remains frozen until treatment completes.
- The active runner pre-seeds every regression before provider execution, discloses prompts sequentially in one persistent lane, captures operational checkpoints without hidden functional gates, and runs one complete concealed verifier suite after the final prompt.
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
