# Evaluation source material

This directory separates active workflow fixtures from archived evidence.

## Active fixtures

The active Fastify repository fixture lives under:

```text
sources/evaluations/fixtures/
  container/Dockerfile
  medium/fastify-fastify/
```

Candidate-only projects do not retain runnable task/setup/reset/verifier assets.

The canonical active sequence list is `data/workflow-task-sequences.json`; fixture readiness metadata is `data/repository-fixtures.json`.

## Workflow sessions

Completed continuous workflow simulations write compact evidence bundles under:

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json
  changes.diff
  evidence.jsonl.gz
  manifest.sha256
```

Do not commit materialized runtime state such as `project/`, `project/repo/`, profile homes, generated tool indexes, `.venv/`, or split setup/verifier logs.

## Legacy evidence

Archived evaluation evidence was removed because it was produced with invalid task designs. Only compact workflow-session artifacts under `sources/evaluations/workflow-sessions/` are current evidence.
