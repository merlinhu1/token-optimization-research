## Why

Tool dossiers currently mix immutable local clone refs with moving GitHub `HEAD` descriptions. That makes source-logic claims hard to audit when upstream repositories change after inspection.

## What Changes

- Add a source snapshot contract for every actual tool dossier.
- Require each dossier to state whether its inspected source is pinned to an immutable commit or is an explicitly unpinned historical inspection.
- Update the dossier template and dossier README with the snapshot metadata policy.
- Add repository validation so future source-logic dossiers cannot rely on moving `HEAD` without an explicit snapshot status.
- Add a small audit script that reports pinned, unpinned-historical, and invalid dossier snapshot metadata.
- Treat repositories without auditable source versioning as invalid candidates for recommendation, stack construction, benchmark-audit, or reproduction until a pinned snapshot is recorded.
- Backfill existing dossiers with the best truthful metadata: exact commit where already recorded, otherwise explicit `unpinned-historical-inspection` without inventing a commit.

## Capabilities

### New Capabilities

- `dossier-source-snapshots`: Defines immutable source snapshot metadata, historical-unpinned disclosure, validation, and audit behavior for tool dossiers.

### Modified Capabilities

- None.

## Impact

- Updates `templates/tool-dossier.md` and `docs/tool-dossiers/README.md`.
- Updates all `docs/tool-dossiers/*.md` dossier identity sections except the README index.
- Updates `scripts/validate_repository.py` and adds `scripts/audit_dossier_snapshots.py`.
- Does not promote any dossier evidence stage, refresh source inspections, or claim current upstream behavior for previously unpinned historical inspections.
