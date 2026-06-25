# Tool dossiers

This directory stores cumulative, persistent analysis for token-saving tools. Dossiers are updated across research sessions and should contain source-level findings, not only README summaries.

## Evidence-stage key

- `lead`: discovery candidate only; no dossier and no decision evidence.
- `source-logic`: minimum dossier stage; representative implementation logic inspected.
- `benchmark-audit`: benchmark harness, tasks, scoring, token accounting, and raw outputs inspected.
- `reproduction`: independent target-workload reproduction with provider-billed usage and quality gates.

## Current dossiers

| Tool | Dossier | Current evidence stage | Primary surface |
|---|---|---:|---|
| RTK | `rtk-ai-rtk.md` | source-logic | Terminal and tool-output compaction |
| CodeGraph | `colbymchenry-codegraph.md` | source-logic | Code retrieval and indexing |
| Ponytail | `dietrichgebert-ponytail.md` | source-logic | Artifact and code minimization |
| Token Savior | `mibayy-token-savior.md` | source-logic | Integrated MCP retrieval, memory, and Bash compaction |
| Caveman | `juliusbrussee-caveman.md` | source-logic | Behavioral output compression |
| Headroom | `chopratejas-headroom.md` | source-logic | Broad context compression via library/proxy/wrap/MCP |
| Repomix | `yamadashy-repomix.md` | source-logic | Repository packing and digest generation |
| Serena | `oraios-serena.md` | source-logic | MCP semantic code retrieval and editing |
| Context-Mode | `mksglu-context-mode.md` | source-logic | Execution offload and result selection |
| Claude Mem | `thedotmack-claude-mem.md` | source-logic | Persistent context capture, summarization, and reinjection |
| Code Review Graph | `tirth8205-code-review-graph.md` | source-logic | SQLite code graph, hybrid search, and review context |
| Gitingest | `coderamp-labs-gitingest.md` | source-logic | Repository ingestion and prompt-friendly digest generation |
| Claude Context | `zilliztech-claude-context.md` | source-logic | MCP semantic code search with embeddings/vector DB |
| LeanCTX | `yvgude-lean-ctx.md` | source-logic | Broad context intelligence layer and MCP tools |
| CocoIndex Code | `cocoindex-io-cocoindex-code.md` | source-logic | Embedded AST/vector code search CLI and MCP server |
| Claw Compactor | `open-compress-claw-compactor.md` | source-logic | Multi-stage compression and proxy middleware |
| jcodemunch MCP | `jgravelle-jcodemunch-mcp.md` | source-logic | MCP symbol retrieval, indexing, and compact encoders |
| MEX | `mex-memory-mex.md` | source-logic | Persistent project memory scaffold and drift detection |
| Cavemem | `juliusbrussee-cavemem.md` | source-logic | Compressed cross-agent persistent memory |
| Lowfat | `zdk-lowfat.md` | source-logic | Terminal/tool-output filtering and command plugins |
| SigMap | `manojmallick-sigmap.md` | source-logic | Signature-map code retrieval, graph, and MCP tools |
| TokenJuice | `vincentkoc-tokenjuice.md` | source-logic | Terminal-heavy output compaction and host hooks |
| xcsift | `ldomaradzki-xcsift.md` | source-logic | Xcode/xcodebuild output parsing and compaction |
| Context Engine | `context-engine-ai-context-engine.md` | source-logic | MCP retrieval skill/tool-selection guidance |
| Snip | `edouard-claude-snip.md` | source-logic | CLI proxy/hook-based command-output filtering |
| pctx | `portofcontext-pctx.md` | source-logic | Execution offload/code mode for MCP/tool calls |
| ClawCodex | `agentforce314-clawcodex.md` | source-logic | Replacement AI coding agent with token/cost/compaction subsystems |
| Tokless | `hoangp8-tokless.md` | source-logic | Installer/orchestrator for token-saving tool stacks across agents |
| Caveman Code | `juliusbrussee-caveman-code.md` | source-logic | Replacement AI coding agent/runtime with memory, repomap, compression, cost, and benchmarks |

## Policy

Reports should cite dossier evidence stages when making stack recommendations. If a tool lacks source-logic inspection, it must remain a discovery lead and must not drive stack decisions.

A compatibility-safe stack is one whose components do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.
