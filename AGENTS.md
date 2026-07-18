# Repository guidance

## Evaluation contract

This repository's sole evaluation portfolio is lifecycle v0:

1. feature implementation;
2. behavior-preserving refactor;
3. code review/correction.

Every active sequence, task ID, qualification file, and current execution contract must be v0. Do not add any non-v0 lane record or parallel compatibility surface. Accepted production records are immutable. Rejected or excluded records may be deleted only by explicit experiment-owner direction, together with their artifact roots and unreferenced protocols.

## Fixture design

- Pin the upstream repository commit.
- Build authentic tasks from upstream code/history.
- Start patches must be independently applicable and compose without overlap.
- Feature and review start states fail semantic acceptance.
- Refactor starts must pass behavior acceptance and fail only the disclosed structural/performance gate.
- Model-facing prompts disclose public behavior and any required structural outcome; controller tests remain concealed.
- Review tasks include the exact proposed patch under review.
- Run all concealed verifiers after the final prompt in one persistent workflow.

## Evidence and execution

Qualification JSON is generated executable evidence; never hand-edit it. Production runs require provider-reported cumulative tokens and isolated baseline/treatment conditions. Verifier and source-review outcomes are diagnostic and must not gate token accounting or trigger pass-selection reruns. Do not infer a token result from qualification readiness.

Lifecycle-v0 treatment execution is availability/natural-use only. Install the profile's normal product integration—including its own hooks, wrappers, proxies, MCP exposure, or product-authored instructions—without evaluator-authored steering. Never require, prefer, suggest, or calibrate forced invocation of a treatment tool. Zero explicit model-issued tool commands does not by itself prove that an integration was inactive, because the intervention may operate below or around the model-visible command surface. Preserve the first valid assignment sample and interpret mechanism evidence only from instrumentation appropriate to the declared integration.

## Documentation lifecycle

An action that changes research state must update every active surface that reports that state in the same change. This includes an evaluation run, qualification or protocol refresh, fixture promotion or retirement, session merge or deletion, treatment comparison, evidence-stage promotion, and a change to eligibility or interpretation policy.

After such an action:

1. Update the machine authority first: `data/workflow-sessions.json`, `data/repository-fixtures.json`, and any affected sequence/profile registry.
2. Regenerate `docs/evaluations/operations/runbook.md`; never hand-edit generated status.
3. Reconcile `README.md`, `docs/evaluations/README.md`, `sources/evaluations/README.md`, `docs/research/roadmap.md`, and `docs/truthmark/engineering/research/current-findings.md` with the registry.
4. Reconcile active prompts, templates, repo-local skills, schemas, and Truthmark docs when the contract changes. Search for the retired status, path, policy phrase, protocol/session ID, and lifecycle term.
5. If a document or template has no distinct maintained authority or current consumer, delete it and remove its references instead of leaving a second stale workflow.
6. Preserve frozen evidence bytes. Describe current execution state in registries and generated views rather than rewriting an executed protocol in place.
7. Run the required checks and inspect `git status` afterward. A green run is invalid if it deleted a required test or left new evidence untracked.

Do not finish an evaluation run with stale `ready-not-run`, `no production result`, empty-registry, mandatory-quality-review, or baseline-rerun guidance in active surfaces.

## Required checks

```bash
python3 scripts/update_workflow_runbook.py --check
python3 scripts/validate_repository.py
python3 scripts/test_workflow_evaluation_contract.py
truthmark check --json
truthmark index --json
git diff --check
git status --short
```

When task contracts change, regenerate the affected `qualification-lifecycle-v0.json`, update the generated runbook, and refresh only current v0 execution contracts.

## Local review skills

Use the repository-local skill matching the work:

- `.agents/skills/benchmark-protocol-writer.md`
- `.agents/skills/claim-evidence-auditor.md`
- `.agents/skills/stack-ablation-planner.md`
- `.agents/skills/practical-software-quality-reviewer.md`
- `.agents/skills/scientific-report-reviewer.md`
- `.agents/skills/citation-light-prior-art-mapper.md`
- `.agents/skills/figure-table-planner.md`
