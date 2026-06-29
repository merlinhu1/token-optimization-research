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
- Evaluation framework: [`docs/evaluations/evaluation-framework.md`](docs/evaluations/evaluation-framework.md)
- Token usage and quality standards: [`docs/evaluations/token-usage-and-quality-standards.md`](docs/evaluations/token-usage-and-quality-standards.md)
- Phase 2 benchmark plan: [`docs/evaluations/phase-2-benchmark-plan.md`](docs/evaluations/phase-2-benchmark-plan.md)
- Progressive repository-level evaluation plan: [`docs/evaluations/progressive-repository-evaluation-plan.md`](docs/evaluations/progressive-repository-evaluation-plan.md)
- Immediately usable evaluation flows: [`docs/evaluations/immediately-usable-flows.md`](docs/evaluations/immediately-usable-flows.md)
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

Phase 1 established 29 source-logic tool dossiers and a compatibility-safe stack report. The current active direction is Phase 2: benchmark design, token-usage accounting, software-quality standards, and immediately usable evaluation flows before controlled stack reproduction.
