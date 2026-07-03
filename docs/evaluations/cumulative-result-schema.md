# Cumulative Result Schema

## Purpose

The research program is iterative: each run must be appendable without changing earlier records. The repository therefore treats `data/evaluations.json` as a compact append-only index and stores raw evidence under `sources/evaluations/**/runs/<evaluation-id>/`.

## Primary objectives

1. Evaluate individual token-saving tools on complex software-engineering tasks.
2. Evaluate compatibility-safe tool stacks on the same kind of complex tasks.

Synthetic micro fixtures and recorded diagnostic fixtures are useful for calibration, sanity checks, and diagnostic-preservation tests. They do not support primary objective claims by themselves.

## Core entities

| Entity | File | Role |
|---|---|---|
| Repository fixture | `data/repository-fixtures.json` | Defines target repository, scale, setup/reset/verifier, and whether the fixture is calibration or primary-objective material. |
| Evaluation profile | `data/evaluation-profiles.json` | Standardizes baseline, individual-tool, stack, replacement-runtime, installer, and comparator profiles. |
| Run record | `data/evaluations.json` plus raw run directory | Records one baseline, individual-tool treatment, stack treatment, replacement runtime, or audit-only run. |
| JSON schema | `schemas/evaluation-run-record.schema.json` | Defines the canonical run-record shape for future tooling. |

## Append-only run policy

- Add one run record per executed baseline or treatment.
- Use the same `experiment_group_id` for a baseline and all directly comparable treatments.
- Use `objective = individual_tool_effectiveness` for one tool, comparator, or replacement-runtime treatment.
- Use `objective = stack_effectiveness` for two-or-more-component stack treatments.
- Use `replicate_index` to accumulate repeated runs without overwriting the original.
- Supersede records instead of deleting failed, excluded, or negative results.
- Do not create paired comparisons or aggregate summaries until the referenced run records exist.

## Required metric groups

Each run must record:

1. `token_usage` — provider-billed tokens when available, cache tokens, output/reasoning tokens, artifact-token estimates, pricing basis.
2. `agent_behavior` — turns, tool calls, correction turns, wall time.
3. `software_quality` — verifier pass/fail, quality score, critical failures, diagnostic preservation.
4. `operational_reproducibility` — install log, reset verification, raw-artifact recovery, state leakage, tool-isolation audit result.

## Complex-project policy

Primary objective claims require `fixture_scale = large-project` and `evidence_stage = reproduction` unless a report explicitly scopes itself to calibration or benchmark-audit evidence.

The retained generated/recorded fixtures are calibration and diagnostic gates. The candidate primary fixtures are public large projects listed in `data/large-project-candidates.json`; each must be promoted from `candidate-fixture` only after a clean pinned snapshot, frozen prompt, setup policy, reset policy, and verifier exist.

## Directory convention

```text
sources/evaluations/large-projects/<project-id>/runs/<evaluation-id>/
  run-record.json
  transcript.jsonl
  provider-usage.json
  verifier-output.txt
  quality-review.md
  diff.patch or artifacts/
```

A compact copy of the run-record metadata may be appended to `data/evaluations.json`, but raw evidence remains in the run directory.
