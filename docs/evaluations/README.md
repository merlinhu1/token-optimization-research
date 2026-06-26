# Evaluations

This area holds human-facing evaluation protocols and operator guidance.

## Canonical active workflow docs

- `workflow-evaluation-runbook.md` — generated operator runbook for the active four-flow matrix.
- `sequential-workflow-runner.md` — implementation notes for persistent multi-task workflow simulation.
- `continuous-workflow-simulation.md` — protocol and artifact contract for cumulative workflow sessions.
- `token-usage-and-quality-standards.md` — shared accounting and software-quality rules.

The active matrix and runbook are generated from:

```text
data/workflow-task-sequences.json
data/repository-fixtures.json
scripts/update_workflow_runbook.py
```

## Planning and background docs

- `phase-2-benchmark-plan.md` — benchmark design background.
- `progressive-repository-evaluation-plan.md` — historical/progressive design notes.
- `repository-fixture-framework.md` — fixture readiness rules.
- `immediately-usable-flows.md` — earlier practical flows and sanity checks.
- `evaluation-framework.md` — general evaluation model.

Planning docs are not operator runbooks. When they conflict with the generated runbook or registries, update the planning doc or treat it as historical context.

## Source and evidence locations

- Active fixture source material: `sources/evaluations/fixtures/`.
- Archived historical evidence: `sources/evaluations/archive/`.
- Compact workflow-session evidence: `sources/evaluations/workflow-sessions/<session-id>/` when sessions are recorded.
