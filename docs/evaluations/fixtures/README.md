# Evaluation Fixtures

This directory stores human-readable notes for repository fixtures when a registry entry needs more context than `data/repository-fixtures.json` can carry cleanly.

The compact registry is canonical for machine validation:

```text
data/repository-fixtures.json
```

Active task sequences are canonical in:

```text
data/workflow-task-sequences.json
```

Use `templates/repository-fixture.md` for detailed fixture notes.

Raw fixture source material lives under `sources/evaluations/fixtures/`.

Fastify is the only current executable workflow fixture. Terraform, Beets, and OrchardCore task surfaces were purged because their designs did not meet the production-grade floor; candidate metadata may remain.

Workflow-session evidence belongs under `sources/evaluations/workflow-sessions/<session-id>/` using the compact four-file artifact contract.

The old generated calibration corpus under `sources/evaluations/fixture-corpus/v1/` is retired.

The old hand-maintained Phase 2 experiment suite under `sources/evaluations/phase-2-experiment-suite-v1/` is retired.

Fixture status is repository readiness only. It does not promote any tool or compatibility-safe stack to `benchmark-audit` or `reproduction`.
