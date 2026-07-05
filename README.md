# Token Optimization Research

Research infrastructure for measuring provider-reported token usage and software quality in realistic coding-agent workflows.

## Current evaluation portfolio

The repository retains operationally valid Fastify, Beets, and Terraform provider-token baseline samples; their verifier and review outcomes are diagnostics, not selection gates. Invalid fixture runs and stale protocols were removed at the experiment owner's direction. Terraform's current verifier exercises pagination through rendered output instead of requiring one canonical private helper name. The only runnable task contracts remain:

| Sequence | Fixture | Ordered stages |
|---|---|---|
| `fastify-lifecycle-sequence-v0` | Fastify | feature → behavior-preserving refactor → code review |
| `beets-lifecycle-sequence-v0` | Beets | feature → behavior-preserving refactor → code review |
| `terraform-lifecycle-sequence-v0` | Terraform | feature → behavior-preserving refactor → code review |

Every lane uses one pinned repository snapshot and one persistent model session. The controller applies all three independently qualified start conditions before prompt 1, discloses prompts in order, preserves model/tool state, and runs all concealed verifiers after prompt 3.

Phase 3 keeps these lifecycle-v0 contracts unchanged. Its first completed stack screen, `stack-tokenjuice-jcodemunch-mcp`, composes TokenJuice as the terminal-output owner with jcodemunch MCP as the retrieval-context owner and reuses the retained `r1` baseline and individual-tool samples. The stack used 9.12% fewer provider tokens than bare Codex but 27.19% more than TokenJuice alone, so it did not advance.

## Documentation

Start with [`docs/README.md`](docs/README.md). The main destinations are:

- [`docs/papers/`](docs/papers/README.md) — completed research papers and phase reports;
- [`docs/evaluations/`](docs/evaluations/README.md) — evaluation design and operator guidance;
- [`docs/research/`](docs/research/README.md) — current roadmap and research direction;
- [`docs/tool-dossiers/`](docs/tool-dossiers/README.md) — tool index and source-inspection dossiers;
- [`templates/`](templates/README.md) — blank outlines and reusable templates.

## Source of truth

- `data/workflow-task-sequences.json` — lifecycle v0 contracts.
- `data/repository-fixtures.json` — pinned fixture readiness.
- `sources/evaluations/fixtures/` — task prompts, start patches, controller acceptance, and generated v0 qualification evidence.
- `data/workflow-sessions.json` — retained provider-backed token samples, diagnostic model outcomes, and experiment-invalid exclusions.
- `docs/evaluations/operations/runbook.md` — generated operator runbook.
- `docs/papers/phase-2-lifecycle-v0-natural-use-screening.md` — production screening report for the retained baseline and treatment evidence.

## Validation

```bash
python3 scripts/validate_repository.py
python3 scripts/test_workflow_evaluation_contract.py
```

Qualification evidence is executable and generated only by:

```bash
python3 scripts/generate_workflow_qualification.py fastify-lifecycle-sequence-v0 sources/evaluations/fixtures/medium/fastify-fastify/repo
python3 scripts/generate_workflow_qualification.py beets-lifecycle-sequence-v0 sources/evaluations/fixtures/medium/beetbox-beets/repo
python3 scripts/generate_workflow_qualification.py terraform-lifecycle-sequence-v0 sources/evaluations/fixtures/large/hashicorp-terraform/repo
```

See `AGENTS.md` before changing evaluation contracts.
