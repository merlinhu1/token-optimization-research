# Evaluation Fixtures

This directory stores human-readable notes for repository fixtures when a registry entry needs more context than `data/repository-fixtures.json` can carry cleanly.

The compact registry is canonical for machine validation:

```text
data/repository-fixtures.json
```

Use `templates/repository-fixture.md` for detailed fixture notes.

Future progressive evaluation changes should reference fixture IDs from the registry in their `proposal.md` and `protocol.md`. Raw transcripts, provider usage, verifier output, environment records, and quality reviews belong under `sources/evaluations/<evaluation-id>/`, not in this directory.

The old generated calibration corpus under `sources/evaluations/fixture-corpus/v1/` is retired. The maintained evaluation architecture is the four-workflow matrix defined by `data/workflow-task-sequences.json`, `data/repository-fixtures.json`, and the workflow runner docs.

Fixture status is repository readiness only. It does not promote any tool or compatibility-safe stack to `benchmark-audit` or `reproduction`.
