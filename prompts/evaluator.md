# Evaluator prompt

You are evaluating one token-saving treatment or compatible stack against a retained lifecycle-v0 baseline. Measure provider-reported workflow token use under the frozen sequence and model condition. Preserve raw evidence and report verifier, source-review, and negative outcomes separately; never select or rerun a sample because its model output scored better.

Read:

- `AGENTS.md` for the active lifecycle, evidence, and documentation-maintenance contract;
- `docs/evaluations/workflow-evaluation-runbook.md` for current baseline occupancy and runnable treatment commands;
- `docs/evaluations/evaluation-framework.md` for estimand and comparison rules;
- `docs/evaluations/token-usage-and-quality-standards.md` for token accounting and diagnostic quality fields;
- `docs/evaluations/continuous-workflow-simulation.md` for persistent state and isolation;
- `docs/evaluations/cumulative-result-schema.md` for the compact result contract.

Use `scripts/run_sequential_workflow_matrix.py <sequence-id> --treatment-profile <profile-id>` for paid execution. Do not rerun an occupied baseline or treatment replicate. The runner writes the compact evidence bundle under `sources/evaluations/workflow-sessions/<session-id>/` and merges its record into `data/workflow-sessions.json`.

Before execution:

- bind the current frozen protocol and compatible baseline pool;
- verify fixture qualification, image identity, treatment adapter identity, concealment, and installation of the profile's normal integration surface;
- declare the provider-token accounting boundary and operational invalidity conditions;
- preserve availability/natural use: never require, prefer, suggest, or calibrate forced treatment-tool invocation;
- do not infer integration inactivity from the absence of explicit model-issued tool commands unless the frozen integration contract makes that observation complete and dispositive;
- treat deterministic verifiers and optional source review as diagnostics, not token-sample eligibility gates.

After execution, follow the `AGENTS.md` documentation lifecycle: update fixture/session state, regenerate the workflow runbook, reconcile current status/findings surfaces, remove obsolete guidance, and run repository validation. Preserve the first operationally valid provider sample even when verifier or review diagnostics are unfavorable.
