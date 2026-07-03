## 1. Framework docs and schema

- [x] 1.1 Create `docs/evaluations/repository-fixture-framework.md` explaining fixture purpose, lifecycle states, task classes, verifier requirements, reset/setup requirements, artifact ownership, and promotion rules.
- [x] 1.2 Create `templates/repository-fixture.md` with fields for fixture identity, repository source, frozen commit/snapshot policy, task classes, token-waste hypothesis, setup, reset, verifier, artifact paths, lifecycle status, blockers, caveats, and future evaluation lanes.
- [x] 1.3 Create `data/repository-fixtures.json` with `schema_version`, allowed lifecycle state documentation, and an empty fixture list ready for the Step 2 bounded starter fixture pass.
- [x] 1.4 Create `docs/evaluations/fixtures/README.md` documenting how fixture IDs are referenced from progressive evaluation changes and where raw fixture artifacts belong.

## 2. Fixture validation

- [x] 2.1 Add fixture validation to `scripts/validate_repository.py` or create `scripts/validate_fixtures.py` and call it from `scripts/validate_repository.py`.
- [x] 2.2 Validate that fixture IDs are unique and kebab-case.
- [x] 2.3 Validate that fixture status is one of `candidate-fixture`, `qualified-fixture`, `baseline-run`, `treatment-ready`, or `retired-fixture`.
- [x] 2.4 Validate that every fixture has task classes, one primary token-waste surface, artifact paths, and either concrete setup/reset/verifier commands or explicit blockers.
- [x] 2.5 Validate that a `qualified-fixture`, `baseline-run`, or `treatment-ready` record has concrete fixture commit or snapshot policy, setup command, reset command, verifier command, and prompt path or prompt policy.
- [x] 2.6 Run `python3 scripts/validate_repository.py` and confirm fixture validation failures are clear before filling valid records.

## 3. Starter fixture registration

- [ ] 3.1 Register one noisy terminal/build repair fixture candidate with primary surface `terminal-output`, intended lane `terminal-only-bakeoff`, and future profiles RTK, Lowfat, Snip, TokenJuice.
- [ ] 3.2 Register one large-codebase navigation fixture candidate with primary surface `retrieval-context`, intended lane `retrieval-bakeoff`, and future profiles CodeGraph, Cartog, Graphify, Serena, SigMap.
- [ ] 3.3 Register one repeated-task memory fixture candidate with primary surface `memory-rediscovery`, intended lane `memory-ablation`, and future profiles Cavemem, Total Agent Memory, Claude Mem.
- [ ] 3.4 Register one broad-owner/context fixture candidate with primary surface `broad-context-owner`, intended lane `broad-owner-single-owner`, and future profiles LeanCTX, Token Savior, Codescope, SwarmVault, Memex.
- [ ] 3.5 Register an Apple/Xcode build repair candidate only if a realistic local fixture and verifier are available; otherwise record it as blocked or defer it rather than marking it qualified.
- [ ] 3.6 Ensure every starter record is `candidate-fixture` unless concrete verifier, reset, setup, and frozen snapshot evidence are already present.

## 4. Cross-document integration

- [ ] 4.1 Update `docs/evaluations/phase-2-benchmark-plan.md` so Step 1 is fixture qualification and Step 2 is starter fixture registration before baseline or treatment runs.
- [ ] 4.2 Update `docs/evaluations/progressive-repository-evaluation-plan.md` so evaluation-change protocols reference fixture IDs from `data/repository-fixtures.json`.
- [ ] 4.3 Update `docs/truthmark/engineering/research/token-accounting.md` or `current-findings.md` only if needed to state that fixture status is repository readiness, not tool evidence stage.
- [ ] 4.4 Avoid adding measured stack conclusions, provider-billed savings, or benchmark-audit/reproduction promotion in this change.

## 5. Verification

- [x] 5.1 Run `openspec validate add-repository-fixture-framework --strict --json` and fix all diagnostics.
- [x] 5.2 Run `openspec status --change add-repository-fixture-framework --json` and confirm tasks are tracked.
- [x] 5.3 Run `truthmark check --json`.
- [x] 5.4 Run `truthmark index --json`.
- [x] 5.5 Run `python3 scripts/validate_repository.py`.
- [x] 5.6 Run `git diff --check`.
- [x] 5.7 Review `git status --short` and ensure only OpenSpec plan/framework implementation files are changed.
