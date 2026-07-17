# Tool dossier: swarmclawai/swarmvault

## Identity

- Repository: `swarmclawai/swarmvault`
- URL: https://github.com/swarmclawai/swarmvault
- Version/ref inspected: local shallow clone `4ce0c7cb545c`, 2026-06-29
- Snapshot status: pinned-commit
- Commit inspected: 4ce0c7cb545c
- Commit URL: https://github.com/swarmclawai/swarmvault/commit/4ce0c7cb545c
- Source artifact path: `sources/discovery/2026-06-29-graph-leads-a-source-logic.json`
- Date inspected: 2026-06-29
- Evidence stage: source-logic (local source inspection of workspace manifest, engine exports, MCP server, vault/retrieval/search/token logic, Obsidian plugin, and retrieval tests)
- License: `LICENSE` present in repository root

## Summary

SwarmVault is a TypeScript workspace for ingesting sources into a local vault/wiki/graph, exposing graph/search/retrieval/memory workflows through CLI/MCP and an Obsidian plugin. Source inspection confirms SQLite FTS retrieval artifacts, graph query tools, token-estimation utilities, compile/query/search surfaces, MCP tools, and health/doctor repair behavior. A later lifecycle-v0 natural-use screen is recorded below; upstream benchmark claims remain unaudited.

## Evidence inventory

| Evidence type | Files inspected | Notes |
|---|---|---|
| Manifest/entrypoints | `package.json`, `packages/engine/src/index.ts` | pnpm workspace scripts and broad engine public API. |
| MCP/server | `packages/engine/src/mcp.ts` | Registers workspace, retrieval, graph, page, source, memory, and doctor tools. |
| Vault/query runtime | `packages/engine/src/vault.ts`, `packages/engine/src/graph-tools.ts` | Compile/query/search surfaces and graph matching/traversal helpers. |
| Retrieval/search/token logic | `packages/engine/src/retrieval.ts`, `packages/engine/src/search.ts`, `packages/engine/src/token-estimation.ts` | SQLite FTS index, retrieval manifest/staleness, token heuristic/trimming. |
| Integration/tests | `packages/obsidian-plugin/src/main.ts`, `packages/engine/test/retrieval.test.ts` | Obsidian plugin lifecycle/CLI version checks; tests for retrieval artifact creation, search, repair, migration. |

## Installation and integration behavior

- Root package is a pnpm monorepo; scripts build viewer, engine, and CLI packages and run checks/tests.
- Engine exports `createMcpServer`/`startMcpServer`, vault compile/query/search/read APIs, retrieval repair/status APIs, graph export/status tools, memory tasks, watch hooks, and provider config.
- MCP server registers tools including `workspace_info`, `search_pages`, `retrieval_status`, `rebuild_retrieval`, `doctor_retrieval`, `doctor_vault`, `read_page`, `list_sources`, `query_graph`, `graph_report`, and `graph_stats`.
- Obsidian plugin registers views/commands, resolves workspace root, probes CLI version against `cli-compat.json`, displays freshness/status, and stops managed processes on unload.
- The inspected code did not include a single install script; integration appears split across packages, CLI/package publishing, Obsidian plugin, and skills directory.

## Runtime behavior

- `vault.ts` is the central orchestration module: imports ingestion, source analysis, graph construction/enrichment, page generation, search index rebuild, provider calls, memory pages, and approval/promotion flows.
- `retrieval.ts` writes `state/retrieval/manifest.json` describing a SQLite backend shard and computes a graph hash from generated graph/page metadata; status detects missing/stale graph/index/manifest.
- `rebuildRetrievalIndex` loads graph artifact, rebuilds SQLite FTS from graph pages/wiki content, writes manifest, then returns status.
- `search.ts` uses Node built-in `node:sqlite` `DatabaseSync` and FTS5 tables over page title/body, incorporating source excerpts for source/module pages when available.
- `graph-tools.ts` normalizes labels, scores node/page/hyperedge matches, builds adjacency, and exposes graph query/path/explain/stat style helpers.
- `token-estimation.ts` estimates tokens by prose/code character heuristics and trims page sets by priority when above budget.

## Token-saving mechanism

- Addressable token surface: vault/wiki page retrieval, graph traversal, memory/task context, and page packs for agents.
- Reduction method: compile sources into pages/graph artifacts; index generated pages in SQLite FTS; use MCP/CLI search and graph traversal to retrieve narrower page/node context; optional token-budget trimming can drop lower-priority pages.
- Quality-preservation mechanisms seen in source: retrieval staleness checks, doctor repair path, graph validation/status tools, source/page citations fields, tests for retrieval artifact creation/repair, and priority-based token trimming.
- Cases where savings may not translate to billed reductions: compile/provider work may add cost, generated wiki summaries may omit needed details, stale retrieval artifacts can mislead, and multiple graph authorities can duplicate context.

## Benchmarks and claims

No benchmark-audit was performed. `benchmark.ts` is present/imported in `vault.ts` and package scripts include live smoke/perf checks, but benchmark methodology/raw outputs were not inspected here. Treat any token or performance claims as unverified until benchmark artifacts are audited.

## Lifecycle-v0 evaluation outcome

- Source-built CLI `3.20.0` at pinned commit `4ce0c7cb545c` passed lite initialization, offline heuristic ingest/compile, 51-tool stdio MCP, workspace-info, and three-lane container preflight checks.
- The treatment used a warm lane-private vault and SwarmVault's deterministic native `--max-files 500` scale cap. No task-specific paths, cloud/local model providers, agent rules, hooks, or viewer were enabled.
- The first valid `r1` screen used 16,974,841 provider tokens on Fastify, 15,464,870 on Beets, and 28,715,407 on Terraform. Aggregate usage was 61,155,118 tokens, -17.24% versus the matched baseline.
- All 9/9 verifier tasks passed. No explicit model-issued SwarmVault MCP call was observed; the natural-availability sample was retained without forced uptake or rerun selection.

## Compatibility notes

SwarmVault can act as a graph/wiki/retrieval/memory authority and can expose MCP tools. In a compatibility-safe stack, avoid overlapping it with another primary graph retrieval system or memory authority without explicit routing (for example Graphify, MaestroGraph, CodeGraph, Serena, LeanCTX, or another Obsidian/agent memory layer).

## Failure modes and limits

- Runtime depends on pnpm workspace packages, Node with `node:sqlite`, and package-specific build outputs.
- Retrieval status can be stale when graph/page metadata changes; doctor repair can rebuild but must be invoked or wired into workflow.
- SQLite FTS query syntax requires conservative escaping; tests cover hyphenated concept targets.
- Obsidian plugin requires a compatible CLI binary; missing/old CLI is surfaced through notices/status.
- Source inspection did not verify provider integrations, live smoke scripts, or full compile quality.

## Open questions

- Which CLI package/bin installs the MCP server and engine in the intended target environment?
- How large are generated pages versus source corpus, and how often are source excerpts included in FTS bodies?
- What provider calls are made during compile/consolidate/query on a representative workload?

## Next review tasks

- [x] Inspect CLI package entrypoints and the exact source-built MCP deployment behavior.
- [ ] Audit `benchmark.ts`, perf budgets, and any raw outputs before using benchmark wording.
- [x] Run fixed source corpora through ingest/compile/MCP and measure provider-reported workflow usage with verifier diagnostics.
