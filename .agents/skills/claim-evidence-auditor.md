---
name: claim-evidence-auditor
description: Use when drafting, revising, or reviewing research reports to ensure every major claim maps to source-logic, benchmark-audit, reproduction, or an explicit limitation.
---
# Claim-Evidence Auditor

## Purpose

Prevent unsupported or over-scoped claims in token-optimization reports. This repository values practical software evidence over citation volume: source inspection, runnable benchmarks, provider-billed usage, verifier output, quality review, and negative findings.

## When to Use

Use before publishing or committing:

- executive summaries;
- stack recommendations;
- evaluation conclusions;
- dossier-stage promotions;
- benchmark or reproduction reports.

## Procedure

1. Extract every major claim from the target text.
2. Classify each claim as one of:
   - mechanism claim;
   - compatibility claim;
   - benchmark claim;
   - reproduction claim;
   - recommendation or prioritization claim.
3. Map each claim to the strongest available evidence:
   - `source-logic` dossier;
   - `benchmark-audit` record;
   - `reproduction` run;
   - explicit limitation/exclusion.
4. Check scope calibration:
   - no benchmark wording without benchmark artifacts;
   - no reproduction wording without controlled task runs;
   - no deployment-grade recommendation from source-logic alone.
5. Add falsification or downgrade conditions for important claims.
6. Weaken, move, or delete claims with no evidence path.

## Output

Produce a compact table:

| Claim | Type | Evidence path | Status | Required edit |
|---|---|---|---|---|

Status values: `supported`, `over-scoped`, `needs evidence`, `move to limitation`, `remove`.

## Common Pitfalls

- Treating implementation plausibility as measured token savings.
- Treating stars, reputation, or README claims as decision evidence.
- Hiding raw uncertainty in polished prose.
- Using `recommended` when the evidence only supports `benchmark-audit priority`.
