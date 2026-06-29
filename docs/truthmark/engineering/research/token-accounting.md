---
status: active
truth_kind: engineering-contract
last_reviewed: 2026-06-29
---

# Token Accounting And Benchmark Protocols

## Purpose

This doc owns the durable token-accounting and benchmark-protocol contract.

It prevents visible prompt estimates from being reported as measured savings.

## Scope

This doc covers Phase 2 benchmark design, token metrics, artifacts, and run records.

Software-quality scoring is owned by `software-quality-gates.md`.

## Current Implementation Behavior

- Phase 2 evaluation docs define benchmark planning and token-accounting standards.
- Phase 2 includes a source-logic stack hypothesis portfolio with baselines, lower-intervention comparators, broad-owner comparators, installer/orchestrator reproducibility profiles, and replacement-agent lanes.
- Evaluation templates define task and run-record artifacts.
- `data/evaluations.json` is the structured evaluation registry.

## Product Truth Links

- None. This is an engineering research contract, not product truth.

## Contract Surface

- Benchmark protocols, evaluation records, run-record schema, and token-usage reporting boundaries.

## Inputs

- Task fixtures, prompts, models, allowed tools, provider usage records, raw outputs, and verifier output.

## Outputs

- Evaluation records that distinguish provider-billed usage from estimates and preserve quality evidence.


## Contract

- Protocols are written before results.
- Baseline and treatment tasks use the same fixture, prompt, model, and allowed-tool boundary unless an explicit protocol explains the difference.
- Provider-billed task usage is the preferred token-accounting boundary.
- Fresh input, cached input, cache-write, output, and reasoning tokens should be recorded when available.
- Estimated tool-result tokens are secondary evidence.
- Benchmark-audit records require raw outputs or recoverable raw-output paths.
- Reproduction records require independent target-workload runs.
- Percentage savings must be paired with absolute token and cost values when available.

## Engineering Decisions

- Decision (2026-06-26): Phase 2 emphasizes benchmark-audit readiness before controlled stack reproduction.
- Decision (2026-06-26): Run records should separate provider-billed usage from estimates.
- Decision (2026-06-26): A treatment does not win if it saves tokens by under-solving the task.
- Decision (2026-06-29): Phase 2 profile roles such as comparator, broad-owner, installer, or replacement-runtime lane are not evidence stages; each component still carries `source-logic`, `benchmark-audit`, or `reproduction` status.

## Rationale

Token-saving tools often move cost between prompt text, tool calls, cache writes, output, and reasoning.

The repo needs accounting boundaries that expose those tradeoffs.

## Non-Goals

- This doc does not store benchmark results.
- This doc does not select the winning stack.
- This doc does not replace per-run artifacts under evaluation sources.

## Maintenance Notes

- Update this doc when `templates/evaluation-run-record.json` changes schema.
- Update this doc when the Phase 2 benchmark plan changes required metrics.
- Keep benchmark-protocol wording aligned with the repo-local `benchmark-protocol-writer` skill.

## Source References

- ../../../../docs/evaluations/evaluation-framework.md
- ../../../../docs/evaluations/phase-2-benchmark-plan.md
- ../../../../docs/evaluations/token-usage-and-quality-standards.md
- ../../../../docs/evaluations/immediately-usable-flows.md
- ../../../../templates/evaluation-record.md
- ../../../../templates/evaluation-task.md
- ../../../../templates/evaluation-run-record.json
- ../../../../prompts/evaluator.md
- ../../../../data/evaluations.json
- ../../../../.agents/skills/benchmark-protocol-writer.md
