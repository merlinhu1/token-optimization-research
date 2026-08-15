# Continuous workflow simulation

## Purpose

Continuous workflow simulation is the primary Phase 2 evidence path for token-optimization claims. It measures weighted token cost across a realistic persistent project session. Monetary cost is out of scope.

The goal is to measure how weighted token cost changes between compatible baseline and treatment sessions. Structured task correctness and optional independent final quality review are recorded as diagnostic outcomes, not eligibility conditions.

## Core rule

Reset before the lane, merge every qualified regression into one composite broken start, and disclose prompts one at a time without controller resets or hidden acceptance gates between prompts.

A valid workflow session preserves these across the ordered task sequence:

- repository source working tree and model-facing Git metadata after one concealed composite broken-start root is created before the lane;
- tool indexes and caches;
- generated profile files;
- agent home and runtime config;
- memory/state stores enabled by the active profile;
- accumulated task artifacts unless the protocol explicitly models cleanup.

The agent must not see future task prompts, controller verifier commands, future task identifiers, or evaluator scoring policy before their prompt is disclosed. Future semantic regression code is intentionally present from lane start. Active Lifecycle V1 injects no acceptance-test assets and presents each current task as a normal software-engineering objective with repository search, related-code inspection, complete implementation, and relevant validation expectations. Historical Baseline V2/V3/V4 prompt and acceptance bytes remain immutable for their executed protocols. Enforce isolation structurally: materialize only the current prompt; keep task fixtures, seed patches, acceptance commands, and verifier scripts in controller-only storage; mount only the persistent target repository plus an isolated output directory into the model runtime; hash verifier assets before execution; and verify those hashes at operational checkpoints. A valid runner starts or resumes the same agent session for every prompt without injecting source changes or running functional gates between prompts, then runs the complete controller verifier suite against the final cumulative repository. Prompt-only metadata such as `future_tasks_visible: false` does not prove isolation by itself.

## Leakage controls

Issue-derived regression fixtures must not expose the answer path as a visible git diff, parent commit, reflog entry, reachable object, or public issue lookup key. Before provider execution, the controller merges every qualified regression against the same fixed snapshot, commits that composite broken state as a parentless root, verifies that the fixed snapshot is inaccessible, and keeps seed patches plus controller reference objects outside the model mount. Use neutral task aliases and sanitize prompts before materializing them one at a time.

Lifecycle V1 uses lenient task-class acceptance inside the controller. Each task seeds an authentic semantic regression from completed upstream behavior and asks the agent to implement the requested feature, refactor, or review correction correctly. Every task must compile; feature and refactor tasks add one narrow essential-behavior smoke, while review tasks remain compile-only. The acceptance commands and final project-wide compile command remain controller-only. Exact-source restoration, broad suites, additional behavioral fidelity, style, and source review are not pass/fail gates, but the agent is not told to disregard them or stop at the minimum gate.

Future semantic regression code may be present from lane start; future prompts, seed patches, acceptance commands, and controller verifier scripts remain controller-only. No acceptance-test assets are materialized. Composite qualification must prove every seed applies, semantic seeds compose cleanly, seeded verifier outcomes are recorded as pass/fail without infrastructure errors, cumulative reverse repairs pass every task verifier, and the fully repaired snapshot passes the project-wide compile command.

## Primary metric

The sole token metric is weighted token cost:

`fresh_input_tokens + 0.1 × cached_input_tokens + 6 × output_tokens`

For Codex exec JSONL, every `turn.completed.usage` record serializes cumulative thread telemetry.
Select the final snapshot for each distinct thread and difference consecutive snapshots for
per-task telemetry. Never sum same-thread snapshots, and fail closed if a counter decreases.

Record fresh input, cached input, cache-write, output, and reasoning only as internal calculation and audit telemetry. Never report a raw-token total or secondary token metric. Do not estimate money.

## Quality constraint

A treatment supports a weighted-token claim when it is bound to a compatible baseline and both executions are operationally complete with valid integrity and provider telemetry. Correctness and quality outcomes are reported alongside the weighted delta rather than used to select samples.

Record one structured verifier outcome for every task, final diff/status, and any optional quality review. Lifecycle V1 acceptance commands and scoring policy remain controller-only, and no acceptance-test assets are injected. Leave `quality_score` null when unreviewed. Failures outside the declared essential smoke, behavioral defects, style findings, and low review scores are diagnostics and remain eligible model-behavior observations; rerun only for experiment invalidity or incomplete execution. Model-facing prompts still require agents to complete the task correctly and validate relevant behavior.

## Workflow session contract

A workflow session binds:

- `session_id`;
- `experiment_group_id`;
- repository fixture and initial snapshot;
- task sequence ID;
- profile ID;
- runtime/model condition;
- state policy;
- per-task results;
- cumulative token usage;
- final software-quality result;
- execution-integrity evidence.

Baseline and treatment sessions are directly comparable only when they use the same repository fixture, initial snapshot, task sequence, runtime, provider, model, model condition, and verifier/acceptance contract.

## Evidence boundaries

| Evidence type | Role |
|---|---|
| `workflow-simulation` | Primary evidence for tool or stack ranking. |
| `workflow-ablation` | Attribution evidence after a full/default profile has workflow evidence. |
| `sanity-check` | Install, profile-isolation, usage-capture, diagnostic-preservation, and runner checks only. |

Sanity checks do not rank tools.

## Artifact layout

Completed workflow-session runs keep a compact evidence bundle instead of a materialized checkout or split task-log tree. New bundles include the structured task-result artifact inside the recoverable evidence bundle and may also expose it during the controller run:

```text
sources/evaluations/workflow-sessions/<session-id>/
  run.json
  changes.diff
  evidence.jsonl.gz
  manifest.sha256
```

`changes.diff` retains ordered cumulative source checkpoints and the final cumulative diff relative to the one parentless composite broken-start root.

`evidence.jsonl.gz` preserves recoverable raw streams such as prompts, Codex events, setup logs, seed-delivery and concealment reports, per-task deltas, verifier output, provider usage extraction, and tool-isolation audit output. Do not commit generated checkouts, virtualenvs, Codex homes, caches, controller Git objects, or split per-task transcript directories.

## Activation sequence

Provider-backed execution requires an active sequence and a frozen protocol. Fastify, Terraform, and Beets satisfy the readiness gate, but fixture qualification and prepare-only validation do not themselves authorize or constitute a paid run.

After one candidate has causally related behavior and passes composite-seed, concealment, verifier-integrity, isolation, and quality preflights:

1. run `baseline-bare-codex` on the full persistent sequence;
2. stop if the baseline fails any frozen gate;
3. run one treatment profile on the same sequence and model condition;
4. compare weighted token cost, structured task outcomes, and final quality;
5. expand only after the record shape, artifacts, and validation remain reliable.

Candidate first treatments:

- LeanCTX as the broad/persistent-context candidate;
- CodeGraph or Serena as narrower retrieval comparators;
- Headroom default Codex integration as a broad compression/proxy candidate.
