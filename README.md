# Token Optimization Research

A research workspace for studying token-saving techniques in AI coding agents.

This repository is not a list of tips. It is organized around a research system:

- collect implementations and claims with provenance;
- decompose products into atomic techniques and owned surfaces;
- inspect source-code logic before using a tool in stack decisions;
- model compatibility and conflicts between techniques;
- evaluate techniques, stacks, replacement runtimes, and installer profiles with token-usage and software-quality standards;
- synthesize findings into reports, standards, prompts, and reusable evaluation flows.

## Start here

- Architecture: [`docs/architecture/README.md`](docs/architecture/README.md)
- Domain model: [`docs/architecture/domain-model.md`](docs/architecture/domain-model.md)
- Compatibility model: [`docs/architecture/compatibility-graph.md`](docs/architecture/compatibility-graph.md)
- Research workflows: [`docs/architecture/workflows.md`](docs/architecture/workflows.md)
- Evaluations index: [`docs/evaluations/README.md`](docs/evaluations/README.md)
- Workflow runbook and activation state: [`docs/evaluations/workflow-evaluation-runbook.md`](docs/evaluations/workflow-evaluation-runbook.md)
- Token usage and quality standards: [`docs/evaluations/token-usage-and-quality-standards.md`](docs/evaluations/token-usage-and-quality-standards.md)
- Methodology: [`docs/methodology/README.md`](docs/methodology/README.md)
- Research roadmap: [`docs/research/roadmap.md`](docs/research/roadmap.md)
- Research-reporting skill patterns: [`docs/research/report-writing-and-methodology-skill-patterns.md`](docs/research/report-writing-and-methodology-skill-patterns.md)
- Repo-local agent instructions and skills: [`AGENTS.md`](AGENTS.md), [`.agents/skills/`](.agents/skills/)
- Repository truth: [`docs/truthmark/routes/areas.md`](docs/truthmark/routes/areas.md), [`docs/truthmark/engineering/research/`](docs/truthmark/engineering/research/)
- Phase 1 report: [`docs/reports/phase-1-compatibility-safe-token-saving-stacks.md`](docs/reports/phase-1-compatibility-safe-token-saving-stacks.md)

## Validate the workspace

```bash
truthmark check --json
truthmark index --json
python3 scripts/validate_repository.py
```

## Current status

Phase 1 established source-logic tool dossiers and a compatibility-safe stack report. Fastify is the only current executable Phase 2 workflow suite. Its checkout-generated production qualification passes all seeded-fail, fixed-pass, cumulative, transition, alternative-repair, concealment, and five-file gates. New paid comparisons remain blocked only until a pool-matched accepted baseline exists; current sessions remain quality-review-pending and do not support token-savings claims.
