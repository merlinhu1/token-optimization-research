# Phase 1 report: compatibility-safe token-saving stacks for AI coding agents

**Date:** 2026-06-26
**Repository:** `token-optimization-research`
**Review status:** draft research report
**Scope:** compatibility-safe token-reduction stacks for AI coding agents, revised after expansion to 29 persistent source-logic tool dossiers.

## Executive summary

This report evaluates token-saving stacks for AI coding agents using the updated 29-dossier source-logic set. A compatibility-safe stack is one whose components do not compete for the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary. The analysis does not treat repository popularity as a primary stack-selection factor. Reputation is already captured during candidate discovery and dossier prioritization; stack construction therefore emphasizes surface fit, review depth, mechanism diversity, and operational compatibility.

The earlier report over-concentrated on one repeated stack pattern: a terminal-output compactor, a code-retrieval tool, and an artifact-minimization layer, repeated separately for Claude Code and Codex CLI. The revised finding is that a single repeated stack should not be presented as the default across environments. The current dossier set supports several distinct stack archetypes, each suited to a different workload and risk profile.

The primary diversified candidates are:

| Stack candidate | Components | Primary use case | Review posture |
|---|---|---|---|
| Source-grounded balanced add-on stack | `Lowfat + SigMap + MEX + Ponytail` | General coding sessions that need output compaction, targeted code navigation, project-memory discipline, and anti-overbuild guidance | source-logic dossiers for all components |
| Lightweight hook-and-memory stack | `Snip + Serena + Cavemem` | Existing Claude/Codex-like workflows needing shell-output filtering, code intelligence, and compressed memory without broad proxy ownership | source-logic dossiers for all three tools |
| Broad context-owner stack | `LeanCTX + Ponytail` | Teams willing to let one broad context layer own retrieval/read/shell/memory surfaces, with a separate artifact-minimization rule layer | source-logic dossiers for both components |
| Apple build-repair stack | `xcsift + Serena + MEX` | Swift, iOS, macOS, and Xcode-heavy repair work | source-logic dossiers for all three tools |
| MCP-heavy offload stack | `pctx + jcodemunch MCP + Caveman` | Workloads dominated by multi-step MCP/tool execution where intermediate traces should stay outside the main context | source-logic dossiers for all three tools |
| Broad compression-owner stack | `Headroom + MEX` | Log, file, RAG, history, or tool-output compression where a single broad compression owner is preferred | source-logic dossiers for both tools |
| Integrated MCP-owner option | `Token Savior MCP profile` | A single owner for retrieval, memory, and Bash compaction in MCP-compatible agents | source-logic dossier |
| Replacement-agent evaluation lane | `ClawCodex` or `Caveman Code` replacement agents | Cases where replacing the coding agent is acceptable | source-logic dossiers for both replacement-agent candidates |

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

The assessment uses repository metadata, persistent tool dossiers, source-tree review, representative source-code logic inspection, and compatibility-surface analysis. README files and integration paths remain useful discovery inputs, but compatibility and stack claims are based on source-logic dossier evidence rather than README or integration claims alone.

Principal evidence basis:

- **Repository catalog and backlog:** normalized repository metadata, discovery status, dossier coverage, and evidence-stage tracking across the token-saving candidate set.
- **Persistent tool dossiers:** 29 per-tool dossiers summarizing identity, integration surfaces, implementation behavior, compatibility notes, limits, and next review tasks.
- **Source-structure review:** batch-level source-tree and integration-path inspection used to locate installers, hooks, plugins, MCP servers, indexes, tests, benchmarks, and runtime entry points.
- **Source-logic inspection:** representative implementation files read for recommended and retained candidates, with raw provenance retained separately for audit but summarized through the dossiers in this report.
- **Compatibility model:** surface-ownership analysis across terminal compaction, retrieval, memory, broad compression, execution offload, behavior control, artifact policy, repository packing, installer/orchestrator layers, and replacement runtimes.

Detailed provenance ledgers are retained in the repository for reproducibility and audit, while the report cites their summarized conclusions through the dossier set and evidence-basis categories above.

The current dossier set contains 29 tools, and the backlog has no lead-only entries. All tools used in recommended stack candidates have source-logic dossiers in this repository. Context Engine also has a source-logic dossier, but the inspected repository contains skills/static-site code rather than runtime MCP implementation, so it remains excluded from runtime stack recommendations. Tokless also has a source-logic dossier and passing Go tests for its inspected repository, but it is classified as an installer/orchestrator rather than an independent reduction runtime.

## Evaluation criteria

Stack selection uses the following priorities. Percentages are decision weights for stack construction, not numerical scores already computed for every option.

| Criterion | Definition | Weight |
|---|---|---:|
| Surface compatibility | Components own distinct surfaces and avoid competing hooks, retrieval, memory, compression, proxy, or state boundaries | 30% |
| Review depth and source evidence | Preference for source-logic dossiers over discovery-only or integration-only evidence | 25% |
| Mechanism fit to workload | The stack addresses the specific token-waste pattern: terminal noise, code search, memory rediscovery, broad context, offload, or artifact bloat | 20% |
| Operational simplicity | The stack has fewer fragile install, state, routing, or recovery boundaries | 10% |
| Benchmark readiness | Tests, fixtures, benchmark artifacts, or raw-output recovery paths exist for future benchmark-audit/reproduction work | 10% |
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

| Component | Evidence stage | Surface | Contribution |
|---|---|---|---|
| `zdk/lowfat` | source-logic | Terminal/tool-output compaction | Filters command output through conditional pipelines, plugin runners, content detection, and raw failure tee logs. |
| `manojmallick/sigmap` | source-logic | Code retrieval/signature graph | Exposes MCP tools for context reads, signature search, maps, impact, routing, and session memory. |
| `mex-memory/mex` | source-logic | Project-memory scaffold and drift governance | Stores structured context files and checks drift across memory/config surfaces. |
| `DietrichGebert/ponytail` | source-logic | Artifact/code minimization | Provides implementation-scope restraint and anti-overbuild guidance. |

**Compatibility assessment:** Lowfat owns terminal-output filtering. SigMap owns retrieval/signature navigation. MEX acts as a project-memory scaffold and drift checker rather than an automatic memory injector in this stack. Ponytail owns artifact/code-minimization policy. These surfaces are distinct if SigMap session memory and MEX scaffold use are configured deliberately and not both used as automatic reinjection authorities.

**Evidence assessment:** Lowfat, SigMap, MEX, and Ponytail all have source-logic dossiers. The stack is recommended as a research candidate because it covers four different token-waste mechanisms without duplicating owners.

**Caveats:** SigMap includes light session memory, so the stack should avoid turning MEX into a second automatic memory injector. Ponytail should be removed when behavior-rule risk is unacceptable or when implementation completeness is more important than minimality.

### 2. Lightweight hook-and-memory stack

```text
Snip + Serena + Cavemem
```

**Target workload:** existing Claude/Codex-like workflows that need command-output filtering, language-aware code navigation, and compressed cross-session memory, without a broad proxy/compression owner.

| Component | Evidence stage | Surface | Contribution |
|---|---|---|---|
| `edouard-claude/snip` | source-logic | Hook-based command-output filtering | Rewrites eligible producer commands through filters while handling shell boundaries, transparent prefixes, unverifiable constructs, and audit logs. |
| `oraios/serena` | source-logic | Code retrieval and editing authority | Provides MCP code-retrieval/editing through language-server-style project understanding. |
| `JuliusBrussee/cavemem` | source-logic | Compressed memory/reinjection authority | Stores compressed observations, backfills embeddings, and exposes MCP/CLI search and hook context. |

**Compatibility assessment:** Snip owns shell-output filtering. Serena owns code retrieval/editing. Cavemem owns memory/reinjection. These are separate surfaces. The stack should not also enable Claude Mem, Token Savior memory, LeanCTX memory, or another code-retrieval MCP server.

**Evidence assessment:** All three components have source-logic dossiers. The combination is not benchmarked end to end, but it is more evidence-grounded than a reputation-led RTK/CodeGraph default because each selected tool has representative implementation inspection in this repository.

**Caveats:** Snip hook rewriting requires cautious handling of shell syntax and supported filter coverage. Cavemem can duplicate context if another memory system is active. Serena should be the only retrieval authority.

### 3. Broad context-owner stack

```text
LeanCTX + Ponytail
```

**Target workload:** teams willing to let one broad context layer own code search, file reads, shell compression, graph/search tools, and token-saving telemetry, while using a separate artifact-minimization policy.

| Component | Evidence stage | Surface | Contribution |
|---|---|---|---|
| `yvgude/lean-ctx` | source-logic | Broad context intelligence layer | Controls what agents read, compresses outputs, exposes many MCP tools, and records token-saving telemetry. |
| `DietrichGebert/ponytail` | source-logic | Artifact/code minimization | Reduces unnecessary implementation scope and dependency expansion. |

**Compatibility assessment:** LeanCTX should be treated as the single broad context owner. It should not be paired with another retrieval engine, shell compressor, memory injector, or broad proxy compressor unless that surface is disabled in one tool. Ponytail is a separate artifact-policy layer and can be evaluated independently of LeanCTX's context surfaces.

**Evidence assessment:** LeanCTX and Ponytail both have source-logic dossiers. This stack is useful when broad context ownership is acceptable and operational simplicity is preferable to combining several narrower tools.

**Caveats:** LeanCTX's breadth is both its advantage and its compatibility risk. The exact enabled-tool set must be mapped before deployment. Ponytail may be omitted for a lower-behavior-change variant.

### 4. Apple platform build-repair stack

```text
xcsift + Serena + MEX
```

**Target workload:** Swift, iOS, macOS, and Xcode-heavy repair workflows where xcodebuild output is the primary token sink.

| Component | Evidence stage | Surface | Contribution |
|---|---|---|---|
| `ldomaradzki/xcsift` | source-logic | Xcode/xcodebuild output parsing | Converts xcodebuild and SPM output into structured build, error, warning, test, timing, coverage, and dependency events. |
| `oraios/serena` | source-logic | Code retrieval and editing authority | Provides language-aware navigation and edits without broad repository packing. |
| `mex-memory/mex` | source-logic | Project-memory scaffold and drift governance | Keeps project conventions and decisions available without introducing another automatic memory injector. |

**Compatibility assessment:** xcsift is specialized to Apple build output and should own that command family. Serena owns code navigation/editing. MEX owns scaffold/governance. The stack should avoid a second general shell-output compactor on xcodebuild commands unless double-filtering is explicitly disabled.

**Evidence assessment:** All three tools have source-logic dossiers. This is a workload-specific stack selected for mechanism fit, not popularity. It is more appropriate for Apple projects than a generic terminal compactor plus generic retrieval engine.

**Caveats:** xcsift is domain-specific and consumes complete output in memory according to its parser comments. Rare linker, coverage, and build-system formats require fidelity tests.

### 5. MCP-heavy offload stack

```text
pctx + jcodemunch MCP + Caveman
```

**Target workload:** agent workflows dominated by MCP/tool execution where large intermediate traces, generated TypeScript/bash execution, and retrieval context should be kept compact.

| Component | Evidence stage | Surface | Contribution |
|---|---|---|---|
| `portofcontext/pctx` | source-logic | Execution offload/code mode | Provides MCP/code-mode execution with session registries, generated tools, V8 execution, and HTTP/session routes. |
| `jgravelle/jcodemunch-mcp` | source-logic | Code retrieval/indexing authority | Provides token-budgeted symbol/context retrieval and compact schema-driven responses. |
| `JuliusBrussee/caveman` | source-logic | Behavioral output compression | Reduces assistant prose and related instruction/tool-description overhead. |

**Compatibility assessment:** pctx owns execution/offload. jcodemunch owns retrieval. Caveman owns output style. The combination is compatibility-safe only if pctx is not also used to replace jcodemunch's retrieval authority and if no second behavior controller is installed.

**Evidence assessment:** All three tools have source-logic dossiers. This stack explores a different mechanism mix than terminal-compactor-plus-retrieval stacks: it emphasizes offloaded execution, compact retrieval, and terse interaction.

**Caveats:** pctx introduces sandbox/runtime trust boundaries and session state. Caveman can reduce visible prose without necessarily reducing total billed tokens if correction turns increase. jcodemunch should be benchmarked against other retrieval authorities on the same tasks.

### 6. Broad compression-owner stack

```text
Headroom + MEX
```

**Target workload:** workflows with large logs, files, RAG chunks, histories, tool outputs, or app/proxy traffic where one broad compressor is preferable to several narrow filters.

| Component | Evidence stage | Surface | Contribution |
|---|---|---|---|
| `chopratejas/headroom` | source-logic | Broad compression owner | Routes JSON, code, prose, logs, files, history, tool outputs, and agent/app traffic through specialized compression modes with original-content recovery mechanisms. |
| `mex-memory/mex` | source-logic | Project-memory scaffold and drift governance | Keeps durable project context and decisions structured without requiring another compression proxy. |

**Compatibility assessment:** Headroom should own broad compression. MEX can coexist as a scaffold/governance layer if it is not configured as a competing automatic context injector. The stack should not include RTK, Lowfat, Snip, TokenJuice, Claw Compactor, or LeanCTX compression unless one tool's overlapping surface is disabled and tested.

**Evidence assessment:** Both tools have source-logic dossiers. This stack is appropriate when broad compression is the target and when raw-content recovery is more important than command-specific shell filtering.

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

**Evidence assessment:** Token Savior now has a source-logic dossier covering representative MCP server, tool schema, compact operation, Bash rewrite, memory DB, query API, project indexer, and tests. It is retained as an integrated-owner candidate because the surface combination is coherent, not because of popularity.

**Caveats:** benchmark-audit review remains required for MCP handler coverage, Bash rewrite effectiveness, capture hooks, benchmark data, and provider-billed end-to-end savings.

### 8. Replacement-agent evaluation lane

```text
ClawCodex / Caveman Code
```

**Target workload:** cases where replacing the coding agent is acceptable and token-saving is evaluated as part of the runtime rather than as a plugin stack.

| Candidate | Evidence stage | Surface | Assessment |
|---|---|---|---|
| `agentforce314/clawcodex` | source-logic | Replacement AI coding agent/runtime | Source inspection found token estimation, history, prefetch, cost tracking, and compression-pipeline tests. It should be benchmarked as an alternative runtime, not combined with hook-layer stacks. |
| `JuliusBrussee/caveman-code` | source-logic | Replacement AI coding agent/runtime | Source inspection found a real agent loop, role/model routing, proxy streaming, cost caps, compression fallback, cavemem memory integration, repository-map construction, token verification, and microbench runners. |

**Compatibility assessment:** Replacement agents are not add-on stacks. ClawCodex and Caveman Code should be compared against each other and against existing Claude/Codex-style workflows using task-level reproduction, pass rates, billed tokens, latency, and implementation-quality review. They should not be combined with hook-layer token-saving stacks unless overlapping runtime surfaces are explicitly disabled and tested.

## Installer/orchestrator evidence

### Tokless

Tokless is retained as operational infrastructure rather than a reduction component. Source inspection found a Go registry and installer/wiring layer for RTK, CodeGraph, Context-Mode, Caveman, and supported agents. It installs tools, writes MCP entries, hooks, plugin references, permissions, indexes, and cleanup paths. It does not provide an independent token-saving mechanism separate from the tools it installs.

Tokless is useful for reproducing selected non-overlapping profiles once a stack has been chosen. It should not be counted as an additional layer in stack scoring. The inspected Tokless clone passed its Go test suite in this environment, covering internal agents, commands, core registry, tools, and utilities.

## Legacy and lower-intervention candidates

### RTK + CodeGraph

```text
RTK + CodeGraph
```

This remains a plausible lower-intervention baseline because RTK owns terminal/tool-output compaction and CodeGraph owns retrieval. Both now have source-logic dossiers. The pair should not be repeated as separate Claude Code and Codex stacks unless the environment-specific integration materially changes the compatibility assessment. It is retained as a baseline for future comparison, not as the default recommendation.

### RTK + CodeGraph + Ponytail

```text
RTK + CodeGraph + Ponytail
```

This remains a plausible artifact-minimization variant of the RTK/CodeGraph baseline, and RTK, CodeGraph, and Ponytail now all have source-logic dossiers. It should no longer be the only or primary stack archetype, and the same three-tool combination should not be duplicated across agent environments. It should be evaluated against the alternatives above, especially `Lowfat + SigMap + MEX + Ponytail` and `Snip + Serena + Cavemem`.

## Non-recommended or excluded combinations

| Combination | Reason for exclusion |
|---|---|
| Multiple general terminal compactors, such as `RTK + Lowfat`, `Lowfat + TokenJuice`, or `Snip + TokenJuice` | They compete for shell/tool-output ownership and can double-filter diagnostics. |
| Multiple retrieval engines, such as `Serena + SigMap`, `CodeGraph + jcodemunch`, or `Claude Context + CocoIndex Code` | They duplicate retrieval authority and may return inconsistent or stale context. |
| Multiple automatic memory systems, such as `Claude Mem + Cavemem` or `Cavemem + Token Savior memory` | They can inject duplicate, stale, or contradictory context. |
| `Headroom + Lowfat`, `Headroom + Snip`, `Headroom + TokenJuice`, or `Headroom + Claw Compactor` | Headroom is a broad compression owner; pairing it with another compressor needs explicit disabled surfaces and benchmarked recovery. |
| `Context-Mode + pctx` | Both own execution offload/result selection. Use one offload owner unless the combination is explicitly documented and tested. |
| `Token Savior + separate retrieval/memory/Bash compaction tools` | Token Savior already combines these surfaces and should be treated as an integrated owner. |
| `ClawCodex` or `Caveman Code` plus hook-layer token-saving stacks | Replacement runtimes already own agent loop, tool execution, memory/context, compression, routing, or cost surfaces. Evaluate them as alternative agents rather than add-on hosts unless overlap is explicitly disabled and tested. |
| `Repomix` or `Gitingest` as default continuous context tools | Repository packing can increase context use. They are better suited to explicit handoff/snapshot tasks than default retrieval. |
| `Context Engine` as a runtime retrieval stack | source-logic inspection of the repository found skills/tool-selection docs and static site code, not runtime MCP implementation. Include only after locating and inspecting runtime code elsewhere. |
| `ccusage`, `Splitrail`, `tokentop`, or `abtop` as reduction stacks | Measurement tools are valuable sidecars but do not directly reduce tokens. |
| `Tokless` as a reduction component | Source inspection shows an installer/orchestrator for other tools rather than an independent token-saving runtime. Use it to reproduce selected non-overlapping profiles, not as an additional stack layer. |

## Selection guidance

| Situation | Recommended research candidate |
|---|---|
| General coding with diverse token waste and source-logic evidence | `Lowfat + SigMap + MEX + Ponytail` |
| Existing agent workflow needing lightweight shell filtering, code intelligence, and compressed memory | `Snip + Serena + Cavemem` |
| Preference for a single broad context layer with optional artifact discipline | `LeanCTX + Ponytail` or `LeanCTX` alone for lower behavior risk |
| Swift/iOS/macOS/Xcode-heavy build-repair work | `xcsift + Serena + MEX` |
| MCP-heavy workflows with large intermediate execution traces | `pctx + jcodemunch MCP + Caveman` |
| Broad logs/files/RAG/history compression with raw-content fallback | `Headroom + MEX` |
| Preference for one integrated MCP owner across retrieval, memory, and Bash compaction | `Token Savior MCP profile` |
| Minimal baseline for comparison with legacy report | `RTK + CodeGraph` |
| Replacement agent acceptable | `ClawCodex` and `Caveman Code` replacement-agent evaluation lane |

## Limitations

The current report remains a research artifact rather than a deployment-grade evaluation.

Key limitations:

- No stack in this report has been reproduced end to end with provider-billed token accounting.
- Most source-logic dossiers inspect representative implementation files, not every runtime path.
- All recommended stack components now have source-logic dossiers, and the backlog has no lead-only entries, but source-logic still covers representative source logic rather than full benchmark or reproduction evidence.
- Maintainer benchmarks and claims have not been independently reproduced in this repository.
- Prompt-cache effects, turn counts, pass rates, latency, correction loops, and implementation-quality outcomes remain unmeasured.
- Stack interactions involving hooks, MCP servers, memory injection, offload sessions, installer/orchestrator profiles, and replacement runtimes require environment-specific verification.
- Repository reputation has intentionally low influence in this report; this may underweight ecosystem maturity until benchmark-audit review adds operational evidence.

## Next review priorities

1. Promote recommended stack candidates from source-logic to benchmark-audit by reviewing benchmark methods, raw outputs, token accounting, and failure semantics.
2. Run comparative benchmark-audit reviews for terminal-output owners: RTK, Lowfat, Snip, TokenJuice, Headroom, and xcsift for Apple workloads.
3. Run comparative retrieval reviews for Serena, SigMap, jcodemunch MCP, Claude Context, CocoIndex Code, Code Review Graph, and LeanCTX.
4. Run replacement-agent benchmark-audit for ClawCodex and Caveman Code, including harness review, raw outputs, provider-billed token accounting, pass rate, latency, and implementation-quality scoring.
5. Define and test Tokless installation profiles that reproduce only selected non-overlapping stack surfaces, then compare profile-installed behavior against manual installation.
