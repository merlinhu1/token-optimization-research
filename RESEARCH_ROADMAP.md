# Research roadmap

## Phase 1 — Source-logic stack research

Status: complete for the current candidate set.

- Build the repository catalog and technique taxonomy.
- Create persistent source-logic dossiers for important token-saving tools.
- Define compatibility-safe stack candidates by surface ownership rather than popularity.
- Publish the Phase 1 compatibility-safe stack report.
- Keep `lead` entries out of stack recommendations until source-code logic is inspected.

## Phase 2 — Benchmark and evaluation framework

Status: active next phase.

- Audit benchmark examples already present in cited repositories, including tokbench, agentic-token-bench, Token Savior tsbench, CodeGraph benchmarks, Caveman Code MicroBench, Ponytail task benchmarks, and terminal-output reducer examples.
- Standardize token accounting around provider-billed task usage, cache effects, estimated artifact tokens, turn count, tool-call count, latency, and cost.
- Standardize software-quality gates: deterministic verifiers, diagnostic preservation, diff quality, maintainability, safety, reviewability, and reset/reversibility.
- Define immediately usable flows for benchmark-audit, terminal-output micro benchmarks, retrieval benchmarks, stack reproduction, replacement-agent comparison, and Tokless profile testing.
- Promote selected dossiers from `source-logic` to `benchmark-audit` only after harness, scoring, token accounting, raw outputs, and failure semantics are inspected.

## Phase 3 — Controlled stack reproduction

- Run baseline and treatment profiles on frozen task fixtures.
- Compare provider-billed task usage, pass rate, quality score, turns, tool calls, latency, and reset/reproducibility.
- Keep failed and negative runs in `data/evaluations.json`.
- Promote only reproduced findings toward deployment-grade recommendations.

## Phase 4 — Research outputs and standards

- Publish Phase 2 and Phase 3 reports with measured results and limitations.
- Update dossiers and standards based on benchmark-audit and reproduction findings.
- Version datasets, task fixtures, evaluation protocols, and run records with clear changelogs.
