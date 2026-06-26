# Phase 1 report: compatibility-safe token-saving stacks for AI coding agents

**Date:** 2026-06-26
**Repository:** `token-optimization-research`
**Review status:** draft research report
**Scope:** compatibility-safe token-reduction stacks for AI coding agents, revised after expansion to 27 persistent tool dossiers.

## Executive summary

This report evaluates token-saving stacks for AI coding agents using the updated dossier set. A compatibility-safe stack is one whose components do not compete for the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary. The analysis does not treat repository popularity as a primary stack-selection factor. Reputation is already captured during candidate discovery and dossier prioritization; stack construction therefore emphasizes surface fit, review depth, mechanism diversity, and operational compatibility.

The earlier report over-concentrated on one repeated stack pattern: a terminal-output compactor, a code-retrieval tool, and an artifact-minimization layer, repeated separately for Claude Code and Codex CLI. The revised finding is that a single repeated stack should not be presented as the default across environments. The current dossier set supports several distinct stack archetypes, each suited to a different workload and risk profile.

The primary diversified candidates are:

| Stack candidate | Components | Primary use case | Review posture |
|---|---|---|---|
| Source-grounded balanced add-on stack | `Lowfat + SigMap + MEX + Ponytail` | General coding sessions that need output compaction, targeted code navigation, project-memory discipline, and anti-overbuild guidance | Mostly Level 3 source-behavior evidence, with Ponytail still Level 2 |
| Lightweight hook-and-memory stack | `Snip + Serena + Cavemem` | Existing Claude/Codex-like workflows needing shell-output filtering, code intelligence, and compressed memory without broad proxy ownership | Level 3 dossiers for all three tools |
| Broad context-owner stack | `LeanCTX + Ponytail` | Teams willing to let one broad context layer own retrieval/read/shell/memory surfaces, with a separate artifact-minimization rule layer | LeanCTX Level 3, Ponytail Level 2 |
| Apple build-repair stack | `xcsift + Serena + MEX` | Swift, iOS, macOS, and Xcode-heavy repair work | Level 3 dossiers for all three tools |
| MCP-heavy offload stack | `pctx + jcodemunch MCP + Caveman` | Workloads dominated by multi-step MCP/tool execution where intermediate traces should stay outside the main context | Level 3 dossiers for all three tools |
| Broad compression-owner stack | `Headroom + MEX` | Log, file, RAG, history, or tool-output compression where a single broad compression owner is preferred | Level 3 dossiers for both tools |
| Integrated MCP-owner option | `Token Savior MCP profile` | A single owner for retrieval, memory, and Bash compaction in MCP-compatible agents | Level 2 dossier; promising but not yet source-behavior reviewed in this repository |
| Replacement-agent evaluation lane | `ClawCodex` or Caveman Code-style replacement agents | Cases where replacing the coding agent is acceptable | ClawCodex Level 3; Caveman Code still lacks a dossier |

No stack in this report is deployment-grade. The current evidence is sufficient for research prioritization and compatibility planning, not procurement-grade claims. Benchmark and reproduction review remain required before asserting provider-billed token savings, pass-rate preservation, or total-cost reduction.

## Scope

Included:

- Token-saving tools with persistent dossiers or equivalent repository evidence.
- Analyst-constructed stacks where each component has a distinct surface and a plausible native integration path.
- Single-owner stacks where one integrated tool deliberately combines multiple surfaces.
- Workload-specific stacks, including Apple/Xcode workflows and MCP-heavy offload workflows.

Excluded:

- Duplicate stacks split only by target agent name.
- Loose bundles that require manual discipline rather than native integration or clear surface ownership.
- Multi-tool combinations that double-own retrieval, memory, shell-output compression, broad proxy compression, or execution offload.
- Rankings based primarily on GitHub stars.

## Methodology

The assessment uses repository metadata, discovery artifacts, source-tree records, code-inspection artifacts, and persistent tool dossiers. README files remain useful discovery inputs, but compatibility and stack claims are based on dossier review levels and representative source inspection where available.

Principal sources:

- `data/repositories.json`
- `data/tool-analysis-backlog.json`
- `docs/tool-dossiers/README.md`
- `docs/tool-dossiers/*.md`
- `sources/discovery/2026-06-26-five-more-tool-source-structures.json`
- `sources/discovery/2026-06-26-five-more-tool-code-inspection.json`
- `sources/discovery/2026-06-26-eight-more-tool-source-structures.json`
- `sources/discovery/2026-06-26-eight-more-tool-code-inspection.json`
- `sources/discovery/2026-06-26-ten-more-tool-source-structures.json`
- `sources/discovery/2026-06-26-ten-more-tool-code-inspection.json`

The current dossier set contains 27 tools. Most new stack candidates are based on Level 3 source-behavior dossiers. RTK, CodeGraph, Ponytail, Token Savior, and Context Engine remain Level 2 in this repository and should be treated as provisional for source-behavior claims.

## Evaluation criteria

Stack selection uses the following priorities. Percentages are decision weights for stack construction, not numerical scores already computed for every option.

| Criterion | Definition | Weight |
|---|---|---:|
| Surface compatibility | Components own distinct surfaces and avoid competing hooks, retrieval, memory, compression, proxy, or state boundaries | 30% |
| Review depth and source evidence | Preference for Level 3+ dossiers over README-only or integration-only evidence | 25% |
| Mechanism fit to workload | The stack addresses the specific token-waste pattern: terminal noise, code search, memory rediscovery, broad context, offload, or artifact bloat | 20% |
| Operational simplicity | The stack has fewer fragile install, state, routing, or recovery boundaries | 10% |
| Benchmark readiness | Tests, fixtures, benchmark artifacts, or raw-output recovery paths exist for future Level 4/5 work | 10% |
| Reputation and adoption signal | Stars, forks, and visibility as weak confidence signals after dossier creation | 5% |

The low reputation weight is intentional. Popularity helped identify which tools deserved dossiers. Once dossiers exist, stack construction should primarily use compatibility, evidence quality, and workload fit.

## Surface ownership model

| Surface | Candidate owners | Stack rule |
|---|---|---|
| Terminal/tool-output compaction | RTK, Lowfat, TokenJuice, Snip, xcsift, LeanCTX shell compression, Token Savior Bash compaction | Use one general owner. xcsift can be used as a specialized Xcode owner if general shell compaction is not also filtering xcodebuild output. |
| Code retrieval and indexing | CodeGraph, Serena, SigMap, Claude Context, jcodemunch MCP, CocoIndex Code, Code Review Graph, LeanCTX retrieval, Token Savior retrieval | Use one primary retrieval authority. Multiple retrieval engines may duplicate context and disagree on freshness. |
| Memory and reinjection | Claude Mem, Cavemem, MEX, Token Savior memory, LeanCTX memory | Use one automatic memory/reinjection authority. MEX can be a scaffold/governance layer if it is not also used as automatic reinjection. |
| Broad context compression/proxy | Headroom, Claw Compactor, LeanCTX, TokenTamer/Kompact-style tools | Use one broad compression owner. Do not combine broad compressors without measured fallback behavior. |
| Execution offload/result selection | Context-Mode, pctx, Headroom proxy modes | Use one offload owner. Offload tools can coexist with a retrieval engine only when retrieval and execution boundaries are explicit. |
| Behavioral output style | Caveman, scrooge-mode, concise | Use one behavior/output-style controller. |
| Artifact/code minimization | Ponytail, Bonsai, Whippet | Use one artifact-policy layer. |
| Repository packing/digests | Repomix, Gitingest | Use for one-off handoffs or snapshots, not as a default alongside targeted retrieval unless the task requires full-repo packaging. |
| Replacement agent/runtime | ClawCodex, Caveman Code | Evaluate as alternative runtimes rather than add-ons to an existing hook stack. |

## Qualified stack candidates

### 1. Source-grounded balanced add-on stack

```text
Lowfat + SigMap + MEX + Ponytail
```

**Target workload:** general coding sessions where terminal noise, broad code search, repeated project rediscovery, and overbuilt implementations are all material token drivers.

| Component | Dossier level | Surface | Contribution |
|---|---:|---|---|
| `zdk/lowfat` | 3 | Terminal/tool-output compaction | Filters command output through conditional pipelines, plugin runners, content detection, and raw failure tee logs. |
| `manojmallick/sigmap` | 3 | Code retrieval/signature graph | Exposes MCP tools for context reads, signature search, maps, impact, routing, and session memory. |
| `mex-memory/mex` | 3 | Project-memory scaffold and drift governance | Stores structured context files and checks drift across memory/config surfaces. |
| `DietrichGebert/ponytail` | 2 | Artifact/code minimization | Provides implementation-scope restraint and anti-overbuild guidance. |

**Compatibility assessment:** Lowfat owns terminal-output filtering. SigMap owns retrieval/signature navigation. MEX acts as a project-memory scaffold and drift checker rather than an automatic memory injector in this stack. Ponytail owns artifact/code-minimization policy. These surfaces are distinct if SigMap session memory and MEX scaffold use are configured deliberately and not both used as automatic reinjection authorities.

**Evidence assessment:** Lowfat, SigMap, and MEX have Level 3 source-behavior dossiers. Ponytail remains Level 2, so the artifact-minimization layer is the least mature evidence point. The stack is recommended as a research candidate because it uses mostly source-reviewed tools and covers four different token-waste mechanisms without duplicating owners.

**Caveats:** SigMap includes light session memory, so the stack should avoid turning MEX into a second automatic memory injector. Ponytail should be removed when behavior-rule risk is unacceptable or when implementation completeness is more important than minimality.

### 2. Lightweight hook-and-memory stack

```text
Snip + Serena + Cavemem
```

**Target workload:** existing Claude/Codex-like workflows that need command-output filtering, language-aware code navigation, and compressed cross-session memory, without a broad proxy/compression owner.

| Component | Dossier level | Surface | Contribution |
|---|---:|---|---|
| `edouard-claude/snip` | 3 | Hook-based command-output filtering | Rewrites eligible producer commands through filters while handling shell boundaries, transparent prefixes, unverifiable constructs, and audit logs. |
| `oraios/serena` | 3 | Code retrieval and editing authority | Provides MCP code-retrieval/editing through language-server-style project understanding. |
| `JuliusBrussee/cavemem` | 3 | Compressed memory/reinjection authority | Stores compressed observations, backfills embeddings, and exposes MCP/CLI search and hook context. |

**Compatibility assessment:** Snip owns shell-output filtering. Serena owns code retrieval/editing. Cavemem owns memory/reinjection. These are separate surfaces. The stack should not also enable Claude Mem, Token Savior memory, LeanCTX memory, or another code-retrieval MCP server.

**Evidence assessment:** All three components have Level 3 source-behavior dossiers. The combination is not benchmarked end to end, but it is more evidence-grounded than a reputation-led RTK/CodeGraph default because each selected tool has representative implementation inspection in this repository.

**Caveats:** Snip hook rewriting requires cautious handling of shell syntax and supported filter coverage. Cavemem can duplicate context if another memory system is active. Serena should be the only retrieval authority.

### 3. Broad context-owner stack

```text
LeanCTX + Ponytail
```

**Target workload:** teams willing to let one broad context layer own code search, file reads, shell compression, graph/search tools, and token-saving telemetry, while using a separate artifact-minimization policy.

| Component | Dossier level | Surface | Contribution |
|---|---:|---|---|
| `yvgude/lean-ctx` | 3 | Broad context intelligence layer | Controls what agents read, compresses outputs, exposes many MCP tools, and records token-saving telemetry. |
| `DietrichGebert/ponytail` | 2 | Artifact/code minimization | Reduces unnecessary implementation scope and dependency expansion. |

**Compatibility assessment:** LeanCTX should be treated as the single broad context owner. It should not be paired with another retrieval engine, shell compressor, memory injector, or broad proxy compressor unless that surface is disabled in one tool. Ponytail is a separate artifact-policy layer and can be evaluated independently of LeanCTX's context surfaces.

**Evidence assessment:** LeanCTX has Level 3 source-behavior review. Ponytail remains Level 2 and should be considered provisional. This stack is useful when broad context ownership is acceptable and operational simplicity is preferable to combining several narrower tools.

**Caveats:** LeanCTX's breadth is both its advantage and its compatibility risk. The exact enabled-tool set must be mapped before deployment. Ponytail may be omitted for a lower-behavior-change variant.

### 4. Apple platform build-repair stack

```text
xcsift + Serena + MEX
```

**Target workload:** Swift, iOS, macOS, and Xcode-heavy repair workflows where xcodebuild output is the primary token sink.

| Component | Dossier level | Surface | Contribution |
|---|---:|---|---|
| `ldomaradzki/xcsift` | 3 | Xcode/xcodebuild output parsing | Converts xcodebuild and SPM output into structured build, error, warning, test, timing, coverage, and dependency events. |
| `oraios/serena` | 3 | Code retrieval and editing authority | Provides language-aware navigation and edits without broad repository packing. |
| `mex-memory/mex` | 3 | Project-memory scaffold and drift governance | Keeps project conventions and decisions available without introducing another automatic memory injector. |

**Compatibility assessment:** xcsift is specialized to Apple build output and should own that command family. Serena owns code navigation/editing. MEX owns scaffold/governance. The stack should avoid a second general shell-output compactor on xcodebuild commands unless double-filtering is explicitly disabled.

**Evidence assessment:** All three tools have Level 3 dossiers. This is a workload-specific stack selected for mechanism fit, not popularity. It is more appropriate for Apple projects than a generic terminal compactor plus generic retrieval engine.

**Caveats:** xcsift is domain-specific and consumes complete output in memory according to its parser comments. Rare linker, coverage, and build-system formats require fidelity tests.

### 5. MCP-heavy offload stack

```text
pctx + jcodemunch MCP + Caveman
```

**Target workload:** agent workflows dominated by MCP/tool execution where large intermediate traces, generated TypeScript/bash execution, and retrieval context should be kept compact.

| Component | Dossier level | Surface | Contribution |
|---|---:|---|---|
| `portofcontext/pctx` | 3 | Execution offload/code mode | Provides MCP/code-mode execution with session registries, generated tools, V8 execution, and HTTP/session routes. |
| `jgravelle/jcodemunch-mcp` | 3 | Code retrieval/indexing authority | Provides token-budgeted symbol/context retrieval and compact schema-driven responses. |
| `JuliusBrussee/caveman` | 3 | Behavioral output compression | Reduces assistant prose and related instruction/tool-description overhead. |

**Compatibility assessment:** pctx owns execution/offload. jcodemunch owns retrieval. Caveman owns output style. The combination is compatibility-safe only if pctx is not also used to replace jcodemunch's retrieval authority and if no second behavior controller is installed.

**Evidence assessment:** All three tools have Level 3 dossiers. This stack explores a different mechanism mix than terminal-compactor-plus-retrieval stacks: it emphasizes offloaded execution, compact retrieval, and terse interaction.

**Caveats:** pctx introduces sandbox/runtime trust boundaries and session state. Caveman can reduce visible prose without necessarily reducing total billed tokens if correction turns increase. jcodemunch should be benchmarked against other retrieval authorities on the same tasks.

### 6. Broad compression-owner stack

```text
Headroom + MEX
```

**Target workload:** workflows with large logs, files, RAG chunks, histories, tool outputs, or app/proxy traffic where one broad compressor is preferable to several narrow filters.

| Component | Dossier level | Surface | Contribution |
|---|---:|---|---|
| `chopratejas/headroom` | 3 | Broad compression owner | Routes JSON, code, prose, logs, files, history, tool outputs, and agent/app traffic through specialized compression modes with original-content recovery mechanisms. |
| `mex-memory/mex` | 3 | Project-memory scaffold and drift governance | Keeps durable project context and decisions structured without requiring another compression proxy. |

**Compatibility assessment:** Headroom should own broad compression. MEX can coexist as a scaffold/governance layer if it is not configured as a competing automatic context injector. The stack should not include RTK, Lowfat, Snip, TokenJuice, Claw Compactor, or LeanCTX compression unless one tool's overlapping surface is disabled and tested.

**Evidence assessment:** Both tools have Level 3 dossiers. This stack is appropriate when broad compression is the target and when raw-content recovery is more important than command-specific shell filtering.

**Caveats:** Prior pilot evidence in this repository indicates that request-level compression may not translate to provider-billed savings if more turns are required. End-to-end measurement is mandatory.

### 7. Integrated MCP-owner option

```text
Token Savior MCP profile
```

**Target workload:** MCP-compatible agents where a single integrated owner for retrieval, memory, and Bash compaction is preferred over composing separate tools.

| Internal surface | Contribution |
|---|---|
| Code retrieval/navigation | Reduces broad file reads through structural tools. |
| Memory/reinjection | Reduces repeated rediscovery across sessions. |
| Bash output compaction | Reduces noisy terminal output. |
| Compact MCP profile/manifests | Reduces tool-context overhead. |

**Compatibility assessment:** Token Savior should be treated as a stack owner. It should not be combined with a separate terminal compactor, retrieval engine, or memory injector unless a specific combined deployment has been inspected and tested.

**Evidence assessment:** Token Savior remains Level 2 in this repository. It is retained as an integrated-owner candidate because the surface combination is coherent, not because of popularity.

**Caveats:** Source-behavior inspection of MCP handlers, Bash rewriter, capture hooks, and benchmark data is still required.

### 8. Replacement-agent evaluation lane

```text
ClawCodex
```

and, separately:

```text
Caveman Code
```

**Target workload:** cases where replacing the coding agent is acceptable and token-saving is evaluated as part of the runtime rather than as a plugin stack.

| Candidate | Dossier level | Surface | Assessment |
|---|---:|---|---|
| `agentforce314/clawcodex` | 3 | Replacement AI coding agent/runtime | Source inspection found token estimation, history, prefetch, cost tracking, and compression-pipeline tests. It should be benchmarked as an alternative runtime, not combined with hook-layer stacks. |
| `JuliusBrussee/caveman-code` | 1 in backlog; dossier not yet created | Replacement AI coding agent/runtime | Remains a candidate until a dossier inspects agent loop, output budgets, memory, repository maps, and benchmark harnesses. |

**Compatibility assessment:** Replacement agents are not add-on stacks. They should be compared against existing agent workflows using task-level reproduction, pass rates, billed tokens, latency, and implementation-quality review.

## Legacy and lower-intervention candidates

### RTK + CodeGraph

```text
RTK + CodeGraph
```

This remains a plausible lower-intervention baseline because RTK owns terminal/tool-output compaction and CodeGraph owns retrieval. However, both dossiers are currently Level 2 in this repository. The pair should not be repeated as separate Claude Code and Codex stacks unless the environment-specific integration materially changes the compatibility assessment. It is retained as a baseline for future comparison, not as the default recommendation.

### RTK + CodeGraph + Ponytail

```text
RTK + CodeGraph + Ponytail
```

This remains a plausible artifact-minimization variant of the RTK/CodeGraph baseline, but it should no longer be the only or primary stack archetype. The same three-tool combination should not be duplicated across agent environments. It should be evaluated against the more source-grounded alternatives above, especially `Lowfat + SigMap + MEX + Ponytail` and `Snip + Serena + Cavemem`.

## Non-recommended or excluded combinations

| Combination | Reason for exclusion |
|---|---|
| Multiple general terminal compactors, such as `RTK + Lowfat`, `Lowfat + TokenJuice`, or `Snip + TokenJuice` | They compete for shell/tool-output ownership and can double-filter diagnostics. |
| Multiple retrieval engines, such as `Serena + SigMap`, `CodeGraph + jcodemunch`, or `Claude Context + CocoIndex Code` | They duplicate retrieval authority and may return inconsistent or stale context. |
| Multiple automatic memory systems, such as `Claude Mem + Cavemem` or `Cavemem + Token Savior memory` | They can inject duplicate, stale, or contradictory context. |
| `Headroom + Lowfat`, `Headroom + Snip`, `Headroom + TokenJuice`, or `Headroom + Claw Compactor` | Headroom is a broad compression owner; pairing it with another compressor needs explicit disabled surfaces and benchmarked recovery. |
| `Context-Mode + pctx` | Both own execution offload/result selection. Use one offload owner unless the combination is explicitly documented and tested. |
| `Token Savior + separate retrieval/memory/Bash compaction tools` | Token Savior already combines these surfaces and should be treated as an integrated owner. |
| `ClawCodex + hook-layer token-saving stack` | ClawCodex is a replacement runtime and should be evaluated as an alternative agent rather than as an add-on host. |
| `Repomix` or `Gitingest` as default continuous context tools | Repository packing can increase context use. They are better suited to explicit handoff/snapshot tasks than default retrieval. |
| `Context Engine` as a runtime retrieval stack | The inspected repository contains skills/tool-selection docs and site code, not the runtime MCP implementation. Promote only after locating and inspecting runtime code. |
| `ccusage`, `Splitrail`, `tokentop`, or `abtop` as reduction stacks | Measurement tools are valuable sidecars but do not directly reduce tokens. |

## Selection guidance

| Situation | Recommended research candidate |
|---|---|
| General coding with diverse token waste and mostly Level 3 source evidence | `Lowfat + SigMap + MEX + Ponytail` |
| Existing agent workflow needing lightweight shell filtering, code intelligence, and compressed memory | `Snip + Serena + Cavemem` |
| Preference for a single broad context layer with optional artifact discipline | `LeanCTX + Ponytail` or `LeanCTX` alone for lower behavior risk |
| Swift/iOS/macOS/Xcode-heavy build-repair work | `xcsift + Serena + MEX` |
| MCP-heavy workflows with large intermediate execution traces | `pctx + jcodemunch MCP + Caveman` |
| Broad logs/files/RAG/history compression with raw-content fallback | `Headroom + MEX` |
| Preference for one integrated MCP owner across retrieval, memory, and Bash compaction | `Token Savior MCP profile`, pending Level 3 source-behavior review |
| Minimal baseline for comparison with legacy report | `RTK + CodeGraph` |
| Replacement agent acceptable | `ClawCodex` evaluation lane; Caveman Code after dossier creation |

## Limitations

The current report remains a research artifact rather than a deployment-grade evaluation.

Key limitations:

- No stack in this report has been reproduced end to end with provider-billed token accounting.
- Most Level 3 dossiers inspect representative implementation files, not every runtime path.
- Several historically prominent candidates remain Level 2, including RTK, CodeGraph, Ponytail, Token Savior, and Context Engine.
- Maintainer benchmarks and claims have not been independently reproduced in this repository.
- Prompt-cache effects, turn counts, pass rates, latency, correction loops, and implementation-quality outcomes remain unmeasured.
- Stack interactions involving hooks, MCP servers, memory injection, and offload sessions require environment-specific verification.
- Repository reputation has intentionally low influence in this report; this may underweight ecosystem maturity until Level 4 benchmark review adds operational evidence.

## Next review priorities

1. Promote RTK, CodeGraph, Ponytail, and Token Savior from Level 2 to Level 3 or demote their role in stack recommendations.
2. Run comparative Level 4 benchmark reviews for terminal-output owners: RTK, Lowfat, Snip, TokenJuice, Headroom, and xcsift for Apple workloads.
3. Run comparative retrieval reviews for Serena, SigMap, jcodemunch MCP, Claude Context, CocoIndex Code, Code Review Graph, and LeanCTX.
4. Reproduce at least three end-to-end stack candidates on the same coding tasks with provider-billed token accounting, pass rate, latency, and implementation-quality scoring.
5. Create or update dossiers for remaining replacement-agent candidates before including them in stack rankings.
