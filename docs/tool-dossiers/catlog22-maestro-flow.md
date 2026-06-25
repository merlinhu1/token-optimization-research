# Tool dossier: catlog22/maestro-flow

## Identity

- Repository: `catlog22/maestro-flow`
- URL: https://github.com/catlog22/maestro-flow
- Version/ref inspected: local shallow clone `6f1d8b6dc41d`, 2026-06-29
- Date inspected: 2026-06-29
- Evidence stage: source-logic (local source inspection of package/CLI/MCP entrypoints, graph facade/query, hook context injection/budgeting, search daemon, file tools, coordinator prompt assembly, and tests)
- License: MIT (`package.json`)

## Summary

Maestro Flow is a Node/TypeScript workflow orchestration CLI with MCP tools, graph/knowledge-graph features, context hooks, search daemon, and multi-agent coordination surfaces. Source inspection confirms lazy command loading, MCP tool registration, graph search/path/impact abstractions, prompt assembly with prior-step state, and context-budget/knowledge-graph injection logic. This is source-logic evidence only, not benchmark or reproduction evidence.

## Evidence inventory

| Evidence type | Files inspected | Notes |
|---|---|---|
| Manifest/entrypoints | `package.json`, `src/cli.ts`, `src/mcp/server.ts` | Bins `maestro`, `maestro-mcp`, statusline/context monitor; lazy CLI command registration and MCP server. |
| Graph/query runtime | `src/graph/facade.ts`, `src/graph/query.ts`, `src/hooks/kg-context-injector.ts` | SQLite/JSON graph backend selection, search/path/diff/impact methods, prompt-time KG context injection. |
| Context/token surfaces | `src/hooks/context-budget.ts`, `src/coordinator/prompt-assembler.ts`, `src/tools/read-many-files.ts` | Context budget tiers, coordinated prompt composition, bounded multi-file reading. |
| Search runtime | `src/search/daemon.ts` | Resident localhost JSON-over-TCP daemon with prewarmed wiki/embedding index and idle shutdown. |
| Tests | `src/coordinator/__tests__/prompt-assembler.test.ts` | Representative tests for prompt arg resolution, command construction, previous-context injection. |

## Installation and integration behavior

- `package.json` exposes bins `maestro`, `maestro-mcp`, `maestro-statusline`, and `maestro-context-monitor`; npm package files include compiled dist, workflows, chains, templates, and agent/skill mirrors.
- CLI uses Commander but lazily imports only the requested command module, reducing startup import surface for common commands.
- MCP server creates a `maestro` server using `@modelcontextprotocol/sdk`, registers builtin tools through a `ToolRegistry`, filters tools via `MAESTRO_ENABLED_TOOLS` or config, and uses stdio transport.
- MCP server also starts a delegate channel relay and writes diagnostic client handshake JSON under Maestro data paths after initialization.
- Source files include install/uninstall commands and hooks command modules, but full install/uninstall code paths were not exhaustively reviewed.

## Runtime behavior

- `GraphFacade` detects SQLite graph backend first, then JSON graph, then none; SQLite paths use `DatabaseConnection`, `QueryBuilder`, `GraphQueryManager`, and `GraphTraverser`.
- JSON query helpers perform substring node search, undirected BFS shortest path, and direct + 1-hop impacted node lookup from changed files.
- `kg-context-injector.ts` extracts file paths and backticked symbols from prompts, opens `MaestroGraph` if initialized, retrieves callers/callees/exports, and injects bounded `<maestro-context>` sections up to a 3072-character cap.
- `context-budget.ts` reads statusline bridge metrics from temp files and chooses full/reduced/minimal/skip injection tiers based on remaining context percentage.
- `read-many-files.ts` validates paths, traverses directories with max depth/file/content caps, supports glob and regex content search, and returns compact file entries.
- `search/daemon.ts` keeps a `WikiIndexer` and embedding index warm behind a localhost TCP JSON protocol, with daemon state written to workflow root and 30-minute idle shutdown.
- `DefaultPromptAssembler` builds coordinated subagent prompts from command nodes, resolved variables, previous-step result summaries, state snapshots, original intent, and required report instructions.

## Token-saving mechanism

- Addressable token surface: agent prompt context, workflow state transfer, code graph context, wiki/search retrieval, and multi-file reads.
- Reduction method: context-budget tiers omit/truncate spec content when remaining context is low; KG injection selects only referenced symbols/files; file reads cap files/content; search daemon avoids repeated cold indexing and returns ranked wiki entries.
- Quality-preservation mechanisms seen in source: required coordinator report contract, previous-result/state carryover, graph caller/callee/exports context, path validation, max-content caps, and tests for prompt assembly.
- Cases where savings may not translate to billed reductions: orchestration can add turns/subagents, injected workflow instructions may be large, graph/wiki data can be stale, and duplicate retrieval systems may create context overlap.

## Benchmarks and claims

No benchmark-audit was performed. The inspected source supports mechanism claims for context selection and workflow orchestration, but not measured token reduction, speedup, or task quality claims.

## Compatibility notes

Maestro Flow can control workflows, MCP tools, hooks, graph context injection, search daemon, and file-reading behavior. In a compatibility-safe stack, treat it as a high-level orchestration/context authority and avoid mixing with another uncoordinated hook/context injector or graph retrieval authority unless routing is explicit.

## Failure modes and limits

- SQLite graph methods throw if the backend is not initialized; JSON fallback is simpler and less featureful.
- Hook KG injection silently skips on no references, missing MaestroGraph initialization, no matches, or import failures.
- Context-budget decisions depend on fresh statusline bridge metrics; stale/missing metrics default to full content.
- Search daemon state can become stale; daemon invalidation/rebuild behavior must be wired correctly.
- MCP server diagnostic handshake files and delegate relay introduce additional local state/process surfaces.

## Open questions

- Which hooks are installed by default for each supported host, and how are they disabled?
- How large are injected Maestro context blocks in real workflows?
- Does workflow orchestration reduce total billed tokens or increase them via extra coordination turns?

## Next review tasks

- [ ] Inspect `src/commands/install.ts`, hook manager, and generated agent/skill mirrors for exact platform side effects.
- [ ] Run a minimal workflow with statusline bridge metrics to observe actual injection tiers.
- [ ] Compare a fixed task with/without Maestro orchestration using provider-billed accounting and quality gates.
