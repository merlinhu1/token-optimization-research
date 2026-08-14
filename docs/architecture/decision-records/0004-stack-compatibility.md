# ADR 0004: Model Stack Compatibility by Surface Ownership

## Status

Accepted

## Context

Token-saving tools can conflict when two components rewrite the same context surface. Grouping
tools by marketing description hides that conflict; a taxonomy has to answer whether two
techniques can run together without double-processing, hiding evidence, or adding turns.
Surface ownership makes stack design testable and reviewable.

## Decision

- Decision (2026-06-26): Compatibility-safe stacks should avoid duplicate ownership of the same
  surface.
- Decision (2026-06-26): Installer or orchestrator tools are evaluated separately from reducers.
- Decision (2026-06-26): Multi-component stack claims require ablation planning before benchmark
  conclusions.
- Decision (2026-07-18): The historical TokenJuice+jcodemunch stack decision is withdrawn
  because the intended component assignments were not validly installed or proven. Preserve its
  provider-accounting records as excluded evidence.
- Decision (2026-07-18): A future stack requires separately qualified versioned individual
  integrations and a new preregistered stack identity.

## Consequences

- Two components claiming one surface is a design error, caught before benchmarking.
- A withdrawn stack keeps its accounting records, marked excluded rather than deleted.
- No stack conclusion without a preregistered identity and per-component qualification.

## Provenance

Migrated 2026-08-14 from `docs/truthmark/engineering/research/stack-compatibility.md` when the
Truthmark workflow was removed. The compatibility graph itself is documented in
[`../compatibility-graph.md`](../compatibility-graph.md).
