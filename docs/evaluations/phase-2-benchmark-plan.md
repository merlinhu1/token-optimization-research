# Phase 2 benchmark and evaluation plan

## Objective

Phase 2 converts source-logic candidates into workflow-simulation evidence. The goal is to determine which compatibility-safe tools and stacks reduce cumulative provider-billed token usage across realistic persistent project sessions while preserving task success and final repository quality.

Single-task isolated runs remain available only as sanity checks for instrumentation, install behavior, isolation, and diagnostic preservation.

## Inputs from Phase 1

- 39 source-logic tool dossiers remain in the current-candidate table after excluding out-of-current-scope research notes.
- Compatibility-safe surface model.
- Phase 1 source-logic stack hypothesis portfolio, baselines, broad-owner comparators, and installer/orchestrator reproducibility profiles.
- Existing benchmark examples in cited repositories, including tokbench, agentic-token-bench, CodeGraph benchmarks, Token Savior tsbench, Caveman behavior-compression benchmarks, Ponytail task benchmark, Headroom/Tokbench pilot results, and terminal-output reducer examples.

## Phase 2 tracks

| Track | Output | Promotion target |
|---|---|---|
| Benchmark-audit | Inspect existing harnesses, tasks, scoring, token accounting, raw outputs, and failure semantics. | Promote selected dossiers to `benchmark-audit`. |
| Workflow harness | Define task sequences, session records, usage schema, quality rubric, and artifact layout. | Create immediately usable workflow-simulation flows. |
| Workflow reproduction | Run baseline and selected treatments on the same persistent task sequence with provider-billed accounting. | Promote validated stack evidence toward `reproduction`. |

## Prioritized components for benchmark-audit

| Surface | Components | Audit focus |
|---|---|---|
| Terminal/tool-output compaction | RTK, Lowfat, Snip, TokenJuice, Headroom terminal modes | command coverage, raw fallback, failing-output fidelity, operation-to-workflow translation. |
| Retrieval/context | CodeGraph, Cartog, Graphify, Understand-Anything, Serena, SigMap, jcodemunch MCP, Claude Context, CocoIndex Code, Code Review Graph, CognitX CodeGraph, Codescope, SwarmVault, LeanCTX retrieval, Token Savior retrieval | query quality, freshness, index cost, tool-call overhead, edit-target success, persistent-session behavior. |
| Memory/reinjection | Cavemem, Claude Mem, MEX, Total Agent Memory, Dragon-Brain, Memex, Token Savior memory, LeanCTX memory, SwarmVault memory | rediscovery reduction across task sequences, stale-context rate, project/session scoping, reset path. |
| Broad compression/proxy | Headroom, Claw Compactor, LeanCTX, Token Savior, Codescope, Memex | schema/code fidelity, raw recovery, workflow-level billing, turn inflation. |
| Installer/orchestrator | Tokless, Maestro Flow, Grace Marketplace | profile reproducibility, non-overlap enforcement, disable/reset behavior, generated config audit, workflow overhead. |

## Initial workflow reproduction portfolio

Run baselines, single-surface owners, and a small set of source-logic hypotheses as full persistent sessions before expanding the matrix.

| Profile ID | Stack/profile | Reason |
|---|---|---|
| `baseline-bare-codex` | Codex CLI substrate with native shell/edit/file operations but no MCP or token-saving add-ons. | Required practical-agent comparator for additive Codex treatment sessions. |
| `retrieval-leanctx` or `broad-context-owner` | LeanCTX retrieval/broad context owner, depending on the intended user setup. | Tests whether broad persistent context reduces cumulative tokens after state can amortize. |
| `retrieval-codegraph` or `lower-intervention-codegraph` | CodeGraph alone, then RTK + CodeGraph if needed. | Lower-intervention source-logic comparator. |
| `retrieval-serena` | Serena only. | Language-server retrieval/editing comparator. |
| `headroom-default-codex` | Default Headroom Codex integration. | Broad compression/proxy candidate; proxy-only ablations are not primary candidate evidence. |
| `integrated-mcp-owner` | Token Savior MCP profile. | Single integrated owner hypothesis. |
| `behavior-caveman` | Caveman. | Behavior/output-compression lane. |
| `tokless-profile` | Tokless-installed selected non-overlapping profile. | Installer reproducibility test, not extra reduction layer. |

## Task classes

| Task class | Token-waste target | Minimum verifier |
|---|---|---|
| Noisy test failure repair | Long failing test logs and repeated reruns across a session. | The failing test passes; no unrelated tests regress. |
| Build/typecheck repair | Compiler/typechecker output and code navigation. | Build/typecheck passes. |
| Large-codebase navigation | Avoid broad file reads while locating relevant symbols across follow-up tasks. | Correct file/function identified and task-specific question answered. |
| Multi-file refactor | Retrieval precision, edit quality, and state reuse across adjacent changes. | Tests pass and diff matches required behavior. |
| Memory rediscovery | Reuse project conventions across repeated tasks. | Correct convention applied without re-reading full docs. |
| MCP/tool-heavy workflow | Large intermediate tool traces and offloaded execution. | Final answer or generated artifact passes verifier; intermediate trace stays outside main context. |

## Workflow run design

1. Freeze repository fixture, initial snapshot, task sequence, and task prompts.
2. Run the baseline workflow session with usage capture enabled.
3. Reset repository, profile home, tool state, indexes, caches, generated config, and agent home before each session.
4. Install or activate exactly one treatment profile on the same agent substrate.
5. Run the ordered task sequence without resetting repository or tool state between tasks.
6. For non-MCP terminal-binary treatments, expose the pinned binary through lane-specific mounts and verify the actual solve shell can resolve it before session execution.
7. Preserve index-backed and stateful tool state naturally across tasks; state reset happens before the session, not between tasks.
8. Record setup/index wall time and output separately; count only what the model sees as provider tokens.
9. Run the same task sequence with the same model/provider where possible.
10. Capture per-task transcript, usage, tool logs, raw artifacts, verifier output, and final diff/status.
11. Capture session-level cumulative provider usage, pricing basis, state observations, and tool-state artifacts.
12. Mount run artifact directories when the evaluated process writes artifacts; missing artifact mounts are harness failures, not treatment results.
13. If a session batch is killed to fix harness or isolation defects, discard its partial summary and rerun the full planned workflow session from the beginning.
14. Score final software quality using the standard rubric.
15. Record result in `data/workflow-sessions.json` and store raw artifacts under `sources/evaluations/workflow-sessions/<session-id>/`.

## Minimum acceptance criteria for a stack to advance

A stack can be described as Phase 2 positive only if:

- cumulative provider-billed workflow tokens or cost improve versus the paired baseline;
- deterministic per-task and final verifiers pass, or the final quality score is at least 3 when no deterministic verifier exists;
- correction turns, repeated reads, tool-call overhead, and stale-context incidents do not erase workflow-level savings;
- no overlapping surface owner is active unintentionally;
- install, disable, and reset paths are documented;
- negative or failed workflow sessions are retained in the evidence record.

## Immediate first experiments

The first objective-bearing batch is a workflow-session pilot, not a single-task matrix.

1. Select one active large-project or medium-project workflow sequence from `data/workflow-task-sequences.json`.
2. Run `baseline-bare-codex` on the full 5-task sequence and record cumulative provider usage.
3. Run one treatment profile on the same sequence and model condition.
4. Compare cumulative tokens, tokens per accepted task, pass rate, correction turns, and final quality.
5. Only after the pilot record shape works, add CodeGraph/Serena/Headroom/LeanCTX comparisons.
6. Use calibration fixtures only for sanity checks and diagnostic-preservation gates.
