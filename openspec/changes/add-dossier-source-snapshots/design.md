## Context

Dossiers are decision-bearing at `source-logic` only when the inspected source can be traced. A moving branch name such as GitHub `HEAD` is not enough because upstream code may change after the dossier is written.

Some existing dossiers already include local shallow clone commit prefixes. Others only describe GitHub `HEAD` API inspection. The safe correction is to distinguish pinned evidence from unpinned historical evidence rather than backfilling invented commits.

## Goals / Non-Goals

**Goals:**

- Make snapshot provenance visible in every tool dossier identity section.
- Keep existing source-logic claims calibrated to the evidence actually recorded.
- Exclude repositories without auditable source versioning from valid candidate sets until a pinned snapshot exists.
- Fail validation when a dossier lacks snapshot metadata.
- Preserve unpinned historical dossiers as usable but explicitly limited evidence.
- Provide an audit command to inventory snapshot status.

**Non-Goals:**

- Do not re-inspect all upstream repositories in this change.
- Do not claim that a current upstream commit matches a historical GitHub `HEAD` inspection unless the original artifact recorded that commit.
- Do not promote any dossier to `benchmark-audit` or `reproduction`.
- Do not register repository fixtures in this change.

## Decisions

### Decision 1: Use explicit snapshot status

Each dossier SHALL carry one of these statuses:

- `pinned-commit`: inspected source is tied to an immutable commit or commit prefix already recorded in the dossier.
- `unpinned-historical-inspection`: original inspection used a moving source such as GitHub `HEAD`, and no immutable commit was recorded in the dossier.
- `not-applicable`: reserved for non-repository index pages; actual tool dossiers should not use it.

### Decision 2: Do not invent old commits

For existing dossiers that only say GitHub `HEAD`, use `Commit inspected: not recorded during original pass`. A future refresh can replace this with a pinned commit after re-inspection.

### Decision 3: Validate identity metadata, not every claim body

Validation checks the identity section and snapshot fields. It does not verify that every evidence artifact internally contains the same commit because older artifacts may not be structured consistently.

### Decision 4: Keep short commit prefixes acceptable for historical pinned records

Several existing dossiers recorded 12-character local shallow clone prefixes. Validation should accept 7- to 40-character hex refs while encouraging full SHAs in the template for future dossiers.

### Decision 5: Snapshot validity is candidate eligibility

`unpinned-historical-inspection` dossiers remain useful as historical notes, but they are not valid candidates for recommendation, stack construction, benchmark-audit, or reproduction. Candidate work requires a `pinned-commit` snapshot or a fresh source-logic refresh that records one.

## Risks / Trade-offs

- Backfilled `unpinned-historical-inspection` records are less strong than pinned source-logic evidence → mark them explicitly and require refresh before high-stakes conclusions.
- Validation can become too rigid for older dossiers → allow historical unpinned status while requiring transparent limitations.
- Full SHA recovery may be possible from external APIs today but would not prove the historical inspected HEAD → do not use current HEAD as old evidence.

## Migration Plan

1. Add OpenSpec requirements and tasks.
2. Add validation RED probes for missing and malformed snapshot metadata.
3. Update validator and audit script.
4. Update template and README policy.
5. Backfill every current dossier identity section with pinned or unpinned-historical metadata.
6. Run audit, OpenSpec validation, repo validation, Truthmark checks, and diff hygiene.
