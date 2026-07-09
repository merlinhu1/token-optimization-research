# Tools

This section indexes the token-saving tools studied by the project. Detailed source-level analysis lives under `dossiers/`; each dossier is updated across research sessions and records more than README claims.

For current treatment validity, read the [official-integration parity audit](../papers/official-integration-parity-audit.md). The [Phase 2 paper](../papers/phase-2-lifecycle-v0-natural-use-screening.md) contains current scoped reproduction evidence but is not a stable product ranking. For selection and promotion rules, read the [tool research strategy](../research/tool-research-strategy.md).

## Evidence-stage key

- `lead`: discovery candidate only; no dossier and no decision evidence.
- `source-logic`: minimum dossier stage; representative implementation logic inspected.
- `benchmark-audit`: benchmark harness, tasks, scoring, token accounting, and raw outputs inspected.
- `reproduction`: independent target-workload reproduction with complete provider-reported token usage and execution integrity; verifier and optional source-review outcomes are separate diagnostics.

## Current dossiers

Current dossier files are listed below. Their dossier stage remains `source-logic` with pinned source-snapshot metadata; separate evaluation records provide scoped reproduction evidence for the tested profile identities and do not automatically promote the dossiers themselves.

| Tool | Dossier | Current evidence stage | Primary surface |
|---|---|---:|---|
| rtk-ai/rtk | [dossier](rtk-ai-rtk.md) | source-logic | Terminal and tool-output compaction through command rewriting, filters, guarded output, and raw-output recovery |
| safishamsi/graphify | [dossier](safishamsi-graphify.md) | source-logic | Source-logic dossier surface recorded in file |
| colbymchenry/codegraph | [dossier](colbymchenry-codegraph.md) | source-logic | Code retrieval and graph-indexing authority exposed through CLI/MCP-oriented workflows |
| DietrichGebert/ponytail | [dossier](dietrichgebert-ponytail.md) | source-logic | Artifact and code-minimization policy layer with hook/plugin/MCP delivery paths |
| Mibayy/token-savior | [dossier](mibayy-token-savior.md) | source-logic | Integrated MCP owner for retrieval, memory, compact operations, and Bash command rewriting |
| chopratejas/headroom | [dossier](chopratejas-headroom.md) | source-logic | Broad context compression through library, proxy, agent wrapper, and MCP modes |
| mksglu/context-mode | [dossier](mksglu-context-mode.md) | source-logic | Execution offload, MCP/tool sandboxing, result selection, and routing hooks |
| HoangP8/tokless | [dossier](hoangp8-tokless.md) | source-logic | installer/orchestrator for multiple external token-saving tools and supported agents |
| JuliusBrussee/caveman-code | [dossier](juliusbrussee-caveman-code.md) | source-logic | replacement AI coding agent/runtime with its own loop, tool execution, memory, routing, compression, cost accounting, repository-map, and benchmark subsystems |
| JuliusBrussee/caveman | [dossier](juliusbrussee-caveman.md) | source-logic | Behavioral output compression and instruction/MCP-description compression |
| yamadashy/repomix | [dossier](yamadashy-repomix.md) | source-logic | Repository packing and optional compression/digest generation |
| oraios/serena | [dossier](oraios-serena.md) | source-logic | MCP-based semantic code retrieval and editing toolkit |
| thedotmack/claude-mem | [dossier](thedotmack-claude-mem.md) | source-logic | Persistent context capture, summarization, memory retrieval, and context reinjection |
| tirth8205/code-review-graph | [dossier](tirth8205-code-review-graph.md) | source-logic | SQLite-backed code graph, hybrid search, and minimal review context assembly |
| coderamp-labs/gitingest | [dossier](coderamp-labs-gitingest.md) | source-logic | Repository ingestion and prompt-friendly repository digest generation |
| yvgude/lean-ctx | [dossier](yvgude-lean-ctx.md) | source-logic | Broad context intelligence layer: compressed reads, search, shell compression, memory, code graph, and MCP tools |
| cocoindex-io/cocoindex-code | [dossier](cocoindex-io-cocoindex-code.md) | source-logic | Embedded AST/vector code search CLI and MCP server |
| open-compress/claw-compactor | [dossier](open-compress-claw-compactor.md) | source-logic | Multi-stage text/tool-result compression pipeline and proxy middleware |
| jgravelle/jcodemunch-mcp | [dossier](jgravelle-jcodemunch-mcp.md) | source-logic | MCP symbol/code retrieval, indexing, schema-driven compact encoding, and ranked context assembly |
| mex-memory/mex | [dossier](mex-memory-mex.md) | source-logic | Persistent project memory scaffold, drift detection, and multi-tool config synchronization |
| JuliusBrussee/cavemem | [dossier](juliusbrussee-cavemem.md) | source-logic | Compressed cross-agent persistent memory with MCP/CLI hooks and semantic search |
| zdk/lowfat | [dossier](zdk-lowfat.md) | source-logic | Terminal/tool-output filtering and command-specific compression plugins |
| manojmallick/sigmap | [dossier](manojmallick-sigmap.md) | source-logic | Signature-map code retrieval, dependency graph, session memory, and MCP tools |
| vincentkoc/tokenjuice | [dossier](vincentkoc-tokenjuice.md) | source-logic | Terminal-heavy command-output compaction and host hook/wrap integration |
| ldomaradzki/xcsift | [dossier](ldomaradzki-xcsift.md) | source-logic | Xcode/xcodebuild output parsing into token-efficient structured JSON/TOON |
| Context-Engine-AI/Context-Engine | [dossier](context-engine-ai-context-engine.md) | source-logic | Skill/tool-selection guidance and static marketing/documentation site, not a validated runtime retrieval implementation in this repo |
| edouard-claude/snip | [dossier](edouard-claude-snip.md) | source-logic | CLI proxy/hook-based command-output filtering with declarative filters |
| portofcontext/pctx | [dossier](portofcontext-pctx.md) | source-logic | Execution offload/code mode that converts MCP/tool calls into sandboxed code workflows |
| agentforce314/clawcodex | [dossier](agentforce314-clawcodex.md) | source-logic | Replacement AI coding agent with token estimation, compaction pipeline, memory/history, and cost tracking |
| Egonex-AI/Understand-Anything | [dossier](egonex-ai-understand-anything.md) | source-logic | Source-logic dossier surface recorded in file |
| swarmclawai/swarmvault | [dossier](swarmclawai-swarmvault.md) | source-logic | Source-logic dossier surface recorded in file |
| catlog22/maestro-flow | [dossier](catlog22-maestro-flow.md) | source-logic | Source-logic dossier surface recorded in file |
| osovv/grace-marketplace | [dossier](osovv-grace-marketplace.md) | source-logic | Source-logic dossier surface recorded in file |
| vbcherepanov/total-agent-memory | [dossier](vbcherepanov-total-agent-memory.md) | source-logic | Source-logic dossier surface recorded in file |
| looptech-ai/understand-quickly | [dossier](looptech-ai-understand-quickly.md) | source-logic | Source-logic dossier surface recorded in file |
| jrollin/cartog | [dossier](jrollin-cartog.md) | source-logic | Source-logic dossier surface recorded in file |
| cognitx-leyton/codegraph | [dossier](cognitx-leyton-codegraph.md) | source-logic | Source-logic dossier surface recorded in file |
| onur-gokyildiz-bhi/codescope | [dossier](onur-gokyildiz-bhi-codescope.md) | source-logic | Source-logic dossier surface recorded in file |
| iikarus/Dragon-Brain | [dossier](iikarus-dragon-brain.md) | source-logic | Source-logic dossier surface recorded in file |
| STiFLeR7/memex | [dossier](stifler7-memex.md) | source-logic | Source-logic dossier surface recorded in file |
| ishandutta2007/Code-Knowledge-Graph | [dossier](ishandutta2007-code-knowledge-graph.md) | source-logic | Source-logic dossier surface recorded in file |

## Policy

Reports should cite dossier evidence stages when making stack recommendations. If a tool lacks source-logic inspection, it must remain a discovery lead and must not drive stack decisions.

A compatibility-safe stack is one whose components do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Source snapshot policy

Every actual tool dossier records source snapshot metadata in its identity section.

- `Snapshot status: pinned-commit` means the inspected source is tied to an immutable commit or commit prefix recorded during inspection.
- `Snapshot status: unpinned-historical-inspection` means the historical inspection used a moving source such as GitHub `HEAD` and did not record an immutable commit.

Future source-logic dossiers should resolve GitHub `HEAD`, default branches, and other moving refs to an immutable commit SHA before making source-level claims. If a future historical dossier is marked unpinned, it must not be silently backfilled with current upstream HEAD; it needs a fresh source-logic refresh to become pinned.

A repository without auditable source versioning for the inspected state is not a valid candidate for recommendation, stack construction, benchmark-audit, or reproduction. If present, unpinned historical dossiers can remain as research notes and refresh targets, but they are candidate-ineligible until a pinned snapshot is recorded.

Use `python3 scripts/audit_dossier_snapshots.py` to inventory pinned dossier metadata and candidate eligibility.
