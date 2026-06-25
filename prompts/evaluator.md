# Evaluator prompt

You are evaluating one token-saving technique, stack profile, or replacement-agent profile. Isolate the tested surface from bundled solutions unless the evaluation is explicitly a stack reproduction. Measure operation-level reduction, fidelity, agent behavior, provider-billed task usage when available, and software quality. Preserve raw artifacts and report negative results.

Use these documents:

- `docs/evaluations/evaluation-framework.md` for evidence stages, experiment classes, controls, and interpretation rules.
- `docs/evaluations/token-usage-and-quality-standards.md` for token accounting, cost fields, software-quality gates, and scoring.
- `docs/evaluations/phase-2-benchmark-plan.md` for prioritized Phase 2 components, task classes, and stack profiles.
- `docs/evaluations/immediately-usable-flows.md` for runbook steps.
- `docs/evaluations/technique-protocol-template.md` and `templates/evaluation-record.md` for records.

Update `data/evaluations.json` with a compact result record and store raw transcripts, usage logs, verifier output, and quality review under `sources/evaluations/<evaluation-id>/`.

Before running a benchmark or reproduction, follow protocol-before-result discipline:
- Write the hypothesis in the form `profile X improves metric Y for workload Z`.
- Freeze baseline, treatment, task prompt, repository fixture, model/provider, turn budget, and token accounting boundary.
- Declare deterministic verifier, software-quality gates, expected failure modes, and exclusion rules.
- For multi-component stacks, plan at least one ablation or lower-intervention comparator when feasible.
- Keep negative results and failed runs in the evaluation record with reason codes.
