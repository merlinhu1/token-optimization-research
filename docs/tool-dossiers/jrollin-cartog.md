# Tool dossier: jrollin/cartog

## Identity

- Repository: `jrollin/cartog`
- URL: https://github.com/jrollin/cartog
- Local clone inspected: `/tmp/token-leads-20260629/jrollin__cartog`
- Version/ref inspected: local shallow clone `890d15b66b52`, 2026-06-29
- Snapshot status: pinned-commit
- Commit inspected: 890d15b66b52
- Commit URL: https://github.com/jrollin/cartog/commit/890d15b66b52
- Source artifact path: `sources/discovery/2026-06-29-graph-leads-b-source-logic.json`
- Date inspected: 2026-06-29
- Evidence stage: source-logic (local shallow clone; representative Cargo workspace, CLI, MCP server/tools, indexer, database query layer, RAG search/context, LSP gate, plugin hooks, and tests inspected)

## Summary

Cartog is a Rust code-graph/indexing toolkit with CLI, MCP server, RAG search/context, LSP-assisted edge resolution, editor/Claude plugin integration, and SQLite-backed local state. Source inspection confirms it indexes source files with tree-sitter extractors, stores symbols/edges/content/embeddings, exposes graph-navigation and task-context MCP tools, and defaults MCP output to compact/token-bounded forms. It is a strong candidate as a local code-retrieval authority, not just a registry or README-level lead.

## Evidence inventory

| Evidence type | Files inspected | Notes |
|---|---|---|
| Workspace/manifests | `Cargo.toml`, `crates/cartog/Cargo.toml`, `crates/cartog-mcp/Cargo.toml`, `crates/cartog-indexer/Cargo.toml`, `crates/cartog-rag/Cargo.toml` (some identified) | Workspace version, internal crates, tree-sitter, SQLite/vector, FastEmbed, MCP, watcher, and LSP dependency surfaces inspected/identified. |
| CLI/commands | `crates/cartog/src/main.rs`, `crates/cartog/src/cli.rs`, `crates/cartog/src/commands/search.rs` (identified), `crates/cartog/src/commands/index.rs` (identified), `crates/cartog/src/commands/ide/run.rs` (identified) | CLI dispatch, consent gate, DB resolution, token/compact flags, serve/watch/index/rag/search/context commands inspected. |
| MCP server/tools | `crates/cartog-mcp/src/lib.rs`, `crates/cartog-mcp/src/tools/index.rs`, `crates/cartog-mcp/src/tools/search.rs`, `crates/cartog-mcp/src/tools/graph.rs`, `crates/cartog-mcp/src/tools/rag.rs`, `crates/cartog-mcp/src/tools/manage.rs` (identified) | MCP exposes indexing, graph navigation, semantic search, context, stats/map/changes, and update/manage tools. |
| Index/query/RAG internals | `crates/cartog-indexer/src/lib.rs`, `crates/cartog-db/src/store/queries.rs`, `crates/cartog-rag/src/search.rs`, `crates/cartog-rag/src/context.rs`, `crates/cartog-lsp/src/manager.rs` (identified), `crates/cartog-languages/src/*.rs` (identified) | Parallel parsing, Merkle/hash incremental updates, SQL query ranking, snippets, task-context bundle, and LSP warm-pass behavior inspected/identified. |
| Hooks/tests/skills | `skills/cartog/scripts/ensure_indexed.sh`, `skills/cartog/scripts/update_on_exit.sh` (identified), `crates/cartog-mcp/src/tests/*.rs`, `crates/cartog-indexer/src/tests/*.rs`, `crates/cartog/tests/*.rs`, `skills/cartog/tests/*.sh` | Plugin hook and representative test surfaces inspected/identified. |

## Installation and integration behavior

- Cargo workspace builds multiple crates: CLI (`cartog`), MCP (`cartog-mcp`), indexer, DB, RAG, LSP, watcher, language extractors, process lock, and core schema.
- `crates/cartog/src/cli.rs` exposes `--json`, `--tokens`, `--compact`, and `--db` globally; subcommands cover index, outline, search, refs, callees, impact, trace, context, deps, map, changes, watch, init, install/ide, serve, and rag setup/index/search.
- `main.rs` resolves DB path from CLI/env/config/project root, enforces a consent gate before creating a fresh `.cartog/` index, warns on rejected configs, and dispatches `serve` into `cartog_mcp::run_server`.
- `skills/cartog/scripts/ensure_indexed.sh` is a Claude/plugin SessionStart hook: it surfaces prior background errors, checks binary drift, runs foreground incremental `cartog index .`, and backgrounds RAG setup/index tasks.
- IDE install paths and editor integration are present under `commands/ide`, `editors/vscode`, and plugin skills; full installer mutation review remains open.

## Runtime behavior

- `cartog index` walks source trees through `cartog-indexer`, filters candidates, detects language, reuses per-thread tree-sitter extractors, computes file/content/Merkle hashes, redacts configured fields, and writes changed symbols/edges/content to SQLite.
- Indexing is incremental by hash unless forced; parse jobs are clamped and pooled to avoid unbounded thread counts. Removed and changed files are tracked through DB lifecycle code.
- LSP resolution is optional and guarded: MCP indexing first runs tree-sitter indexing with LSP off, then performs a warm LSP pass that can reopen heuristic-exhausted edges, resolve targets, and re-seal when no server starts. Cancellation is surfaced as error; LSP failures degrade to warnings.
- DB query layer provides symbol search with literal escaping, prefix/substring ranking, centrality ordering, outline, refs, callees, impact traversal, trace, hierarchy, deps, map, stats, and changes.
- MCP server validates file/index paths stay under the canonical current working directory, uses mutexed DB/LSP/provider state, runs blocking work off the async runtime, returns structured content where possible, and logs tool queries for savings/stats.
- MCP tools include `cartog_index`, `cartog_rag_index`, `cartog_search`, `cartog_stats`, `cartog_map`, `cartog_changes`, graph navigation tools (`outline`, `refs`, `callees`, `impact`, `trace`, `hierarchy`, `deps`), `cartog_rag_search`, and `cartog_context`.
- RAG search uses hybrid FTS5/vector retrieval with optional reranking; it works keyword-only when embeddings are missing. Task context fuses semantic seeds, one-hop callers/callees, central definitions in seed files, deduplicates, ranks, and attaches bodies until a token budget is spent.

## Token-saving mechanism

- Main mechanism: answer source-understanding questions from a graph index and task-context bundles instead of reading/grepping many files.
- MCP compact mode is default (`CARTOG_MCP_COMPACT=0` disables it): docstrings/cache hashes are dropped from symbols, `rag_search` content is capped to 500-byte snippets, and large responses are byte-capped with narrowing hints.
- `cartog_context` is explicitly designed as a one-shot bundle for “how does X work?” tasks, including relevant bodies within a token budget (default 6000, max 20000) to avoid chains of search/ref/read calls.
- CLI also supports `--tokens` and `--compact` to bound non-MCP output.
- Savings may not translate to billed reductions if the index is stale, embeddings are missing for semantic queries, tool chains become longer than direct reads, or multiple code-retrieval authorities return overlapping context.

## Benchmarks and claims

| Claim area | Source inspected | Reviewed method | Caveats |
|---|---|---|---|
| Token-bounded MCP output and context bundling. | `cartog-mcp/src/lib.rs`, `tools/rag.rs`, `cartog-rag/src/context.rs`, `cartog-rag/src/search.rs`. | Source-logic; implementation paths inspected. | No provider-billed accounting or task-quality benchmark inspected. |
| Bench/fixture files exist. | `crates/cartog/benches/*.rs`, `crates/cartog-indexer/benches/indexing.rs`, `benchmarks/fixtures/*` paths identified. | Not benchmark-audit. | Do not treat as measured effectiveness evidence until harness/scoring/raw outputs are reviewed. |

## Compatibility notes

- Cartog should be treated as a local code retrieval/indexing authority. Avoid stacking it with another code-index MCP server over the same repo unless one has a narrow role or an ablation/reproduction shows benefits.
- It can coexist with a durable memory tool if memory is limited to historical decisions and Cartog owns current-source navigation.
- Watcher/SessionStart hooks and IDE install surfaces can conflict with other auto-indexers or hook managers.

## Failure modes and limits

- Initial indexing requires explicit consent/config unless `CARTOG_AUTO_INIT=1`; without an index, MCP can run degraded and read commands return empty/stateful warnings.
- Tree-sitter extractors and language coverage determine symbol/edge quality; dynamic dispatch and unresolved imports remain limits.
- LSP availability varies by language/project; failures degrade, so some edges may remain heuristic/unresolved.
- RAG vector quality depends on model setup and embedding index freshness; keyword-only fallback may miss conceptual matches.
- Local SQLite state, embeddings, and hook logs can leak code structure if used in sensitive repos without review.

## Open questions

- Which MCP tool list and defaults are exposed in a fresh installed plugin under each supported client?
- How often does `cartog_context` replace multi-tool file reading on target workloads without under-solving tasks?
- What languages and frameworks are mature enough for compatibility-safe use today?

## Next review tasks

- [ ] Inspect migration/schema tables and compact/byte-cap response code end-to-end.
- [ ] Run a sandbox indexing smoke test on a small repo and verify `cartog_context`, `refs`, and stale-index warnings.
- [ ] Audit benchmark harnesses only after locating task definitions, scoring, token accounting, and raw outputs.
