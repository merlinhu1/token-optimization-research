# ADR 0003: Weight Practical Software Evidence Over Citation Volume

## Status

Accepted

## Context

This is a practical software-research workspace. Its main quality risk is over-scoped claims,
not a lack of prose polish. A report that dumps every provenance record is not more rigorous
than one that summarizes evidence classes; it is just harder to audit.

## Decision

- Decision (2026-06-26): Practical software evidence has higher decision weight than citation
  volume.
- Decision (2026-06-26): Research reports should summarize evidence classes instead of dumping
  raw provenance ledgers.
- Decision (2026-06-26): Negative findings and exclusions are part of the research record.
- Decision (2026-06-28): Discovery coverage is a separate quality gate from source inspection
  depth; high-signal leads must be visible before stack candidates are called complete or
  primary.
- Decision (2026-06-30): Candidate recommendations require auditable source versioning;
  unpinned historical inspections are refresh targets, not valid candidates.

## Consequences

- Excluded and failed conditions stay in the record rather than disappearing.
- Breadth of discovery and depth of inspection are tracked separately.
- Reports cite evidence classes and internal IDs, not raw ledgers.

## Provenance

Migrated 2026-08-14 from `docs/truthmark/engineering/research/methodology.md` when the
Truthmark workflow was removed. See [`0002-evidence-stages.md`](0002-evidence-stages.md).
