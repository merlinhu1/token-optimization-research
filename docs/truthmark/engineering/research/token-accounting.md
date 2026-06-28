---
status: active
truth_kind: engineering-contract
last_reviewed: 2026-07-11
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
- Phase 2 uses continuous workflow simulation as the primary evidence path for token-optimization claims.
- Evaluation templates define task, run-record, and workflow-session artifacts.
- `data/workflow-task-sequences.json` defines ordered persistent task sequences.
- `data/workflow-sessions.json` is the structured workflow-session registry.
- `docs/evaluations/workflow-evaluation-runbook.md` is the maintained human-facing runbook rendered from the workflow sequence and fixture registries.
- `scripts/update_workflow_runbook.py` refreshes that runbook and provides a validator check so operator docs fail closed on registry drift.
- `scripts/run_codex_fixture_evaluation.py` creates lane-specific Codex homes, mounts a pinned Codex package through a dedicated container entrypoint (without exposing the broader host bin directory), captures preflight artifacts, runs Codex, extracts provider usage, verifies tasks, and invokes the isolation audit for Codex-based sanity or historical fixture evaluations.
- `scripts/run_codex_workflow_evaluation.py` loads canonical profile metadata from `data/evaluation-profiles.json` and keeps executable adapter configuration separate.
- `scripts/generate_workflow_qualification.py` produces deterministic workflow qualification evidence from a clean pinned checkout before paid runs.
- `scripts/refresh_workflow_contracts.py` validates immutable qualification evidence, then refreshes frozen execution protocols; it never rewrites qualification results.
- `scripts/run_codex_workflow_evaluation.py` treats missing Codex thread IDs after a successful task as a workflow-continuity failure instead of silently starting later tasks in a fresh thread.
- `scripts/run_codex_workflow_evaluation.py` materializes prompts one task at a time, keeps task fixtures and verifiers outside the model mount, and verifies acceptance-asset hashes before running controller verifiers.
- Non-MCP terminal-binary treatment lanes expose the active binary through lane-specific container mounts and require solve-shell availability checks in addition to runner preflight.
- `scripts/extract_codex_usage.py` normalizes Codex JSONL `turn.completed.usage` blocks into `provider-usage.json` records.
- `scripts/audit_tool_isolation.py` audits event streams and preflight artifacts against the active run record's tool manifest.
- `data/evaluations.json` is the structured evaluation registry.

## Product Truth Links

- None. This is an engineering research contract, not product truth.

## Contract Surface

- Benchmark protocols, workflow-session records, run-record schema, workflow-session schema, and token-usage reporting boundaries.

## Inputs

- Task fixtures, prompts, models, allowed tools, provider usage records, raw outputs, and verifier output.

## Outputs

- Workflow-session records that distinguish provider-billed cumulative workflow usage from estimates and preserve quality evidence.


## Contract

- Protocols are written before results.
- Baseline and treatment workflow sessions use the same fixture, task sequence, model, and allowed-tool boundary unless an explicit protocol explains the difference.
- Cumulative provider-billed workflow usage is the primary token-accounting boundary.
- Fresh input, cached input, cache-write, output, and reasoning tokens should be recorded when available.
- Estimated tool-result tokens and isolated task totals are secondary evidence.
- Benchmark-audit records require raw outputs or recoverable raw-output paths.
- Reproduction records require independent continuous target-workload workflow simulations.
- Codex-based reproduction runs require containerized execution, lane-specific runtime isolation, provider-billed usage capture, controller-only verifier assets, verifier-integrity evidence, final diff/status, and a passing tool-isolation audit before execution acceptance.
- Completed workflow-session directories publish evidence streams as the compact four-file bundle `run.json`, `changes.diff`, `evidence.jsonl.gz`, and `manifest.sha256`.
- Human runbook tables are generated from machine registries, not maintained as a separate hand-written source of truth.
- Parallel Codex-based batches must use isolated lane checkouts and Codex home roots; shared mutable fixture repos or shared profile Codex homes are not valid parallel reproduction evidence.
- Docker preflight may build the evaluation image from the repo Dockerfile, then must smoke-test the image with mounted Codex/tool binaries before model execution. Frozen protocols and preflight records bind both the Dockerfile hash and immutable Docker image identity from `docker image inspect`: image ID is required, and RepoDigests are recorded when available. Runtime setup re-inspects the tag and rejects tag repoints before provider spend.
- Docker-socket execution from a Dockerized Hermes agent must translate nested `docker run` bind sources from the agent-visible `/opt/data` tree at runtime, without recording actual host paths in publishable artifacts unless a record is explicitly marked private.
- Host execution is permitted only as an explicit diagnostic override and must not be reported as container-grade evidence.
- `baseline-bare-codex` is the Codex substrate baseline. It allows Codex native shell/edit/file operations but must use a fresh Codex home with no MCP servers, hooks, global Codex instructions, skills, plugins, or warm indexes copied from the controller environment.
- Baseline run artifacts should use profile-specific manifests and avoid naming treatment tools except in external aggregate comparison records.
- Treatment Codex workflow sessions are additive lanes on the same Codex substrate. They may expose only the tools named by the active profile and must use isolated tool data directories before the session begins. Treatment protocols bind the resolved executable token, realpath, executable metadata, SHA-256, and bounded deterministic version output; runtime setup rejects unresolved, changed, or mismatched treatment binaries before provider spend.
- Workflow sessions reset repository, tool, profile, and agent state before the session and preserve them between tasks unless the sequence explicitly models a user reset.
- Accepted workflow sessions require a captured Codex thread ID before later tasks can resume the persistent session.
- Session IDs and compact evidence are immutable; reruns use a new replicate/session ID instead of replacing prior evidence.
- A reviewed baseline is reusable only within its frozen protocol fingerprint and replicate. That fingerprint binds the fixture snapshot, prompt and verifier bytes, baseline substrate, agent/model condition, immutable Docker execution identity, and isolation policy; the execution date is metadata, not a baseline cache key.
- New workflow evidence defaults to Codex CLI `gpt-5.3-codex-spark` at `medium` reasoning effort (`codex-openai-gpt-5-3-codex-spark-medium`). This is a protocol-bound model condition: changing it requires a new baseline pool.
- Fastify, Terraform, and Beets are the three active production-qualified flows; each has exactly five tasks. Qualification must bind controller task-directory bytes as well as prompt, seed, verifier, pinned source, ordered transition, and concealed-test evidence. Historical sessions with a different fixture fingerprint remain preserved but are ineligible for reuse or comparison.
- New workflow artifact IDs begin with the short profile label, short project lane, and UTC run date, followed by the protocol fingerprint and replicate; the fingerprint, rather than the date-bearing name, determines reuse eligibility.
- The matrix defaults to three concurrent lanes (`--max-parallel 3`). It runs distinct sequence lanes concurrently up to that cap; after a shared baseline is reviewed reusable, repeated `--treatment-profile` arguments run independent profile lanes concurrently; an unreviewed/missing baseline collapses those requests to one baseline-only lane to prevent duplicate spend.
- A comparison is published only after the matching baseline and treatment both have reviewed, objective-accepted records with compact artifacts.
- Single-replicate comparisons are screening observations with null uncertainty and are not ranking evidence.
- Index-using retrieval tools persist their indexes during the workflow session; index preparation is setup metadata, not a separate warm optional condition.
- Percentage savings must be paired with absolute token and cost values when available.

## Engineering Decisions

- Decision (2026-06-26): Phase 2 emphasizes benchmark-audit readiness before controlled stack reproduction.
- Decision (2026-06-26): Run records should separate provider-billed usage from estimates.
- Decision (2026-06-26): A treatment does not win if it saves tokens by under-solving the task.
- Decision (2026-06-29): Phase 2 profile roles such as comparator, broad-owner, installer, or replacement-runtime lane are not evidence stages; each component still carries `source-logic`, `benchmark-audit`, or `reproduction` status.
- Decision (2026-07-02): Codex-based Phase 2 runs enforce tool isolation through lane-specific `CODEX_HOME` directories and preflight/post-run audits rather than relying on prompt instructions or uninstalling globally installed tools.
- Decision (2026-07-02): Non-MCP terminal-binary lanes require solve-shell PATH verification and stable binary/artifact mounts before full-suite reruns can be accepted.
- Decision (2026-07-03): Parallel Codex batch execution uses rsync-materialized lane roots by default so dirty or untracked evaluation setup is snapshotted without sharing mutable fixture checkouts.
- Decision (2026-07-07): Continuous workflow simulation is the primary Phase 2 evidence path; cumulative provider-billed workflow usage is the primary metric, and isolated task runs are sanity/debug evidence only.
- Decision (2026-07-08): Completed workflow-session runs keep a compact four-file evidence bundle instead of committing materialized checkouts, virtualenvs, Codex homes, or split per-task logs.
- Decision (2026-07-08): The human-facing workflow-evaluation runbook is maintained by rendering active registry data and validating the rendered file, rather than by hand-maintaining a parallel Phase 2 suite folder.
- Decision (2026-07-08): Workflow evaluation supports multiple single-tool Codex treatment profiles, and missing persistent Codex thread IDs are acceptance failures.
- Decision (2026-07-09): Sequential disclosure is enforced by model mount boundaries, lazy prompt materialization, and verifier hashes rather than trusted metadata or prompt instructions.
- Decision (2026-07-09): The July 8-9 r0 workflow sessions are excluded from objective use because the old runner exposed the writable run directory; their raw token and execution artifacts remain historical audit evidence.
- Decision (2026-07-11): Active workflows use one shared four-flow contract and frozen GPT-5.6 Terra-medium baseline protocol/preflight identity; GPT-5.5 is historical-inactive metadata only.

## Rationale

Token-saving tools often move cost between prompt text, tool calls, cache writes, output, and reasoning.

The repo needs accounting boundaries that expose those tradeoffs.

## Non-Goals

- This doc does not store benchmark results.
- This doc does not select the winning stack.
- This doc does not replace per-run artifacts under evaluation sources.

## Maintenance Notes

- Update this doc when `templates/workflow-session-record.json` changes schema.
- Update this doc when the Phase 2 benchmark plan changes required metrics.
- Keep workflow protocol wording aligned with the repo-local `benchmark-protocol-writer` skill.
- Regenerate `docs/evaluations/workflow-evaluation-runbook.md` after active sequence or fixture registry changes.

## Source References

- ../../../../docs/evaluations/evaluation-framework.md
- ../../../../docs/evaluations/phase-2-benchmark-plan.md
- ../../../../docs/evaluations/token-usage-and-quality-standards.md
- ../../../../docs/evaluations/continuous-workflow-simulation.md
- ../../../../docs/evaluations/workflow-evaluation-runbook.md
- ../../../../docs/evaluations/tool-isolation-policy.md
- ../../../../scripts/audit_tool_isolation.py
- ../../../../scripts/extract_codex_usage.py
- ../../../../scripts/update_workflow_runbook.py
- ../../../../scripts/run_codex_fixture_evaluation.py
- ../../../../templates/evaluation-record.md
- ../../../../templates/evaluation-task.md
- ../../../../templates/evaluation-run-record.json
- ../../../../templates/workflow-session-record.json
- ../../../../schemas/workflow-session-record.schema.json
- ../../../../data/workflow-task-sequences.json
- ../../../../data/workflow-sessions.json
- ../../../../prompts/evaluator.md
- ../../../../data/evaluations.json
- ../../../../.agents/skills/benchmark-protocol-writer.md
