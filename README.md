# Token Optimization Research

Research infrastructure for measuring weighted token cost and software quality in realistic coding-agent workflows. Weighted token cost (`fresh input + 0.1 × cached input + 6 × output`) is the repository's sole token metric; raw provider counters are calculation/audit telemetry only.

## Current evaluation portfolio

The active portfolio is **Lifecycle V2** for two medium-project lanes. Both lanes have passed provider-free qualification. Fastify holds two baseline replicates. Beets was repinned on 2026-08-22 to reach a minable window of upstream history and holds none, so it needs fresh baselines before it can carry a comparison. No treatment has run against either lane. New Codex CLI and OpenCode evaluations use GPT-5.6 Sol/medium; new Claude Code evaluations use direct-Anthropic Claude Opus 5/medium. High-effort conditions are historical only because the added deliberation can increase trajectory divergence. Each task pre-seeds an authentic semantic regression from completed upstream behavior and gives the agent a normal software-engineering objective: implement the requested outcome correctly, search and inspect related code, preserve prior work, and validate appropriately. Prompts state the observable symptom and never name the file, function, or test, so locating the defect remains real retrieval work, and they do not disclose evaluator scoring or controller commands. The controller applies every regression as one composite start before prompt 1; after the final prompt it runs each task verifier and one frozen project-wide compile command. Every task requires affected-component compilation plus one narrow essential-behavior smoke check. Broader tests, behavioral fidelity, style, maintainability, and source review are diagnostics. The active lifecycle portfolio is:

| Sequence | Fixture | Ordered stages |
|---|---|---|
| `fastify-lifecycle-sequence-v2` | Fastify | 6 bounded defect repairs |
| `beets-lifecycle-sequence-v2` | Beets | 7 bounded defect repairs |

<!-- generated:corpus-summary -->
The active registry contains 12 accepted provider-backed sessions: 8 baselines, 4 replacement-runtime controls. By sequence: 6 `beets-lifecycle-sequence-v2`, 6 `fastify-lifecycle-sequence-v2`. By runtime: Claude Code 2, Codex CLI 6, OpenCode CLI 4.

Weighted token cost decomposes as agent steps times weighted cost per step. `c86863838e8b` holds 4 replicates (64, 64, 63, 123 agent steps, spread 95.2%); weighted cost per step spread 98.5%; `dc16afea3ad5` holds 4 replicates (69, 73, 76, 138 agent steps, spread 100.0%); weighted cost per step spread 35.2%.
<!-- /generated:corpus-summary -->

## Retired evidence

Lifecycle V0 was retired on 2026-08-14 under [`sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json`](sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json). Its 212 sessions, their compact artifact roots, and 224 frozen protocols were deleted from the active corpus at the experiment owner's direction.

The retirement is a design judgement, not an allegation about any individual run. V0 prompts used solution-directed task assistance: they prescribed target files, symbols, implementation steps, and validation commands to reduce trajectory variance. That suppresses the repository search and exploration where context-reduction tools actually act, so a V0 token delta is not attributable to a tool's effect on realistic agent work. Provider totals from those runs were real; the workload they measured was not representative. The receipt records that fault separately from the two narrower ones already adjudicated — the 2026-07-18 official-integration parity failures and the Baseline V3 verifier-environment defect corrected by V4.

Papers reporting V0 results are retained and annotated rather than withdrawn, because negative findings and exclusions are part of the research record ([ADR 0003](docs/architecture/decision-records/0003-methodology-and-reporting.md)). Their numbers are no longer reproducible from this repository. Terraform was a V0-only lane and has no active fixture or task contract.

## Documentation

Start with [`docs/README.md`](docs/README.md). The main destinations are:

- [`docs/papers/`](docs/papers/README.md) — completed research papers and phase reports;
- [`docs/evaluations/`](docs/evaluations/README.md) — evaluation design and operator guidance;
- [`docs/research/`](docs/research/README.md) — current roadmap and research direction;
- [`docs/tool-dossiers/`](docs/tool-dossiers/README.md) — tool index and source-inspection dossiers;
- [`templates/`](templates/README.md) — blank outlines and reusable templates.

## Source of truth

- `data/workflow-task-sequences.json` — Lifecycle V2 contracts.
- `data/repository-fixtures.json` — pinned fixture readiness.
- `sources/evaluations/fixtures/` — task prompts, start patches, controller acceptance, and generated V2 qualification evidence.
- `data/workflow-sessions.json` — active retained provider-backed controls and objective-eligible treatment samples; corrupted treatments are represented only by deletion receipts.
- `docs/evaluations/operations/runbook.md` — generated operator runbook.
- `docs/papers/opencode-four-tool-screen-20260808.md` — archived pre-correction OpenCode Lifecycle V1 screen.
- `docs/papers/phase-2-natural-use-screening.md` — archived pre-correction Lifecycle V1 screening report.
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
python3 scripts/generate_workflow_qualification.py fastify-lifecycle-sequence-v2 sources/evaluations/fixtures/medium/fastify-fastify/repo
python3 scripts/generate_workflow_qualification.py beets-lifecycle-sequence-v2 sources/evaluations/fixtures/medium/beetbox-beets/repo
```

Executed provider-free integration matrices are published with `scripts/publish_integration_qualification.py`; the publisher rejects nonzero lanes, provider-backed session creation, failed preparation, failed host integration, failed warmup, or failed MCP handshakes.

See `AGENTS.md` before changing evaluation contracts.
