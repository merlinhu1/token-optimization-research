---
status: active
truth_kind: engineering-contract
last_reviewed: 2026-07-02
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
- `scripts/run_codex_fixture_evaluation.py` creates lane-specific Codex homes, isolates agent HOME/PYTHONUSERBASE/XDG/TMPDIR under that Codex home, captures preflight artifacts, runs Codex, extracts provider usage, verifies tasks, and invokes the isolation audit for Codex-based fixture evaluations.
- Non-MCP terminal-binary treatment lanes expose the active binary through lane-specific container mounts and require solve-shell availability checks in addition to runner preflight.
- `scripts/run_codex_evaluation_batch.py` runs planned Codex fixture evaluations, skips already accepted runs by default, and writes a machine-readable batch summary.
- `scripts/extract_codex_usage.py` normalizes Codex JSONL `turn.completed.usage` blocks into `provider-usage.json` records.
- `scripts/audit_tool_isolation.py` audits event streams and preflight artifacts against the active run record's tool manifest.
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
- Codex-based reproduction runs require containerized execution, lane-specific runtime isolation, container/Codex preflight artifacts, full event streams, verifier output, final diff/status, and a passing tool-isolation audit before acceptance.
- Docker preflight may build the evaluation image from the repo Dockerfile, then must smoke-test the image with mounted Codex/tool binaries before model execution.
- Docker-socket execution from a Dockerized Hermes agent must translate nested `docker run` bind sources from the agent-visible `/opt/data` tree at runtime, without recording actual host paths in publishable artifacts unless a record is explicitly marked private.
- Host execution is permitted only as an explicit diagnostic override and must not be reported as container-grade evidence.
- `baseline-codex-no-mcp` is the Codex substrate baseline. It allows Codex native shell/edit/file operations but must use a fresh Codex home with no MCP servers, hooks, global Codex instructions, skills, plugins, or warm indexes copied from the controller environment.
- Baseline run artifacts should use profile-specific manifests and avoid naming treatment tools except in external aggregate comparison records.
- Treatment Codex runs are additive lanes on the same Codex substrate. They may expose only the tools named by the active profile and must use isolated tool data directories unless the protocol explicitly measures warm state.
- Terminal-binary treatment reruns must mount the pinned binary for provenance, mount the same binary into a stable solve-shell path such as `/usr/local/bin/<tool>`, and mount writable run artifact directories when Codex is asked to write final-message artifacts.
- Index-using retrieval tools use cold/optional as the primary full-suite condition unless a protocol says otherwise.
- Warm-index optional variants are calibration conditions; run them on a capped sentinel subset and mark records with `calibration_only: true` so default batches skip them.
- Warm-index preparation is a setup metric. Record wall time, exit code, and output artifacts separately; do not count warmup as provider tokens unless the model sees it through `codex-events.jsonl`.
- Percentage savings must be paired with absolute token and cost values when available.

## Engineering Decisions

- Decision (2026-06-26): Phase 2 emphasizes benchmark-audit readiness before controlled stack reproduction.
- Decision (2026-06-26): Run records should separate provider-billed usage from estimates.
- Decision (2026-06-26): A treatment does not win if it saves tokens by under-solving the task.
- Decision (2026-06-29): Phase 2 profile roles such as comparator, broad-owner, installer, or replacement-runtime lane are not evidence stages; each component still carries `source-logic`, `benchmark-audit`, or `reproduction` status.
- Decision (2026-07-02): Codex-based Phase 2 runs enforce tool isolation through lane-specific `CODEX_HOME` directories and preflight/post-run audits rather than relying on prompt instructions or uninstalling globally installed tools.
- Decision (2026-07-02): Non-MCP terminal-binary lanes require solve-shell PATH verification and stable binary/artifact mounts before full-suite reruns can be accepted.

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
- ../../../../docs/evaluations/tool-isolation-policy.md
- ../../../../scripts/audit_tool_isolation.py
- ../../../../scripts/extract_codex_usage.py
- ../../../../scripts/run_codex_evaluation_batch.py
- ../../../../scripts/run_codex_fixture_evaluation.py
- ../../../../templates/evaluation-record.md
- ../../../../templates/evaluation-task.md
- ../../../../templates/evaluation-run-record.json
- ../../../../prompts/evaluator.md
- ../../../../data/evaluations.json
- ../../../../.agents/skills/benchmark-protocol-writer.md
