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
| `baseline-native-agent` | Native Claude/Codex-style workflow without token-saving add-ons | Required comparator. |
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
2. Run native baseline with usage capture enabled.
3. Reset repository and tool state.
4. Install or activate one treatment profile.
5. Run the same task with the same model/provider where possible.
6. Capture transcript, usage, tool logs, raw artifacts, transformed artifacts, and verifier output.
7. Score software quality using the standard rubric.
8. Record result in `data/evaluations.json` and store raw artifacts under `sources/evaluations/<evaluation-id>/`.

## Minimum acceptance criteria for a stack to advance

A stack can be described as Phase 2 positive only if:

- provider-billed task tokens or cost improve versus baseline, or the report explains a non-cost benefit such as quality or latency;
- deterministic verifier passes or quality score is at least 3;
- turn count and tool-call count do not erase the operation-level savings without explanation;
- no overlapping surface owner is active unintentionally;
- install, disable, and reset paths are documented;
- negative or failed runs are retained in the evidence record.

## Immediate first experiments

1. Run the first controlled batch: `baseline-native-agent`, `lower-intervention-codegraph`, `lower-intervention-cartog`, `graphify-retrieval`, and `sigmap-governance-artifact` on the same small coding or navigation task.
2. Audit and reproduce one terminal-output compactor on a noisy failing-test fixture before selecting a default terminal owner.
3. Run a retrieval bakeoff on a large-codebase navigation fixture with one fixed terminal owner and exactly one retrieval authority per run.
4. Run repeated-task memory ablations for `cartog-memory`, `serena-cavemem-lightweight`, and `understand-anything-retrieval` with and without memory enabled.
5. Run broad-owner comparators (`broad-context-owner`, `integrated-mcp-owner`, `codescope-owner`, `swarmvault-owner`, `broad-compression-owner`) as single owners before composing them with narrow tools.
6. Run ClawCodex and Caveman Code on a separate replacement-agent fixture using the same verifier.
7. Test Tokless, Maestro Flow, and Grace Marketplace on profiles or fixtures that match their actual orchestration/governance surfaces.
