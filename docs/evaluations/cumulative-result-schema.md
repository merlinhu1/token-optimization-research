# Cumulative Result Schema

## Purpose

The research program is iterative and token-focused. The repository therefore stores primary evaluation evidence as append-only workflow-session records and keeps raw evidence under `sources/evaluations/workflow-sessions/<session-id>/`.

The primary metric is cumulative provider-billed token usage across a realistic persistent project workflow. Single-run records remain useful for historical results, debugging, instrumentation checks, and sanity gates, but they are not the default basis for recommendations.

## Primary objectives

1. Evaluate individual token-saving tools by cumulative workflow token usage on complex software-engineering sessions.
2. Evaluate compatibility-safe tool stacks by cumulative workflow token usage on the same kind of persistent sessions.

Synthetic micro fixtures and recorded diagnostic fixtures are useful for sanity checks and diagnostic-preservation tests. They do not support primary objective claims by themselves.

## Core entities

| Entity | File | Role |
|---|---|---|
| Repository fixture | `data/repository-fixtures.json` | Defines target repository, scale, setup/reset/verifier, and whether the fixture is calibration or primary-objective material. |
| Workflow task sequence | `data/workflow-task-sequences.json` | Defines the ordered tasks for a persistent session and the reset/state policy for the sequence. |
| Evaluation profile | `data/evaluation-profiles.json` | Standardizes baseline, individual-tool, stack, installer, and comparator profiles. |
| Agent/model condition registry | `data/evaluation-agent-runtimes.json` | Separates evaluated runtime/provider/model settings from tool profiles. |
| Workflow session record | `data/workflow-sessions.json` plus raw session directory | Records one baseline or treatment workflow simulation with cumulative token usage and quality gates. |
| Historical run record | `data/evaluations.json` plus raw run directory | Records prior single-run baselines, treatments, comparisons, and aggregates. |
| JSON schema | `schemas/workflow-session-record.schema.json` | Defines the canonical workflow-session shape for future tooling. |

## Append-only workflow policy

- Add one workflow session record per executed baseline or treatment session.
- Use one reviewed canonical baseline pool per frozen protocol fingerprint and replicate, plus a separate treatment `experiment_group_id` per profile. The fingerprint binds the fixture snapshot, task-prompt and verifier hashes, baseline substrate, agent/model condition, and isolation policy; execution date remains metadata only. Link treatments through comparison records and `interpretation.comparison_baseline_session_id`.
- Bind `agent.runtime_id`, `agent.provider`, `agent.model`, and `agent.model_condition_id` before execution; placeholder model/provider values are allowed only for planned records.
- Keep baseline and treatment workflow sessions on the same task sequence and model condition for direct tool-effect comparisons.
- Use `objective = individual_tool_effectiveness` for one tool or comparator profile.
- Use `objective = stack_effectiveness` for two-or-more-component stack treatments.
- Reset repository/tool/agent state before the session, then preserve state between tasks unless the sequence explicitly models a user reset.
- Supersede records instead of deleting failed, excluded, or negative results.
- Never reuse a session ID or overwrite its compact evidence. Post-hoc integrity review may change objective eligibility only by preserving raw metrics/artifacts and recording the assessment reason and evidence.
- Do not create paired workflow comparisons or aggregate summaries until the referenced workflow session records exist.

## Required workflow metric groups

Each workflow session must record:

1. `cumulative_token_usage` — provider-billed session totals, cache tokens, output/reasoning tokens, pricing basis, and tokens per accepted task.
2. `per_task_results` — task ID, status, provider usage, verifier output, turns, tool calls, correction turns, and notes.
3. `software_quality` — per-task verifier pass/fail, final verifier pass/fail, explicit review status, nullable quality score, critical failures, and final diff/status. Verifier success alone must not synthesize a quality score.
4. `state_observations` — persisted indexes/cache/memory/config, stale-context incidents, repeated rediscovery, overfeeding, and recovery notes.
5. `operational_reproducibility` — install log, pre-session reset verification, raw-artifact recovery, state leakage outside the session boundary, and tool-isolation audit result.

Completed reproduction records must also prove structural sequential disclosure: lazy future-prompt materialization, controller-only task/verifier assets, a model mount limited to the target repository plus isolated output, and passing verifier-integrity hashes. Single-replicate comparisons must record `replicate_count = 1`, null uncertainty, and non-ranking claim status.

## Complex-project policy

Primary objective claims require `fixture_scale = large-project` or `fixture_scale = medium-project`, `evidence_stage = reproduction`, and `evidence_type = workflow-simulation` unless a report explicitly scopes itself to calibration or benchmark-audit evidence.

The retained generated/recorded fixtures are sanity and diagnostic gates. The candidate primary fixtures are public complex projects listed in `data/large-project-candidates.json` and `data/medium-project-candidates.json`; each must be promoted from `candidate-fixture` only after a clean pinned snapshot, frozen task sequence, setup policy, reset policy, and verifier exist.

## Directory convention

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json
  changes.diff
  evidence.jsonl.gz
  manifest.sha256
```

A compact copy of workflow-session metadata is appended to `data/workflow-sessions.json`; recoverable raw evidence remains in the session directory inside `evidence.jsonl.gz`.
