# Phase 2 benchmark and evaluation plan

## Objective

Phase 2 converts Phase 1 source-logic candidates, including the promoted corrective-audit graph/RAG and memory dossiers, into benchmark-audited and partially reproduced evidence. The goal is to determine which compatibility-safe stacks produce provider-billed savings while preserving software quality on defined task classes, while keeping coverage breadth separate from measured recommendations.

## Inputs from Phase 1

- 42 source-logic tool dossiers: 29 original dossiers plus 13 corrective-audit graph/RAG and memory dossiers promoted on 2026-06-29.
- Compatibility-safe surface model.
- Phase 1 source-logic stack hypothesis portfolio, baselines, broad-owner comparators, installer/orchestrator reproducibility profiles, and replacement-agent lanes.
- Existing benchmark examples in cited repositories, including tokbench, agentic-token-bench, CodeGraph benchmarks, Token Savior tsbench, Caveman Code MicroBench, Ponytail task benchmark, Headroom/Tokbench pilot results, and terminal-output reducer examples.

## Phase 2 tracks

| Track | Output | Promotion target |
|---|---|---|
| Benchmark-audit | Inspect existing harnesses, tasks, scoring, token accounting, raw outputs, and failure semantics. | Promote selected dossiers to `benchmark-audit`. |
| Evaluation harness | Define tasks, fixtures, run records, usage schema, and quality rubric. | Create immediately usable reproduction flows. |
| Stack reproduction | Run baseline and selected treatments on the same tasks with provider-billed accounting. | Promote validated stack evidence toward `reproduction`. |

## Prioritized components for benchmark-audit

| Surface | Components | Audit focus |
|---|---|---|
| Terminal/tool-output compaction | RTK, Lowfat, Snip, TokenJuice, xcsift, Headroom terminal modes | command coverage, raw fallback, failing-output fidelity, operation-to-task translation. |
| Retrieval/context | CodeGraph, Cartog, Graphify, Understand-Anything, Serena, SigMap, jcodemunch MCP, Claude Context, CocoIndex Code, Code Review Graph, CognitX CodeGraph, Codescope, SwarmVault, LeanCTX retrieval, Token Savior retrieval | query quality, freshness, index cost, tool-call overhead, edit-target success, install/reset behavior. |
| Memory/reinjection | Cavemem, Claude Mem, MEX, Total Agent Memory, Dragon-Brain, Memex, Token Savior memory, LeanCTX memory, SwarmVault memory | rediscovery reduction, stale-context rate, project/session scoping, reset path. |
| Broad compression/proxy | Headroom, Claw Compactor, LeanCTX, Token Savior, Codescope, Memex | schema/code fidelity, raw recovery, request versus task billing, turn inflation. |
| Replacement runtime | ClawCodex, Caveman Code | agent loop, routing defaults, memory/compression defaults, benchmark harness validity, baseline parity. |
| Installer/orchestrator | Tokless, Maestro Flow, Grace Marketplace | profile reproducibility, non-overlap enforcement, disable/reset behavior, generated config audit, workflow overhead. |

## Initial stack reproduction portfolio

Run baselines, single-surface owners, and a broader set of source-logic stack hypotheses before narrowing to reproduction candidates.

| Profile ID | Stack/profile | Reason |
|---|---|---|
| `baseline-codex-no-mcp` | Codex CLI substrate with native shell/edit/file operations but no MCP or token-saving add-ons. | Required practical-agent comparator for additive Codex treatment lanes. |
| `lower-intervention-codegraph` | RTK + CodeGraph | Lower-intervention source-logic comparator. |
| `lower-intervention-cartog` | RTK + Cartog | Local graph/RAG comparator against CodeGraph and Graphify. |
| `graphify-retrieval` | Snip + Graphify + optional MEX | Source-logic graph retrieval hypothesis. |
| `understand-anything-retrieval` | Snip + Understand-Anything, then + Cavemem in repeated-task pass | Source-logic onboarding/graph-context hypothesis. |
| `cartog-memory` | Lowfat + Cartog + Total Agent Memory | Current-source graph plus durable memory hypothesis. |
| `sigmap-governance-artifact` | Lowfat + SigMap + MEX + Ponytail | Terminal, retrieval, governance, and artifact-minimization source-logic hypothesis. |
| `serena-cavemem-lightweight` | Snip + Serena + Cavemem | Lightweight hook, language-server retrieval/editing, and compressed-memory source-logic hypothesis. |
| `code-review-graph` | Code Review Graph + Claude Mem + Lowfat | Review/diff-oriented retrieval and repeated-review memory profile. |
| `swarmvault-owner` | SwarmVault alone, then optional Lowfat | Wiki/graph owner hypothesis for documentation-heavy repositories. |
| `codescope-owner` | Codescope alone | Broad code-intelligence owner comparator. |
| `cognitx-dragon-memory` | CognitX CodeGraph + Dragon-Brain | Heavy architecture graph plus durable memory comparator. |
| `broad-context-owner` | LeanCTX alone, then LeanCTX + Ponytail | Single broad owner hypothesis. |
| `integrated-mcp-owner` | Token Savior MCP profile | Single integrated MCP owner hypothesis. |
| `mcp-offload` | pctx + jcodemunch MCP + Caveman | Execution-offload and compact retrieval hypothesis. |
| `broad-compression-owner` | Headroom alone or Claw Compactor alone | Broad compression-owner hypothesis. |
| `apple-build-repair` | xcsift + Serena + MEX | Apple/Xcode workload-specific profile. |
| `replacement-clawcodex` | ClawCodex | Replacement-agent lane. |
| `replacement-caveman-code` | Caveman Code | Replacement-agent lane. |
| `tokless-profile` | Tokless-installed selected non-overlapping profile | Installer reproducibility test, not extra reduction layer. |
| `maestro-orchestrator` | Maestro Flow alone on workflow/state-heavy fixture | Orchestrator/context-budget profile. |
| `grace-artifact-project` | Grace Marketplace on GRACE-governed fixture | Governance/artifact retrieval profile for projects with GRACE markup. |

## Task classes

| Task class | Token-waste target | Minimum verifier |
|---|---|---|
| Noisy test failure repair | Long failing test logs and repeated reruns. | The failing test passes; no unrelated tests regress. |
| Build/typecheck repair | Compiler/typechecker output and code navigation. | Build/typecheck passes. |
| Large-codebase navigation | Avoid broad file reads while locating relevant symbols. | Correct file/function identified and task-specific question answered. |
| Multi-file refactor | Retrieval precision and edit quality. | Tests pass and diff matches required behavior. |
| Memory rediscovery | Reuse project conventions across repeated tasks. | Correct convention applied without re-reading full docs. |
| MCP/tool-heavy workflow | Large intermediate tool traces and offloaded execution. | Final answer or generated artifact passes verifier; intermediate trace stays outside main context. |
| Apple build repair | xcodebuild/SPM output compaction. | Build/test issue is correctly localized; fix passes where environment permits. |
| Replacement-agent coding task | Runtime-level token/cost/quality trade-off. | Same verifier across baseline and replacement agents. |

## Run design

1. Freeze repository fixture and task prompt.
2. Run the Codex no-MCP substrate baseline with usage capture enabled.
3. Run reproduction evidence under the container backend; host runs are diagnostic-only unless explicitly labeled otherwise.
4. Reset repository and tool state.
5. Install or activate exactly one additive treatment profile on the same Codex substrate.
6. For non-MCP terminal-binary treatments, expose the pinned binary only through lane-specific container mounts and verify the actual Codex login shell can resolve it before model execution.
7. For index-backed or stateful tools, use the primary full-suite condition from the active profile, normally cold/optional.
8. Mark warm-state optional variants as `calibration_only: true`; run those on a capped sentinel subset instead of the full suite unless the protocol explicitly promotes warm state to primary.
9. For warm conditions, rebuild the task-local tool state after setup and before Codex starts; record warmup wall time/output separately from provider-token usage.
10. Run the same task with the same model/provider where possible.
11. Capture transcript, usage, tool logs, raw artifacts, transformed artifacts, container preflight, verifier output, and tool-state artifacts where applicable.
12. Mount run artifact directories when the evaluated process writes artifacts such as `codex-last-message.txt`; missing artifact mounts are harness failures, not treatment results.
13. If a rerun batch is killed to fix harness or isolation defects, discard its partial summary and rerun the full planned set from the beginning with `--no-skip-accepted`.
14. Score software quality using the standard rubric.
15. Record result in `data/evaluations.json` and store raw artifacts under `sources/evaluations/<evaluation-id>/`.

## Minimum acceptance criteria for a stack to advance

A stack can be described as Phase 2 positive only if:

- provider-billed task tokens or cost improve versus baseline, or the report explains a non-cost benefit such as quality or latency;
- deterministic verifier passes or quality score is at least 3;
- turn count and tool-call count do not erase the operation-level savings without explanation;
- no overlapping surface owner is active unintentionally;
- install, disable, and reset paths are documented;
- negative or failed runs are retained in the evidence record.

## Immediate first experiments

The first evaluation batch is the concrete multi-fixture suite in `docs/evaluations/phase-2-experiment-suite-v1.md` and `sources/evaluations/phase-2-experiment-suite-v1/`. It replaces any single-fixture pilot as the default next action.

1. Run the 10 Codex no-MCP substrate baselines across the fixture corpus before reporting treatment wins.
2. Run terminal-output treatments on the terminal/build/recorded-Xcode strata before selecting any default terminal owner.
3. Run retrieval treatments with exactly one retrieval authority per run; use cold/optional as the default full-suite condition unless a tool protocol names a different primary condition.
4. Run warm-state optional retrieval calibration only when explicitly requested, with `--include-calibration` and a capped sentinel subset.
5. Run memory ablations on the repeated ledger-convention fixture with explicit state-preserve and state-reset conditions.
6. Run broad-owner and MCP/tool-trace profiles as single owners before composing them with narrow tools.
7. Run installer/orchestrator validation against the profile-isolation fixture and treat generated config/cleanup failures as negative operational evidence.
8. Run ClawCodex and Caveman Code on the replacement-runtime fixture using the same verifier as the Codex no-MCP baseline.
9. Aggregate by stratum; do not publish a default-owner claim from a single fixture or a cold-only retrieval run.
