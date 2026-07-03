# Evaluation Fixtures

This directory stores human-readable notes for repository fixtures when a registry entry needs more context than `data/repository-fixtures.json` can carry cleanly.

The compact registry is canonical for machine validation:

```text
data/repository-fixtures.json
```

Use `templates/repository-fixture.md` for detailed fixture notes.

Future progressive evaluation changes should reference fixture IDs from the registry in their `proposal.md` and `protocol.md`. Raw transcripts, provider usage, verifier output, environment records, and quality reviews belong under `sources/evaluations/<evaluation-id>/`, not in this directory.

The first concrete Phase 2 fixture suite is documented in `../phase-2-experiment-suite-v1.md` and materialized under `../../../sources/evaluations/fixture-corpus/v1/`.

Fixture status is repository readiness only. It does not promote any tool or compatibility-safe stack to `benchmark-audit` or `reproduction`.
