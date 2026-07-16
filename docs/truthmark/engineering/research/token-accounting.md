---
status: active
truth_kind: engineering-contract
last_reviewed: 2026-07-16
---

# Token Accounting And Evaluation Contracts

## Purpose

Define the boundary between fixture readiness and measured production evidence. Visible prompt estimates are never reported as measured savings.

## Current Implementation Behavior

- `data/workflow-task-sequences.json` defines exactly three lifecycle v0 sequences.
- `scripts/generate_workflow_qualification.py` produces fixed/start/composite readiness evidence from clean pinned checkouts.
- `scripts/refresh_workflow_contracts.py` writes current v0 execution contracts only after qualification succeeds.
- `scripts/run_codex_workflow_evaluation.py` pre-seeds one composite start, discloses prompts sequentially, preserves one warm model/tool/repository state, and runs every concealed verifier after the final prompt.
- `scripts/extract_codex_usage.py` normalizes provider usage.
- `scripts/audit_tool_isolation.py` verifies the selected baseline or treatment boundary.
- `data/workflow-sessions.json` is empty because no production execution has commenced.

## Contract

- Qualification proves fixture mechanics; it is not a model result.
- The only lifecycle contract is v0: feature implementation, behavior-preserving refactor, then code review/correction.
- A production run resets repository, profile, tool, and agent state before the lane and preserves them between prompts.
- Cumulative provider-reported workflow tokens are the primary accounting boundary. Record fresh input, cached input, cache-write, output, and reasoning components when available.
- Monetary cost estimation is outside the project objective.
- All concealed verifiers run without short-circuiting after the final prompt and emit structured per-task outcomes.
- Accepted evidence requires complete provider usage, controller acceptance, tool-isolation acceptance, final diff/status, and independent software-quality review.
- Baseline and treatment comparisons require the same fixture, sequence, model condition, execution identity, and causal contract.
- Percentage changes must be paired with absolute provider-token values.
- Treatment installation/configuration is valid experimental treatment; observed invocation count is descriptive, may be zero, and is not an acceptance gate.
- A fixture or verifier defect is attributed to the fixture, not the model. Before production begins, repair the sole v0 contract rather than retaining superseded qualification, protocol, or result records.
- `data/workflow-sessions.json` remains empty until an actual production baseline or treatment completes.

## Current Portfolio

- `fastify-lifecycle-sequence-v0`
- `beets-lifecycle-sequence-v0`
- `terraform-lifecycle-sequence-v0`

Each sequence uses one pinned checkout, one composite start, three sequential prompts, and final-only cumulative verification.

## Evidence Boundary

No baseline, treatment, comparison, or effectiveness finding currently exists. The first production step is one isolated bare baseline replicate per sequence followed by independent correctness and quality review.

## Source References

- ../../../../data/workflow-task-sequences.json
- ../../../../data/repository-fixtures.json
- ../../../../data/workflow-sessions.json
- ../../../../docs/evaluations/workflow-evaluation-runbook.md
- ../../../../docs/evaluations/token-usage-and-quality-standards.md
- ../../../../scripts/generate_workflow_qualification.py
- ../../../../scripts/run_codex_workflow_evaluation.py
- ../../../../scripts/validate_repository.py
