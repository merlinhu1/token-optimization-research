# Tool dossier: onur-gokyildiz-bhi/codescope

## Identity

- Repository: `onur-gokyildiz-bhi/codescope`
- URL: https://github.com/onur-gokyildiz-bhi/codescope
- Local clone inspected: `/tmp/token-leads-20260629/onur-gokyildiz-bhi__codescope`
- Version/ref inspected: local shallow clone commit `d8e58d83e920`
- Snapshot status: pinned-commit
- Commit inspected: d8e58d83e920
- Commit URL: https://github.com/onur-gokyildiz-bhi/codescope/commit/d8e58d83e920
- Source artifact path: `sources/discovery/2026-06-29-graph-leads-c-source-logic.json`
- Date inspected: 2026-06-29
- Evidence stage: source-logic
- License observed in manifest: MIT

## Summary

Codescope is a Rust code-intelligence stack that parses supported project files, writes a SurrealDB-backed knowledge graph, and exposes graph/search/context tools through CLI, stdio MCP, HTTP MCP, web, LSP, and VS Code surfaces. Source logic shows explicit token-surface interventions: graph lookups instead of raw file reads/grep, context summaries injected into MCP instructions, large-output archiving with retrieval IDs, and optional output compaction.

## Evidence inventory

| Evidence type | Source file paths inspected | Notes |
|---|---|---|
| Manifest/workspace | `Cargo.toml` | Rust workspace with `core`, `mcp-server`, `cli`, `web`, `lsp`, `e2e`; SurrealDB, tree-sitter, MCP, fastembed, notify dependencies. |
| CLI entrypoint | `crates/cli/src/main.rs` | Dispatches index/search/query/init/mcp/web/lsp/daemon/review/gain/exec/ingest commands; emits structured JSON error bodies on failure. |
| MCP entrypoint | `crates/mcp-server/src/main.rs` | Supports stdio, HTTP daemon, background start/stop/status, auto-index flags, PID/log files under `~/.codescope`. |
| MCP server/router | `crates/mcp-server/src/server.rs`, `crates/mcp-server/src/tools/mod.rs` | Merges search/callgraph/http/refactor/skills/temporal/conversation/memory/knowledge/indexed/sandbox tool routers; maintains project context, index gate, result archive, context cache. |
| Indexing pipeline | `crates/mcp-server/src/indexing.rs` | Staged parse before DB cleanup, rayon file parsing, SurrealDB insertion, call resolution, git/conversation indexing, embeddings, watcher phases. |
| Graph storage/query | `crates/core/src/graph/builder.rs`, `crates/core/src/graph/query.rs` | Batched UPSERT/INSERT RELATION; graph queries for functions, callers, callees, file entities, raw SurrealQL, stats, explore. |
| Parser/source extraction | `crates/core/src/parser/extractor.rs` | Extracts file/function/class/import entities, contains/imports/calls/inheritance edges, arrow-function declarations, body hashes. |
| Output/runtime helpers | `crates/mcp-server/src/helpers.rs` | Archives outputs over 4096 chars with retrieval IDs; builds conversation/context summaries from graph tables. |
| Install/editor integration | `install.sh`, `vscode-extension/src/extension.ts` | Release downloader installs binaries and bundled Surreal binary; VS Code extension spawns `codescope mcp ... --auto-index` and calls MCP tools. |
| Tests | `crates/mcp-server/tests/graph_query_tests.rs` | In-memory SurrealDB tests verify query-layer behavior for search, callers/callees, and file entities. |

## Installation and integration behavior

- `install.sh` detects OS/architecture, calls the GitHub releases API, downloads `codescope`, `codescope-mcp`, `codescope-web`, copies them to an existing install directory or `~/.local/bin`, and places bundled `surreal` under `~/.codescope/bin`.
- The installer can stop running `codescope`/`codescope-mcp` processes before overwriting binaries and can append a PATH export to the user's shell rc file in an interactive terminal.
- CLI `init` and `mcp` commands wire the Rust MCP server to a target project. `codescope-mcp` stdio mode can auto-index; daemon mode serves web UI plus MCP under `/mcp` on `127.0.0.1:9877` by default.
- VS Code extension source starts `codescope mcp <workspace> --auto-index` as a child process and sends JSON-RPC `tools/call` requests for index/search/stats commands.

## Runtime behavior

- Indexing walks supported files with ignore/gitignore handling, parses in parallel, and stages parse output before clearing graph tables so an empty parse does not wipe a prior index.
- Graph writes use SurrealDB tables for files, functions, classes, imports, configs, docs, packages, infra, skills, HTTP calls, and edge tables such as `contains`, `calls`, `imports`, `inherits`.
- Query tools read graph tables with default limits and timeouts; caller/callee queries group duplicate legacy edges.
- MCP server returns an index-gate status while background indexing is in progress or failed, instead of silently returning empty results.
- The server keeps in-memory per-session result archives and context caches; large results can be retrieved via `retrieve_archived`.

## Token-saving mechanism

- Primary mechanism: replace broad file reads, grep, and manual call tracing with pre-indexed graph calls (`find_function`, `search_functions`, `find_callers`, `find_callees`, `file_entities`, `explore`, `impact_analysis` in tool surface).
- Secondary mechanisms: MCP instructions tell agents to prefer graph/context tools before raw reads; `maybe_archive` truncates large tool outputs and offers retrieval IDs; `raw_query` can apply environment-driven JSON compaction.
- Quality-preservation logic at source-logic stage: graph queries expose line/file/signature metadata so the agent can still open exact code bodies after narrowing; tests exercise key query paths.

## Benchmarks and claims

- README/marketing claims were not used as decision evidence.
- This pass inspected source and tests only; no benchmark-audit or reproduction evidence is promoted here.
- Source comments mention prior performance fixes and a bad historical benchmark, but those comments are not treated as measured effectiveness evidence.

## Lifecycle-v0 evaluation outcome

- A checksum-verified `v0.8.12` Linux release and bundled SurrealDB were qualified against pinned source commit `d8e58d83e920`.
- The official 37-tool stdio MCP surface passed index/search smoke testing. Mandatory upstream initialization wording that instructed agents to always prefer CodeScope was removed for the natural-use arm; ordinary tool schemas and responses remained available.
- The first valid `r1` screen used 5,516,066 provider tokens on Fastify, 15,344,837 on Beets, and 64,579,065 on Terraform. Aggregate usage was 85,439,968 tokens, +15.63% versus the matched baseline.
- All 9/9 verifier tasks passed. No explicit model-issued CodeScope MCP call was observed; that diagnostic does not invalidate the frozen natural-availability assignment.

## Compatibility notes

- Broad context owner: Codescope overlaps with code graph, search, memory, shell/output compression, web UI, editor extension, and MCP surfaces.
- Compatibility-safe use requires deciding whether Codescope or another tool owns graph indexing, memory/knowledge, retrieval, output truncation, editor hooks, daemon state, and raw-output recovery.
- SurrealDB state under `~/.codescope` and daemon PID/log files become part of the agent runtime boundary.

## Failure modes and limits

- Requires compatible release assets or a Rust build path; installer depends on GitHub API/download availability.
- SurrealDB/daemon unavailability surfaces as structured errors, but tools still depend on DB readiness.
- In-memory result archive is bounded and session-local; archived IDs can disappear after process restart or eviction.
- Unsupported languages/files will not produce graph entities; stale or duplicate edges can persist in legacy DBs despite dedup/grouping mitigations.
- Installer has side effects: process termination, binary overwrite, PATH-shell modification, and bundled Surreal binary install.

## Open questions

- Which language parsers are sufficiently complete for target repositories beyond representative extractor paths?
- How stable is the daemon/web/MCP path under multi-project concurrent use?
- What raw-output recovery guarantees are needed when archives are in memory only?

## Next review tasks

- [x] Run a bounded source-logic smoke test on a small fixture to verify index/search/MCP round trip.
- [x] Inspect the production MCP initialization and state boundaries needed for an isolated natural-use screen.
- [x] Map `~/.codescope` state and bundled SurrealDB into lane-private homes for reproducibility.
- [ ] Audit upstream benchmark artifacts separately from the retained lifecycle-v0 provider-token evidence.
