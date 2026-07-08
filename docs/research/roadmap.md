# Research roadmap

## Current direction

The active research direction is Phase 2 workflow simulation: compare compatibility-safe profiles on persistent multi-task repository workflows using cumulative provider-billed token usage and software-quality gates.

The default active matrix is:

- Terraform: large Go workflow.
- OrchardCore: large C# workflow.
- Fastify: medium TS/JS workflow.
- Beets: medium Python workflow.

Django single-task evidence is archived as historical evidence outside the active workflow matrix.

## Phase 1 — Source-logic stack research

Status: complete for the current candidate set.

- Build the repository catalog and technique taxonomy.
- Create persistent source-logic dossiers for important token-saving tools.
- Define compatibility-safe stack candidates by surface ownership rather than popularity.
- Publish the Phase 1 compatibility-safe stack report.
- Keep `lead` entries out of stack recommendations until source-code logic is inspected.

## Phase 2 — Workflow-simulation benchmark framework

Status: active.

- Maintain active workflow sequences in `data/workflow-task-sequences.json`.
- Maintain fixture readiness in `data/repository-fixtures.json`.
- Generate the human operator runbook with `scripts/update_workflow_runbook.py`.
- Run paired baseline and treatment workflow sessions with the same sequence, runtime, provider, model condition, prompt-disclosure policy, and verifier set.
- Record compact workflow-session evidence under `sources/evaluations/workflow-sessions/<session-id>/`.
- Promote selected dossiers from `source-logic` to `benchmark-audit` only after harness, scoring, token accounting, raw outputs, and failure semantics are inspected.

## Phase 3 — Controlled stack reproduction

Status: not complete.

- Run baseline and treatment profiles on frozen active workflow sequences.
- Compare provider-billed workflow usage, pass rate, quality score, turns, tool calls, latency, and reset/reproducibility.
- Keep failed and negative workflow sessions in `data/workflow-sessions.json` or compact evidence bundles.
- Promote only reproduced findings toward deployment-grade recommendations.

## Phase 4 — Research outputs and standards

Status: future.

- Publish Phase 2 and Phase 3 reports with measured results and limitations.
- Update dossiers and standards based on benchmark-audit and reproduction findings.
- Version datasets, task fixtures, evaluation protocols, and run records with clear changelogs.
