## Why

The repository now has many source-logic dossiers and compatibility-safe stack hypotheses, but stack evaluation cannot start cleanly until the project can qualify repositories as controlled evaluation fixtures. A repository-fixture layer prevents Phase 2 from confusing stack failures with broken setup, weak verifiers, unstable prompts, or unsuitable task classes.

## What Changes

- Add a repository fixture framework for Step 1: fixture schema, lifecycle states, task-class taxonomy, verifier/reset requirements, artifact ownership, and validation rules.
- Add starter fixture registration for Step 2: a small set of candidate fixtures covering noisy terminal repair, large-codebase navigation, repeated-task memory, broad-owner/context evaluation, and Apple/Xcode only when a realistic fixture exists.
- Add validation so fixture records remain structurally reviewable before any provider-billed baseline or treatment run.
- Keep this change limited to planning and fixture qualification. It does not run baselines, treatments, stack ablations, or promote any stack beyond source-logic.

## Capabilities

### New Capabilities

- `repository-fixture-framework`: Defines how repository fixtures are represented, qualified, validated, and promoted through evaluation readiness states.
- `starter-fixture-registration`: Defines how the first 3-5 candidate fixtures are selected and registered without claiming benchmark-audit or reproduction evidence.

### Modified Capabilities

- None.

## Impact

- New docs under `docs/evaluations/` for the repository fixture framework and fixture registry entrypoint.
- New template under `templates/` for repository fixture records.
- New structured data file under `data/` for fixture records.
- Possible validation update in `scripts/validate_repository.py` or a dedicated `scripts/validate_fixtures.py` called by repository validation.
- No change to tool dossier evidence stages, stack rankings, provider usage, or evaluation results.
