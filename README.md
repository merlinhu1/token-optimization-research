# Token Optimization Research

Research infrastructure for measuring provider-reported token usage and software quality in realistic coding-agent workflows.

## Current evaluation portfolio

The repository retains operationally valid Fastify and Beets Lifecycle V1 provider-token evidence. The owner-declared-invalid Terraform Lifecycle V1 r0 was removed under an invalidation receipt. The active portfolio is **Lifecycle V1** for the two medium-project lanes. Each task pre-seeds an authentic semantic regression from completed upstream behavior and gives the agent a normal software-engineering objective: implement the requested outcome correctly, search and inspect related code, preserve prior work, and validate appropriately. Agent prompts do not disclose evaluator scoring or controller compile commands. After task 3, the controller runs the affected-component compile commands and one frozen project-wide compile command. Internally, component and final project compilation are the only pass/fail gates; tests, behavioral fidelity, style, maintainability, and source review are diagnostics. The active lifecycle portfolio is:

| Sequence | Fixture | Ordered stages |
|---|---|---|
| `fastify-lifecycle-sequence-v1` | Fastify | feature → behavior-preserving refactor → code review |
| `beets-lifecycle-sequence-v1` | Beets | feature → behavior-preserving refactor → code review |

Lifecycle V1 provider-free qualification passes every standalone, composite, cumulative, aggregate, and project-wide compile boundary. Fastify and Beets each retain one bare-Codex GPT-5.6 Sol/`high` r0 pilot; bare-Codex treatment remains machine-blocked until its required pilot audit exists. Direct-Anthropic Claude Code Sonnet 5/high retains thirteen accepted Fastify treatment lanes. Against the accepted Fastify Claude baseline (460,555.0 weighted units), RTK, Graphify, Snip, LowFat, Caveman, Token Savior, LeanCTX, jCodeMunch, CodeScope, Serena, Ponytail, SigmaP, and CodeGraph changed weighted usage by -28.02%, -20.08%, -9.82%, -6.14%, -4.23%, +7.50%, +16.14%, +17.10%, +18.92%, +22.22%, +30.86%, +54.35%, and +107.62%. Beets now retains RTK and Cartog at +55.02% and +135.20% versus its 436,553.2-weighted baseline. Fastify/Cartog and Fastify/TokenJuice remain occupied excluded failures. Thirteen Beets lanes remain unlaunched, so these incomplete results are not ranking evidence. Terraform is not an active Lifecycle V1 lane: its owner-declared-invalid r0 frozen protocol, raw evidence, and retirement receipt were deleted under `sources/evaluations/audits/lifecycle-v1-terraform-invalidated-20260802.json`; retained task and qualification sources cannot authorize a rerun or treatment.

RepoWise 0.39.0 is pinned at `a3b6714c5523dc7c45d6bce0522035339bcf3afd`. The provider-backed Codex V2 screen completed valid Fastify and Beets lanes: 5,690,107 and 2,326,247 provider tokens, respectively, or +342.03% and +97.38% versus matched bare-Codex controls (+151.57% and +119.89% on the fresh-input-plus-output view). These are single-replicate screening observations (`eligible_for_ranking: false`). The provider-configured OpenCode protocols remain prepared but unexecuted. The earlier provider-free setup was invalid; its results and protocols were deleted under the recorded receipt, and any future no-provider fallback is discarded before registry publication.

The 2026-08-08 OpenCode Lifecycle V1 screen completed eight accepted lanes for Graphify, LeanCTX, Snip, and CodeScope across Fastify and Beets. The two-sequence descriptive weighted deltas versus matched bare OpenCode were Graphify -12.49%, LeanCTX +16.33%, Snip -26.61%, and CodeScope -0.52%. These are single-replicate observations marked `eligible_for_ranking: false`; Cartog was explicitly excluded before provider execution because its pinned native binary did not reproduce the frozen artifact identity. See [`docs/papers/opencode-four-tool-lifecycle-v1-screen-20260808.md`](docs/papers/opencode-four-tool-lifecycle-v1-screen-20260808.md).

Direct-Anthropic Claude Code completed bounded baseline campaigns for `claude-code-anthropic-sonnet-5-high` (`claude-sonnet-5`, `high` effort; 6,207,153 provider tokens / 897,108.2 weighted units) and `claude-code-anthropic-opus-5-high` (`claude-opus-5`, `high` effort; 7,343,190 provider tokens / 1,167,276.7 weighted units), each across Fastify and Beets with six task turns. Opus used 30.12% more weighted token cost than Sonnet; Sonnet was already 73.85% above matched Codex and 22.71% above matched OpenCode weighted baselines, so subsequent Claude Code treatment experiments continue with Sonnet 5/high. Opus remains a baseline-only reference. Provider-free qualification passed all 30 native Claude lanes for the 15 Claude-native profiles; the serialized Sonnet treatment matrix is now owner-authorized, while SDL-MCP remains excluded for its Codex-only installer surface. See the [Sonnet preparation authority](sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-protocol-preparation-20260808.json), [qualification receipt](sources/evaluations/audits/corrected-integration-qualification-claude-code-anthropic-sonnet-5-high-lifecycle-v1-20260810.json), and [treatment authorization](sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-treatment-authorization-20260810.json).

<!-- generated:corpus-summary -->
The active registry holds no provider-backed sessions. A corrected task family mints new qualification and protocol identities, so the prior corpus is archived and fresh execution is required before any result claim.

Archived generations: `lifecycle-v1-pre-corrected-prompts-20260813` (103 sessions).
<!-- /generated:corpus-summary -->

## Retired evidence

Lifecycle V0 was retired on 2026-08-14 under [`sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json`](sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json). Its 212 sessions, their compact artifact roots, and 224 frozen protocols were deleted from the active corpus at the experiment owner's direction.

The retirement is a design judgement, not an allegation about any individual run. V0 prompts used solution-directed task assistance: they prescribed target files, symbols, implementation steps, and validation commands to reduce trajectory variance. That suppresses the repository search and exploration where context-reduction tools actually act, so a V0 token delta is not attributable to a tool's effect on realistic agent work. Provider totals from those runs were real; the workload they measured was not representative. The receipt records that fault separately from the two narrower ones already adjudicated — the 2026-07-18 official-integration parity failures and the Baseline V3 verifier-environment defect corrected by V4.

Papers reporting V0 results are retained and annotated rather than withdrawn, because negative findings and exclusions are part of the research record ([ADR 0003](docs/architecture/decision-records/0003-methodology-and-reporting.md)). Their numbers are no longer reproducible from this repository. Terraform was a V0-only lane; its fixture registration is kept so a future large-project V1 lane remains possible, but it has no active tasks.

## Documentation

Start with [`docs/README.md`](docs/README.md). The main destinations are:

- [`docs/papers/`](docs/papers/README.md) — completed research papers and phase reports;
- [`docs/evaluations/`](docs/evaluations/README.md) — evaluation design and operator guidance;
- [`docs/research/`](docs/research/README.md) — current roadmap and research direction;
- [`docs/tool-dossiers/`](docs/tool-dossiers/README.md) — tool index and source-inspection dossiers;
- [`templates/`](templates/README.md) — blank outlines and reusable templates.

## Source of truth

- `data/workflow-task-sequences.json` — Lifecycle V1 contracts.
- `data/repository-fixtures.json` — pinned fixture readiness.
- `sources/evaluations/fixtures/` — task prompts, start patches, controller acceptance, and generated V1 qualification evidence.
- `data/workflow-sessions.json` — active retained provider-backed controls and objective-eligible treatment samples; corrupted treatments are represented only by deletion receipts.
- `docs/evaluations/operations/runbook.md` — generated operator runbook.
- `docs/papers/opencode-four-tool-lifecycle-v1-screen-20260808.md` — current four-tool OpenCode Lifecycle V1 screen.
- `docs/papers/phase-2-lifecycle-v1-natural-use-screening.md` — current standalone Lifecycle V1 natural-use screening report.
- `sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json` — Lifecycle V0 retirement adjudication.

## Validation

`make check` runs the full `AGENTS.md` required-checks gate — generated-runbook drift, both
contract test suites, repository validation, and a working-tree comparison that fails if the checks themselves changed tracked or untracked state. Run it
before finishing any change to evaluation state; nothing runs it automatically.

```bash
make check
```

Individual entry points:

```bash
python3 scripts/validate_repository.py
python3 scripts/test_workflow_evaluation_contract.py
python3 scripts/test_claude_code_usage_contract.py
```

Both require `jsonschema` (see `requirements-dev.txt`): every registry record is gated on
`schemas/workflow-session-record.schema.json`, and validation fails closed without it.

Fixture qualification evidence is executable and generated by:

```bash
python3 scripts/generate_workflow_qualification.py fastify-lifecycle-sequence-v1 sources/evaluations/fixtures/medium/fastify-fastify/repo
python3 scripts/generate_workflow_qualification.py beets-lifecycle-sequence-v1 sources/evaluations/fixtures/medium/beetbox-beets/repo
```

Executed provider-free integration matrices are published with `scripts/publish_integration_qualification.py`; the publisher rejects nonzero lanes, provider-backed session creation, failed preparation, failed host integration, failed warmup, or failed MCP handshakes.

See `AGENTS.md` before changing evaluation contracts.
