# Evaluation framework

## Purpose

This framework defines how token-saving tools and compatibility-safe stacks move from `source-logic` evidence to `benchmark-audit` and then to `reproduction`. It separates operation-level compression from task-level agent behavior and provider-billed cost, because a tool can reduce bytes or estimated tokens at one boundary while increasing turns, tool calls, latency, or provider-billed tokens for the full task.

## Evidence progression

| Stage | Required evidence | Decision use |
|---|---|---|
| `source-logic` | Representative implementation files inspected; runtime transformations, state, fallbacks, and compatibility implications mapped. | Qualified candidate selection and stack design. |
| `benchmark-audit` | Existing harnesses, task definitions, scoring, token accounting, raw outputs, and failure/exclusion semantics inspected. | Evidence-weighted ranking and benchmark design. |
| `reproduction` | Independent runs on target workloads with provider-billed usage, task pass rate, turns, latency, and quality gates. | Deployment-grade recommendation for a defined environment. |

A tool or stack can advance only one stage at a time. Maintainer benchmarks, external pilots, and local reproductions must be labeled separately.

## Evaluation layers

| Layer | Measurement question | Required outputs |
|---|---|---|
| Operation layer | Does a transformation reduce the artifact it directly touches? | raw artifact, transformed artifact, tokenizer counts, reduction ratio, raw fallback path. |
| Fidelity layer | Does the transformed artifact preserve required facts, diagnostics, code structure, schemas, and line references? | task-specific assertions, semantic/factual checks, lost-detail notes. |
| Agent-behavior layer | Does the agent solve the task with fewer turns, fewer tool calls, fewer rereads, or less context churn? | transcript, turn count, tool-call count, retry/correction count, pass/fail verifier. |
| Provider-billing layer | Does the complete task reduce billed tokens or cost after cache effects? | provider usage record with fresh input, cached input, output, reasoning if exposed, cost, model, and pricing basis. |
| Software-quality layer | Does the resulting change remain correct, maintainable, safe, and minimal? | deterministic tests, static checks, diff-size metrics, quality rubric, reviewer notes. |
| Operational layer | Is the profile installable, resettable, and explainable? | install log, generated files, disable/reset path, environment metadata, failure log. |

## Experiment classes

| Class | Purpose | Typical candidates |
|---|---|---|
| Micro artifact benchmark | Isolate one reducer on fixed command output, code snippets, schemas, logs, or repository digests. | RTK, Lowfat, Snip, TokenJuice, xcsift, Headroom transforms. |
| Retrieval benchmark | Compare code/navigation tools on the same questions and edit targets. | Serena, SigMap, CodeGraph, jcodemunch MCP, Claude Context, LeanCTX retrieval. |
| Memory benchmark | Test whether persisted memory reduces rediscovery without stale reinjection. | Cavemem, Claude Mem, MEX, Token Savior memory, LeanCTX memory. |
| Stack pilot | Run a complete coding task with a compatibility-safe stack and baseline. | Lowfat + SigMap + MEX + Ponytail; Snip + Serena + Cavemem; LeanCTX; Token Savior. |
| Replacement-agent benchmark | Compare an alternative runtime against baseline agents without add-on stacks. | ClawCodex, Caveman Code. |
| Installer profile test | Verify that an orchestrator reproduces a selected non-overlapping profile. | Tokless-installed RTK + CodeGraph or other intentionally selected profiles. |

## Controls

Every reproduction run must record:

- repository snapshot and fixture hash;
- fixture scale (`large-project` for primary objective claims);
- task ID and prompt hash;
- baseline and treatment profile IDs from `data/evaluation-profiles.json`;
- objective: `individual_tool_effectiveness` or `stack_effectiveness`;
- agent, model, provider, temperature or deterministic settings when available;
- maximum turns, time budget, and tool permissions;
- enabled token-saving surfaces and explicitly disabled overlapping surfaces;
- raw transcript and transformed artifacts;
- validation commands and exact outputs;
- provider usage source and pricing basis;
- tool manifest and transcript-level tool-isolation audit result;
- run exclusions with reason, not silent deletion.

`data/evaluations.json` is append-only. Use one run record per baseline, individual-tool treatment, stack treatment, replacement-runtime treatment, or audit-only run. Use `experiment_group_id` to tie comparable runs together and `replicate_index` for accumulation.

## Interpretation rules

1. Report operation-level, request-level, session-level, and provider-billed results separately.
2. Treat cache tokens as a first-class billing field, not as ordinary fresh input.
3. Do not claim cost savings from estimated tokenizer counts alone.
4. A run that saves tokens but fails validation is a quality regression, not a successful reduction.
5. A run that saves request tokens but increases correction turns requires task-level downgrade.
6. A stack with overlapping owners is invalid unless overlap is explicitly disabled and verified.
7. One-run pilots are hypothesis tests, not general rankings.
8. Negative findings remain evidence and should be recorded in `data/evaluations.json`.
