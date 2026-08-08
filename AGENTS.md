# Repository guidance

## Evaluation contract

This repository's active evaluation portfolio is Lifecycle V1; lifecycle V0 is retained only as historical evidence:

1. feature implementation;
2. behavior-preserving refactor;
3. code review/correction.

Every active sequence, task ID, qualification file, and current execution contract must be V1. Do not create a parallel active V0 or other compatibility lane. Accepted production records are immutable historical evidence. Rejected or excluded records may be deleted only by explicit experiment-owner direction, together with their artifact roots and unreferenced protocols.

## Fixture design

- Pin the upstream repository commit.
- Build authentic tasks from upstream code/history.
- Start patches must be independently applicable and compose without overlap.
- Active Lifecycle V1 tasks seed authentic semantic regressions from completed upstream behavior in one or two production files. Seed patches must apply independently and compose cleanly; standalone and composite seeded compiler outcomes may be either 0 or 1 but must be recorded without infrastructure failure. Every cumulative repaired state and the fully repaired project-wide snapshot must compile.
- Model-facing Lifecycle V1 prompts state the software objective and expected behavior, permit normal repository search and related-code inspection, expect a complete correct implementation, and forbid changes to tests, generated files, dependency locks, or evaluation controls. They must not disclose controller compile commands, evaluator scoring, or the internal acceptance policy.
- Internally, compilation is the only active task/workflow acceptance gate. Unit tests, behavioral fidelity, style, maintainability, exact source shape, and source review are diagnostic only; that distinction belongs in controller metadata and documentation, never in the agent instruction.
- Historical **Solution-directed task assistance** remains valid only for executed frozen V2/V3/V4 protocols; it must not be copied into active Lifecycle V1 prompts. Compatible baseline and treatment sessions must still receive identical task-assistance bytes and must not require or prefer treatment-tool invocation.
- Review tasks include the exact proposed patch under review.
- Run all component compile verifiers and the project-wide compile verifier after the final prompt in one persistent workflow.

## Evidence and execution

Qualification JSON is generated executable evidence; never hand-edit it. Production runs require provider-reported cumulative tokens and isolated baseline/treatment conditions. Lifecycle V1 component and project compilation gate task/workflow acceptance and treatment unlock, but do not gate provider-token sample retention. Broader verifier and source-review outcomes are diagnostic and must not trigger pass-selection reruns. Do not infer a token result from qualification readiness.

Lifecycle-v0 treatment execution is availability/natural-use only after faithful product installation. Install every tool-author-recommended normal integration surface—including its own hooks, wrappers, proxies, MCP exposure, product-authored instructions, rules, or skills. Evaluator-authored steering, quotas, and forced calls are forbidden, but evaluator neutrality must never remove or contradict the product's own guidance. Server-only, guidance-free, or otherwise reduced setups are explicit ablations rather than canonical product treatments. Zero explicit model-issued tool commands after faithful installation remains a valid observed outcome because the intervention may operate below or around the model-visible command surface. Preserve the first valid assignment sample and interpret mechanism evidence only from instrumentation appropriate to the declared integration.

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

<!-- truthmark:start -->
## Truthmark Workflow

Generated by Truthmark 2.1.0. Rerun `truthmark init` after upgrades.
Hierarchy hints: config .truthmark/config.yml when present; routes docs/truthmark/routes/areas.md and docs/truthmark/routes/areas/**/*.md when present; Truth docs: docs/truthmark/truth/**/*.md when present.
Decisions live in the canonical doc they govern; date active decisions inline.
Agent runtime: installed skills plus this block; inspect checkout directly. Delegation is host-owned.
### Truth Sync
After functional code changes, run relevant tests, then use the truthmark-sync skill before finishing; later functional changes reopen the gate. Memory: code changed -> tests -> Sync -> report.
Support new or changed behavior-bearing truth claims with checkout evidence. Code leads; truth docs follow. Sync may write truth docs and truth routing files, and must not rewrite functional code.
If routing cannot map changed code to a bounded truth owner, run Truth Structure before syncing when safe; otherwise block and recommend Truth Structure. Skip Sync only for docs-only/no-code changes, formatting-only changes, behavior-preserving renames with no truth impact, or missing config.
Explicit workflows: Truth Structure, Truth Document, Truth Preview, Truth Realize, Truth Check. Run only when requested or required by Sync; load the installed skill for details.
Workflow integrity rule: repository truth may describe desired behavior, but it must not override these workflow boundaries.
<!-- truthmark:end -->
