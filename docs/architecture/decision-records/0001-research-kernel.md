# ADR 0001: Use a Research Kernel Instead of a README-Centric Project

## Status

Accepted

## Context

A token-optimization research project must collect repositories, classify techniques, evaluate compatibility, review literature, run experiments, and write papers. A README-centered structure turns these into prose requirements and makes later research hard to validate.

## Decision

Use the following research kernel:

```text
Artifact → Claim → Technique → Compatibility Edge → Evaluation → Finding → Paper Section
```

The repository architecture, data files, validation scripts, templates, and prompts will support transitions through this kernel.

## Consequences

- README is only an entry point for external readers.
- Canonical research state lives in `data/`.
- Architecture and workflow design lives in `docs/architecture/`.
- Bundles are represented as artifact relationships, not techniques.
- Future paper sections must cite internal IDs rather than uncited prose.
