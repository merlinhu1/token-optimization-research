---
status: active
truth_kind: engineering-contract
last_reviewed: 2026-07-14
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
- `scripts/refresh_workflow_contracts.py` validates immutable qualification evidence, then writes frozen execution protocols. A qualification-contract change must mint a new qualification path and protocol version; historical qualification results, evidence inputs, and protocol files remain unchanged.
- `scripts/run_codex_workflow_evaluation.py` treats missing Codex thread IDs after a successful task as a workflow-continuity failure instead of silently starting later tasks in a fresh thread.
- `scripts/run_codex_workflow_evaluation.py` pre-seeds one qualified composite broken root, materializes prompts one at a time, preserves one warm source/tool/agent state, keeps task fixtures and verifiers outside the model mount, and runs concealed functional verification only after all prompts complete.
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

- Workflow-session records that distinguish provider-reported cumulative workflow token use from estimates and preserve structured correctness and quality evidence. Monetary cost estimation is outside the project objective.


## Contract

- Protocols are written before results.
- Baseline and treatment workflow sessions use the same fixture, task sequence, model, and allowed-tool boundary unless an explicit protocol explains the difference.
- Cumulative provider-reported workflow token use is the primary accounting boundary. The project does not estimate monetary cost.
- Fresh input, cached input, cache-write, output, and reasoning tokens should be recorded when available.
- Estimated tool-result tokens and isolated task totals are secondary evidence.
- Benchmark-audit records require raw outputs or recoverable raw-output paths.
- Reproduction records require independent continuous target-workload workflow simulations.
- Codex-based reproduction runs require containerized execution, lane-specific runtime isolation, provider usage capture, controller-only verifier assets, verifier-integrity evidence, final diff/status, and a passing tool-isolation audit before execution acceptance.
- The final verifier runs every concealed task verifier without short-circuiting, emits one structured outcome per task, and derives `tasks_passed` from structured accepted states. Missing or duplicate outcomes fail closed.
- Completed workflow-session directories publish evidence streams as the compact four-file bundle `run.json`, `changes.diff`, `evidence.jsonl.gz`, and `manifest.sha256`.
- Human runbook tables are generated from machine registries, not maintained as a separate hand-written source of truth.
- Parallel Codex-based batches must use isolated lane checkouts and Codex home roots; shared mutable fixture repos or shared profile Codex homes are not valid parallel reproduction evidence.
- Docker preflight may build the evaluation image from the repo Dockerfile, then must smoke-test the image with mounted Codex/tool binaries before model execution. Frozen protocols and preflight records bind both the Dockerfile hash and immutable Docker image identity from `docker image inspect`: image ID is required, and RepoDigests are recorded when available. Runtime setup re-inspects the tag and rejects tag repoints before provider spend.
- Docker-socket execution from a Dockerized Hermes agent must translate nested `docker run` bind sources from the agent-visible `/opt/data` tree at runtime, without recording actual host paths in publishable artifacts unless a record is explicitly marked private.
- Host execution is permitted only as an explicit diagnostic override and must not be reported as container-grade evidence.
- `baseline-bare-codex` is the Codex substrate baseline. It allows Codex native shell/edit/file operations but must use a fresh Codex home with no MCP servers, hooks, global Codex instructions, skills, plugins, or warm indexes copied from the controller environment.
- Baseline run artifacts should use profile-specific manifests and avoid naming treatment tools except in external aggregate comparison records.
- Treatment Codex workflow sessions are additive lanes on the same Codex substrate. They may expose only the tools named by the active profile and must use isolated tool data directories before the session begins. Treatment protocols bind the resolved executable token, realpath, executable metadata, SHA-256, and bounded deterministic version output; runtime setup rejects unresolved, changed, or mismatched treatment binaries before provider spend.
- Workflow sessions reset repository, tool, profile, and agent state before the session and preserve them between tasks; controller checkpoints do not run hidden functional gates or reset warm state.
- Accepted workflow sessions require a captured Codex thread ID before later tasks can resume the persistent session.
- Session IDs and compact evidence are immutable; later compatible runs use a new replicate/session ID and add evidence rather than replacing prior evidence.
- A reviewed baseline is reusable only within its causal comparison fingerprint and replicate. Comparison identity binds fixture/seed state, prompt and verifier bytes, baseline substrate, agent/model condition, immutable Docker execution identity, and isolation. Full implementation hashes remain frozen provenance, but reporting-, validator-, registry-, or schema-only changes do not split the comparison pool. Guarded causal-identity aliases preserve the active pools while adopting this rule.
- New workflow evidence defaults to Codex CLI `gpt-5.6-luna` at maximum supported `xhigh` reasoning effort (`codex-openai-gpt-5-6-luna-xhigh`). This is a protocol-bound model condition: changing it requires a new baseline pool.
- Fastify, Terraform, and Beets maintenance sequences remain immutable scoped evidence but are retired from the active primary design. The active `beets-lifecycle-sequence-v1` is a compact feature-implementation, behavior-preserving-refactor, and code-review/correction workflow. Its qualification binds task bytes, prompt/seed/verifier bytes, pinned source, individual and composite initial-state failure, cumulative fixed-state success, and concealment evidence.
- New workflow artifact IDs begin with the short profile label, short project lane, and UTC run date, followed by the protocol fingerprint and replicate; the fingerprint, rather than the date-bearing name, determines reuse eligibility.
- The matrix defaults to three concurrent lanes (`--max-parallel 3`). It runs distinct sequence lanes concurrently up to that cap; after a shared baseline is reviewed reusable, repeated `--treatment-profile` arguments run independent profile lanes concurrently; an unreviewed/missing baseline collapses those requests to one baseline-only lane to prevent duplicate spend.
- A comparison is published only after the matching baseline and treatment both have reviewed, objective-accepted records with compact artifacts.
- One replicate means one complete multi-task workflow execution. A valid single replicate is retained as screening evidence; additional compatible runs accumulate evidence as token budget permits.
- Index-using retrieval tools persist their indexes during the workflow session; index preparation is setup metadata, not a separate warm optional condition.
- Percentage savings must be paired with absolute provider-token values.
- Required canonical metrics are intentionally lean: provider token components/total, structured per-task outcomes, independent quality, treatment installation/configuration and isolation, and recoverable artifact integrity. Observed treatment use is optional descriptive telemetry and never an acceptance gate. Money, latency, setup/index timing, broad turn/tool-call telemetry, and manual stale-context observations are not required.

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
- Decision (2026-07-12): Primary token-tool evaluation uses one preseeded composite broken repository, sequential prompts, and persistent warm source/tool/agent state. Hidden controller verification runs once after the complete lane so correctness gates do not truncate or feed back into the measured workflow.
- Decision (2026-07-09): The July 8-9 r0 workflow sessions are excluded from objective use because the old runner exposed the writable run directory; their raw token and execution artifacts remain historical audit evidence.
- Decision (2026-07-12): Active workflows use one shared three-flow contract; new protocols bind GPT-5.6 Luna xhigh. Spark and GPT-5.6 Terra protocols and evidence remain immutable historical contracts.
- Decision (2026-07-14): The grand objective measures cumulative provider token use only; monetary cost estimation is excluded.
- Decision (2026-07-14): All concealed task verifiers run and emit structured per-task outcomes; `tasks_passed` is no longer inferred all-or-zero from one aggregate exit.
- Decision (2026-07-14): Compatible runs accumulate as additional evidence. Framework-only reporting changes do not invalidate or split prior causal comparison pools.
- Decision (2026-07-14): The next practical workflow after consolidation and candidate reduction uses a feature/refactor/code-review lifecycle triad rather than a language matrix.
- Decision (2026-07-15): `beets-lifecycle-sequence-v1` realizes that triad on one pinned Python repository; maintenance sequences are retained but retired from active planning. `retrieval-codegraph` is the sole initial treatment shortlist and all other unexecuted candidates are deferred.

## Rationale

Token-saving tools often move token volume between prompt text, cache reads/writes, output, reasoning, and additional model turns.

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
