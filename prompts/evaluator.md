# Evaluator prompt

You are evaluating one token-saving treatment or compatible stack against a compatible Lifecycle V1 baseline. Measure provider-reported workflow token use under the frozen sequence and model condition. Preserve raw evidence and report compile, verifier, source-review, and negative outcomes separately; never select or rerun a sample because its model output scored better.

Read:

- `AGENTS.md` for the active lifecycle, evidence, and documentation-maintenance contract;
- `docs/evaluations/operations/runbook.md` for current baseline occupancy and runnable treatment commands;
- `docs/evaluations/design/framework.md` for estimand and comparison rules;
- `docs/evaluations/design/token-and-quality-policy.md` for token accounting and diagnostic quality fields;
- `docs/evaluations/design/workflow-model.md` for persistent state and isolation;
- `docs/evaluations/design/result-schema.md` for the compact result contract.

Use `scripts/run_sequential_workflow_matrix.py <sequence-id> --treatment-profile <profile-id>` for paid execution. Do not rerun an occupied baseline or treatment replicate. The runner writes the compact evidence bundle under `sources/evaluations/workflow-sessions/<session-id>/` and merges its record into `data/workflow-sessions.json`.

Before execution:

- bind the current frozen protocol and compatible baseline pool;
- verify fixture qualification, image identity, treatment adapter identity, concealment, and installation of the profile's normal integration surface;
- declare the provider-token accounting boundary and operational invalidity conditions;
- preserve availability/natural use after faithful product installation: include every tool-author-recommended integration surface, including product-authored guidance, rules, skills, and hooks, while never adding evaluator-authored steering, quotas, or forced calls;
- never strip product-authored guidance in the name of neutrality; server-only, guidance-free, or otherwise reduced setups are explicit ablations rather than canonical product treatments;
- do not infer integration inactivity from the absence of explicit model-issued tool commands unless the frozen integration contract makes that observation complete and dispositive;
- treat deterministic verifiers and optional source review as diagnostics, not token-sample eligibility gates.

After execution, follow the `AGENTS.md` documentation lifecycle: update fixture/session state, regenerate the workflow runbook, reconcile current status/findings surfaces, remove obsolete guidance, and run repository validation. Preserve the first operationally valid provider sample even when verifier or review diagnostics are unfavorable.
