# Evaluation framework

## Purpose

This framework defines how token-saving tools and compatibility-safe stacks produce decision evidence. The primary metric is cumulative provider-billed token usage across realistic continuous project workflows. A tool is useful when it reduces cumulative tokens or cost for a persistent work session while preserving task success and final repository quality.

Single-task isolated runs are not primary recommendation evidence. They remain useful as sanity checks for installation, profile isolation, usage capture, diagnostic preservation, and runner correctness.

## Evidence progression

| Stage | Required evidence | Decision use |
|---|---|---|
| `source-logic` | Representative implementation files inspected; runtime transformations, state, fallbacks, and compatibility implications mapped. | Qualified candidate selection and workflow-session design. |
| `benchmark-audit` | Existing harnesses, task definitions, scoring, token accounting, raw outputs, and failure/exclusion semantics inspected. | Background evidence and protocol design. |
| `reproduction` | Independent continuous workflow simulation with provider-billed cumulative token accounting and quality gates. | Deployment-grade recommendation for a defined environment. |

A tool or stack can advance only one stage at a time. Maintainer benchmarks, external pilots, sanity checks, and workflow reproductions must be labeled separately.

## Primary evaluation unit

The canonical objective-bearing unit is a `workflow_session`:

- one repository fixture and initial snapshot;
- one ordered task sequence;
- one baseline or treatment profile;
- one runtime/model condition;
- persistent repository state across tasks;
- persistent tool state, indexes, caches, generated config, and agent home across tasks;
- provider-billed token usage accumulated across the whole sequence.

Baseline and treatment sessions must start from the same initial snapshot and run the same task sequence. Reset happens before the session, not between tasks, unless the task sequence explicitly models a user reset.

## Evaluation layers

| Layer | Measurement question | Required outputs |
|---|---|---|
| Workflow token layer | Does the profile reduce cumulative provider-billed tokens across the session? | fresh input, cached input, cache-write, output, reasoning if exposed, total provider tokens, cost, pricing basis. |
| Workflow behavior layer | Does state persistence reduce rereads, repeated exploration, correction turns, or tool chatter? | per-task transcript, turn count, tool-call count, repeated-read notes, correction count. |
| Software-quality layer | Does the resulting cumulative repo state remain correct, maintainable, safe, and minimal? | per-task verifiers, final verifier, final diff/status, quality rubric, reviewer notes. |
| State-quality layer | Does accumulated state help rather than stale or overfeed context? | tool-state manifest, index/cache/memory changes, stale-context incidents, overfeeding incidents, reset/recovery notes. |
| Operational layer | Is the profile installable, observable, and recoverable across a session? | install log, generated files, disable/reset path, environment metadata, failure log. |
| Sanity layer | Do artifact-level reducers and runner hooks preserve required facts? | raw artifact, transformed artifact, diagnostic assertions, raw fallback path. |

## Experiment classes

| Class | Purpose | Typical candidates | Decision weight |
|---|---|---|---|
| Workflow simulation | Compare baseline and treatment over a persistent multi-task project session. | LeanCTX, CodeGraph, Serena, Headroom, Token Savior, compatibility-safe stacks. | Primary. |
| Workflow ablation | Rerun the same task sequence with one component removed, disabled, or replaced. | Multi-component stacks, broad owners, installer profiles. | Secondary attribution evidence. |
| Sanity check | Verify install, profile isolation, usage capture, diagnostic preservation, raw fallback, or runner behavior. | Terminal compactors, binary lanes, profile manifests, usage extractors. | Not recommendation evidence. |
| Benchmark audit | Inspect existing published or repository-local harnesses and token accounting. | Tools with built-in benchmarks. | Protocol/background evidence. |

## Controls

Every workflow reproduction must record:

- repository fixture ID, initial snapshot, and fixture scale;
- task sequence ID and the ordered task IDs;
- baseline and treatment profile IDs from `data/evaluation-profiles.json`;
- objective: `individual_tool_effectiveness` or `stack_effectiveness`;
- agent runtime, model condition, model, provider, and deterministic settings when available;
- maximum turns, time budget, and tool permissions for the session;
- state policy, including what persists across tasks and what is reset only before the session;
- enabled token-saving surfaces and explicitly disabled overlapping surfaces;
- per-task transcripts, provider usage, verifier output, and diff/status artifacts;
- session-level cumulative provider usage and pricing basis;
- final repository verifier output, final diff/status, and quality review;
- tool manifest and session-level tool-isolation audit result;
- exclusions with reason, not silent deletion.

`data/workflow-sessions.json` is the compact index for workflow simulation records. Raw evidence lives under `sources/evaluations/workflow-sessions/<session-id>/`. Existing `data/evaluations.json` single-run records remain historical and sanity/debug material unless a report explicitly scopes them otherwise.

## Interpretation rules

1. Token usage is the primary metric, measured as cumulative provider-billed workflow usage.
2. Report fresh input, cached input, cache-write, output, reasoning if exposed, total provider tokens, and cost separately.
3. Compare treatments by tokens per accepted workflow and tokens per accepted task, not by isolated one-off task deltas.
4. Do not claim savings from estimated tokenizer counts alone.
5. A workflow that saves tokens but fails task verifiers or final quality gates is a quality regression.
6. A workflow that saves one task but increases later correction turns or stale-context failures requires session-level downgrade.
7. A stack with overlapping owners is invalid unless overlap is explicitly disabled and verified.
8. Single-task isolated runs are sanity checks and do not rank tools.
9. Negative findings remain evidence and should be recorded.
