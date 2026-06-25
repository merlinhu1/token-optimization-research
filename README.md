# Token Optimization Research

A research workspace for studying token-saving techniques in AI coding agents.

This repository is not a list of tips. It is organized around a research system:

- collect implementations and claims with provenance;
- decompose products into atomic techniques;
- model compatibility and conflicts between techniques;
- evaluate techniques independently from bundled stacks;
- synthesize findings into papers, standards, and reusable prompts.

## Start here

- Architecture: [`docs/architecture/README.md`](docs/architecture/README.md)
- Domain model: [`docs/architecture/domain-model.md`](docs/architecture/domain-model.md)
- Compatibility model: [`docs/architecture/compatibility-graph.md`](docs/architecture/compatibility-graph.md)
- Research workflows: [`docs/architecture/workflows.md`](docs/architecture/workflows.md)
- Evaluation framework: [`docs/evaluations/evaluation-framework.md`](docs/evaluations/evaluation-framework.md)

## Validate the workspace

```bash
python3 scripts/validate_repository.py
```

## Current status

The repository is in architecture/bootstrap phase. Seed material lives in `sources/seed-catalogs/`; canonical research records live under `data/`.
