## 1. OpenSpec and policy docs

- [x] 1.1 Create OpenSpec proposal, design, and spec for dossier source snapshots.
- [x] 1.2 Update `templates/tool-dossier.md` with snapshot status, commit inspected, commit URL, and source artifact path fields.
- [x] 1.3 Update `docs/tool-dossiers/README.md` to explain pinned vs unpinned historical snapshot policy.

## 2. Validation and audit tooling

- [x] 2.1 Add RED smoke checks proving missing snapshot metadata and malformed pinned/unpinned metadata fail before accepting validator changes.
- [x] 2.2 Add snapshot validation to `scripts/validate_repository.py` for every actual dossier under `docs/tool-dossiers/*.md` except `README.md`.
- [x] 2.3 Add `scripts/audit_dossier_snapshots.py` to report pinned, unpinned-historical, invalid, and index records.
- [x] 2.4 Run targeted GREEN smoke checks for valid pinned, valid unpinned-historical, invalid pinned, invalid unpinned, and non-dict/empty edge cases where applicable.
- [x] 2.5 Extend audit output so unpinned-historical and invalid snapshot records are candidate-ineligible for versioning.

## 3. Existing dossier backfill

- [x] 3.1 Backfill dossiers with existing hexadecimal refs as `Snapshot status: pinned-commit` and copy the ref into `Commit inspected:`.
- [x] 3.2 Backfill moving-HEAD dossiers as `Snapshot status: unpinned-historical-inspection` with `Commit inspected: not recorded during original pass`.
- [x] 3.3 Add source artifact paths where recoverable from evidence inventory; otherwise record `not recorded` explicitly.
- [x] 3.4 Confirm no actual dossier is missing `Snapshot status:`.

## 4. Verification

- [x] 4.1 Run `python3 scripts/audit_dossier_snapshots.py` and inspect counts.
- [x] 4.2 Run `openspec validate add-dossier-source-snapshots --strict --json`.
- [x] 4.3 Run `openspec validate --all --strict --json`.
- [x] 4.4 Run `PATH=/opt/data/bin:/opt/data/.local/bin:$PATH truthmark check --json`.
- [x] 4.5 Run `PATH=/opt/data/bin:/opt/data/.local/bin:$PATH truthmark index --json`.
- [x] 4.6 Run `PATH=/opt/data/bin:/opt/data/.local/bin:$PATH python3 scripts/validate_repository.py`.
- [x] 4.7 Run `git diff --check`.
- [x] 4.8 Review `git status --short --branch --untracked-files=all` for expected files only.
