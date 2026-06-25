## ADDED Requirements

### Requirement: Dossier snapshot metadata

Every actual tool dossier SHALL include explicit source snapshot metadata in its identity section.

#### Scenario: Pinned dossier records commit

- **WHEN** a dossier has `Snapshot status: pinned-commit`
- **THEN** it includes `Commit inspected:` with a 7- to 40-character hexadecimal commit or commit prefix
- **AND** it includes `Source artifact path:` naming the discovery artifact or other evidence record used for inspection

#### Scenario: Historical unpinned dossier is transparent

- **WHEN** a dossier was inspected from moving GitHub `HEAD` and no immutable commit was recorded
- **THEN** it uses `Snapshot status: unpinned-historical-inspection`
- **AND** it includes `Commit inspected: not recorded during original pass`
- **AND** it includes a note or artifact path explaining the historical evidence source

#### Scenario: Moving HEAD is not silently accepted

- **WHEN** a dossier identity section says GitHub `HEAD`
- **THEN** validation fails unless the dossier also has an explicit snapshot status

### Requirement: Dossier template snapshot contract

The tool dossier template SHALL instruct future dossiers to resolve moving refs to immutable commits before source-logic claims are written.

#### Scenario: Template names required fields

- **WHEN** a researcher opens `templates/tool-dossier.md`
- **THEN** the identity section contains fields for version/ref inspected, snapshot status, commit inspected, commit URL, source artifact path, date inspected, reviewer, and evidence stage

#### Scenario: Template warns against moving refs

- **WHEN** a researcher follows the template
- **THEN** it states that GitHub `HEAD` or default branch names must be resolved to an immutable commit SHA before the dossier is considered pinned

### Requirement: Snapshot validation

Repository validation SHALL check tool dossier snapshot metadata.

#### Scenario: Missing snapshot status fails

- **WHEN** an actual tool dossier lacks `Snapshot status:`
- **THEN** `python3 scripts/validate_repository.py` fails with a diagnostic naming the dossier path

#### Scenario: Pinned dossier without commit fails

- **WHEN** an actual tool dossier uses `Snapshot status: pinned-commit` without a valid `Commit inspected:` hex value
- **THEN** validation fails with a diagnostic naming the dossier path

#### Scenario: Unpinned historical dossier without disclosure fails

- **WHEN** an actual tool dossier uses `Snapshot status: unpinned-historical-inspection` without `Commit inspected: not recorded during original pass`
- **THEN** validation fails with a diagnostic naming the dossier path

### Requirement: Snapshot audit script

The repository SHALL provide a command that reports dossier snapshot coverage.

#### Scenario: Audit reports snapshot categories

- **WHEN** `python3 scripts/audit_dossier_snapshots.py` runs
- **THEN** it reports counts and filenames for pinned, unpinned-historical, invalid, and non-dossier index records

#### Scenario: Audit supports validation use

- **WHEN** any actual dossier has invalid snapshot metadata
- **THEN** the audit command exits non-zero

### Requirement: Versioning gates candidate validity

Repositories without auditable source versioning SHALL NOT be treated as valid candidates for recommendation, stack construction, benchmark-audit, or reproduction.

#### Scenario: Pinned snapshot is candidate-eligible

- **WHEN** a dossier has `Snapshot status: pinned-commit`
- **THEN** the audit command reports it under candidate-eligible snapshot records

#### Scenario: Unpinned historical snapshot is candidate-ineligible

- **WHEN** a dossier has `Snapshot status: unpinned-historical-inspection`
- **THEN** reports and prompts treat it as a refresh target or limitation, not as a valid candidate
- **AND** the audit command reports it under candidate-ineligible versioning records

### Requirement: Existing dossier backfill

Existing tool dossiers SHALL be backfilled truthfully without inventing historical commits.

#### Scenario: Existing commit prefix is preserved

- **WHEN** an existing dossier already records a hexadecimal commit or commit prefix in `Version/ref inspected:`
- **THEN** the backfill uses `Snapshot status: pinned-commit`
- **AND** it copies that commit or prefix into `Commit inspected:`

#### Scenario: Existing moving HEAD remains limited

- **WHEN** an existing dossier only records GitHub `HEAD` or another moving reference
- **THEN** the backfill uses `Snapshot status: unpinned-historical-inspection`
- **AND** it does not replace that value with current upstream HEAD unless a fresh source-logic inspection is performed
