# Repository guidance

## Evaluation contract

This repository's only evaluation framework is Lifecycle V1. Lifecycle V0 was retired on 2026-08-14 under `sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json` and no longer exists in the corpus:

1. feature implementation;
2. behavior-preserving refactor;
3. code review/correction.

Every active sequence, task ID, qualification file, and current execution contract must be V1. Do not reintroduce a V0 or other compatibility lane. Accepted production records are immutable historical evidence. Rejected or excluded records may be deleted only by explicit experiment-owner direction, together with their artifact roots and unreferenced protocols.

## Fixture design

- Pin the upstream repository commit.
- Build authentic tasks from upstream code/history.
- Start patches must be independently applicable and compose without overlap.
- Active Lifecycle V1 tasks seed authentic semantic regressions from completed upstream behavior in one or two production files. Seed patches must apply independently and compose cleanly; standalone and composite seeded compiler outcomes may be either 0 or 1 but must be recorded without infrastructure failure. Every cumulative repaired state and the fully repaired project-wide snapshot must compile.
- Model-facing Lifecycle V1 prompts state the software objective and expected behavior, permit normal repository search and related-code inspection, expect a complete correct implementation, and forbid changes to tests, generated files, dependency locks, or evaluation controls. They must not disclose controller compile commands, evaluator scoring, or the internal acceptance policy.
- Internally, compilation is the only active task/workflow acceptance gate. Unit tests, behavioral fidelity, style, maintainability, exact source shape, and source review are diagnostic only; that distinction belongs in controller metadata and documentation, never in the agent instruction.
- **Solution-directed task assistance** is forbidden. Prescribing target files, symbols, implementation steps, or validation commands suppresses the search and exploration that context-reduction tools act on, which is why Lifecycle V0 was retired; see [ADR 0005](docs/architecture/decision-records/0005-token-accounting-and-protocol-identity.md). Compatible baseline and treatment sessions must receive identical prompt bytes and must not require or prefer treatment-tool invocation.
- Review tasks include the exact proposed patch under review.
- Run all component compile verifiers and the project-wide compile verifier after the final prompt in one persistent workflow.

## Evidence and execution

Qualification JSON is generated executable evidence; never hand-edit it. Production runs require provider-reported cumulative tokens and isolated baseline/treatment conditions. Lifecycle V1 component and project compilation gate task/workflow acceptance and treatment unlock, but do not gate provider-token sample retention. Broader verifier and source-review outcomes are diagnostic and must not trigger pass-selection reruns. Do not infer a token result from qualification readiness.

Treatment execution is availability/natural-use only after faithful product installation. Install every tool-author-recommended normal integration surface—including its own hooks, wrappers, proxies, MCP exposure, product-authored instructions, rules, or skills. Evaluator-authored steering, quotas, and forced calls are forbidden, but evaluator neutrality must never remove or contradict the product's own guidance. Server-only, guidance-free, or otherwise reduced setups are explicit ablations rather than canonical product treatments. Zero explicit model-issued tool commands after faithful installation remains a valid observed outcome because the intervention may operate below or around the model-visible command surface. Preserve the first valid assignment sample and interpret mechanism evidence only from instrumentation appropriate to the declared integration.

## Documentation lifecycle

An action that changes research state must update every active surface that reports that state in the same change. This includes an evaluation run, qualification or protocol refresh, fixture promotion or retirement, session merge or deletion, treatment comparison, evidence-stage promotion, and a change to eligibility or interpretation policy.

After such an action:

1. Update the machine authority first: `data/workflow-sessions.json`, `data/repository-fixtures.json`, and any affected sequence/profile registry.
2. Regenerate the derived surfaces; never hand-edit generated content:
   - `python3 scripts/update_workflow_runbook.py` for `docs/evaluations/operations/runbook.md`;
   - `python3 scripts/update_registry_summaries.py` for the `generated:corpus-summary` blocks in `README.md` and `sources/evaluations/README.md`.
   `make check` fails when either is stale, so do not restate corpus counts, role splits, or runtime splits in prose by hand -- put them in a generated block instead.
3. Reconcile the narrative that generation cannot own: `docs/evaluations/README.md`, `docs/research/roadmap.md`, and any interpretation claim that depends on the changed state.
4. Reconcile active prompts, templates, repo-local skills, schemas, and architecture decision records when the contract changes. Search for the retired status, path, policy phrase, protocol/session ID, and lifecycle term.
5. If a document or template has no distinct maintained authority or current consumer, delete it and remove its references instead of leaving a second stale workflow.
6. Preserve frozen evidence bytes. Describe current execution state in registries and generated views rather than rewriting an executed protocol in place.
7. Run the required checks and inspect `git status` afterward. A green run is invalid if it deleted a required test or left new evidence untracked.

Do not finish an evaluation run with stale `ready-not-run`, `no production result`, empty-registry, mandatory-quality-review, or baseline-rerun guidance in active surfaces.

## Required checks

Run `make check`. It is the executable definition of this gate, so the list below documents one
target rather than a second checklist that can drift from it. Nothing runs it automatically:
this repository has no CI, and an unrun gate is the same as no gate.

```bash
make check
```

That target runs, in order:

```bash
python3 scripts/update_workflow_runbook.py --check
python3 scripts/update_registry_summaries.py --check
python3 scripts/test_workflow_evaluation_contract.py
python3 scripts/test_claude_code_usage_contract.py
python3 scripts/validate_repository.py
git diff --check
git status --short   # compared before and after; the run fails if the checks changed the tree
```

Repository validation gates every registry record on `schemas/workflow-session-record.schema.json`
and fails closed when `jsonschema` is absent, so install `requirements-dev.txt` first. When a
record shape legitimately changes, update the schema in the same change: it is enforced against
all retained sessions, not just new ones.

When task contracts change, regenerate the affected `qualification-lifecycle-v1-*.json`, regenerate the runbook and registry summaries, and refresh only current V1 execution contracts. A model-facing prompt change mints new qualification and protocol identities and archives the prior corpus.

## Local review skills

Use the repository-local skill matching the work:

- `.agents/skills/benchmark-protocol-writer.md`
- `.agents/skills/claim-evidence-auditor.md`
- `.agents/skills/stack-ablation-planner.md`
- `.agents/skills/practical-software-quality-reviewer.md`
- `.agents/skills/scientific-report-reviewer.md`
- `.agents/skills/citation-light-prior-art-mapper.md`
- `.agents/skills/figure-table-planner.md`
