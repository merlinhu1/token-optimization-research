# Tool dossiers

This directory stores cumulative, persistent analysis for token-saving tools. Dossiers are updated across research sessions and should contain source-level findings, not only README summaries.

## Review-level key

- Level 0: discovery lead
- Level 1: surface review
- Level 2: integration review
- Level 3: source behavior review
- Level 4: benchmark review
- Level 5: reproduction review

## Current dossiers

| Tool | Dossier | Current review level | Primary surface |
|---|---|---:|---|
| RTK | `rtk-ai-rtk.md` | 2 | Terminal and tool-output compaction |
| CodeGraph | `colbymchenry-codegraph.md` | 2 | Code retrieval and indexing |
| Ponytail | `dietrichgebert-ponytail.md` | 2 | Artifact and code minimization |
| Token Savior | `mibayy-token-savior.md` | 2 | Integrated MCP retrieval, memory, and Bash compaction |
| Caveman | `juliusbrussee-caveman.md` | 3 | Behavioral output compression |
| Headroom | `chopratejas-headroom.md` | 3 | Broad context compression via library/proxy/wrap/MCP |
| Repomix | `yamadashy-repomix.md` | 3 | Repository packing and digest generation |
| Serena | `oraios-serena.md` | 3 | MCP semantic code retrieval and editing |
| Context-Mode | `mksglu-context-mode.md` | 3 | Execution offload and result selection |
| Claude Mem | `thedotmack-claude-mem.md` | 3 | Persistent context capture, summarization, and reinjection |
| Code Review Graph | `tirth8205-code-review-graph.md` | 3 | SQLite code graph, hybrid search, and review context |
| Gitingest | `coderamp-labs-gitingest.md` | 3 | Repository ingestion and prompt-friendly digest generation |
| Claude Context | `zilliztech-claude-context.md` | 3 | MCP semantic code search with embeddings/vector DB |
| LeanCTX | `yvgude-lean-ctx.md` | 3 | Broad context intelligence layer and MCP tools |
| CocoIndex Code | `cocoindex-io-cocoindex-code.md` | 3 | Embedded AST/vector code search CLI and MCP server |
| Claw Compactor | `open-compress-claw-compactor.md` | 3 | Multi-stage compression and proxy middleware |
| jcodemunch MCP | `jgravelle-jcodemunch-mcp.md` | 3 | MCP symbol retrieval, indexing, and compact encoders |
| MEX | `mex-memory-mex.md` | 3 | Persistent project memory scaffold and drift detection |
| Cavemem | `juliusbrussee-cavemem.md` | 3 | Compressed cross-agent persistent memory |
| Lowfat | `zdk-lowfat.md` | 3 | Terminal/tool-output filtering and command plugins |
| SigMap | `manojmallick-sigmap.md` | 3 | Signature-map code retrieval, graph, and MCP tools |
| TokenJuice | `vincentkoc-tokenjuice.md` | 3 | Terminal-heavy output compaction and host hooks |
| xcsift | `ldomaradzki-xcsift.md` | 3 | Xcode/xcodebuild output parsing and compaction |
| Context Engine | `context-engine-ai-context-engine.md` | 2 | MCP retrieval skill/tool-selection guidance |
| Snip | `edouard-claude-snip.md` | 3 | CLI proxy/hook-based command-output filtering |
| pctx | `portofcontext-pctx.md` | 3 | Execution offload/code mode for MCP/tool calls |
| ClawCodex | `agentforce314-clawcodex.md` | 3 | Replacement AI coding agent with token/cost/compaction subsystems |

## Policy

Reports should cite dossier review levels when making stack recommendations. If a tool lacks a dossier, it should be treated as a candidate or discovery lead unless another source file contains equivalent analysis.

A compatibility-safe stack is one whose components do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.
