# Repository Fixture Template

Copy this template when drafting a fixture note. The machine-readable registry lives in `data/repository-fixtures.json`; this template is for reviewer-friendly context.

## Identity

- Fixture ID:
- Status: candidate-fixture | qualified-fixture | baseline-run | treatment-ready | retired-fixture
- Date opened:
- Owner/operator:

## Repository source

- Repository ID:
- Repository URL or local path:
- Fixture commit, tag, archive, or snapshot policy:
- Dirty-state policy:

## Task class and token-waste hypothesis

- Task classes:
- Primary token-waste surface:
- Future evaluation lanes:
- Candidate profiles:
- Why this repository is useful as a fixture:

## Setup

- Setup command:
- Setup blocker:
- Required tools or platform:
- Expected setup output:

## Reset

- Repository reset command:
- Tool/index/memory reset command:
- Reset blocker:
- Clean-state check:

## Verifier

- Verifier command:
- Verifier blocker:
- Expected passing output:
- Critical diagnostic facts to preserve:
- Minimum quality gate:

## Prompt and task records

- Prompt path:
- Prompt policy if prompt is not written yet:
- Related task template:
- Forbidden shortcuts:

## Artifact paths

- Raw artifact root:
- Environment record:
- Baseline transcript:
- Treatment transcript:
- Provider usage:
- Verifier output:
- Quality review:

## Promotion checklist

- [ ] Repository source is stable and reviewable.
- [ ] Fixture commit or snapshot policy is concrete.
- [ ] Setup command or setup blocker is recorded.
- [ ] Reset command or reset blocker is recorded.
- [ ] Verifier command or verifier blocker is recorded.
- [ ] Prompt path or prompt policy is recorded.
- [ ] Artifact paths are defined.
- [ ] Fixture status does not imply tool evidence stage.

## Blockers and caveats

-
