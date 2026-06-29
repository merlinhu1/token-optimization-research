# Tool dossier: STiFLeR7/memex

## Identity

- Repository: `STiFLeR7/memex`
- URL: https://github.com/STiFLeR7/memex
- Local clone inspected: `/tmp/token-leads-20260629/STiFLeR7__memex`
- Version/ref inspected: local shallow clone commit `cf9b1833ab41`
- Date inspected: 2026-06-29
- Evidence stage: source-logic
- License observed in manifest: MIT

## Summary

Memex is a Python MCP context-continuity system that watches repositories, extracts symbols and some call edges, writes structured and natural-language graph records through Graphiti/Neo4j, and serves compressed project/symbol/decision/problem/search briefings to coding agents. Source logic shows a broad memory-plus-code-context surface with explicit token budgets, temporal confidence, watcher/git-hook side effects, and Neo4j/Gemini dependencies.

## Evidence inventory

| Evidence type | Source file paths inspected | Notes |
|---|---|---|
| Manifest/entrypoints | `pyproject.toml`, `npm/bin/memex-mcp.js` | Python package `memex-mcp` with `memex` CLI; npm wrapper delegates to `uv tool run --from memex-mcp memex`. |
| MCP server | `memex/mcp_server/server.py` | Lists and dispatches read/write/context tools over stdio and optional HTTP; validates config and Neo4j connectivity at startup. |
| Read tools | `memex/mcp_server/tools_read.py` | Produces project context, symbol context, decisions/problems, stale context, composite search, and token-capped context briefing. |
| Query layer | `memex/mcp_server/queries.py` | Neo4j Cypher for counts, modules, decisions, problems, stale edges, symbols, callers/callees, clusters, access-count bump, composite search. |
| Graph writer | `memex/graph/writer.py` | Writes structured Symbol nodes and CALLS edges plus Graphiti episodes; writes Decision/Dependency nodes and post-hoc properties. |
| Schema/governance | `memex/graph/schema.py` | Pydantic node schemas and write-policy defaults for Symbol, Module, Decision, Problem, Session, Dependency, Repository, Cluster. |
| Parser/extractor | `memex/extractor/treesitter.py` | Extracts function/class symbols for several languages; Python-only call-expression extraction for call edges. |
| Watcher/daemon | `memex/watcher/daemon.py` | Installs git hooks, starts filesystem observer and commit poller, runs initial lockfile index and decay scheduler. |
| Tests | Local test tree listing including `tests/test_mcp_server.py`, `tests/test_mcp_queries.py`, `tests/test_graph_writer.py`, `tests/test_watcher_daemon.py`, `tests/test_context_briefing.py` | Tests were identified; representative implementation files above were the decision evidence for this source-logic pass. |

## Installation and integration behavior

- Python package exposes `memex = memex.cli:main`; npm wrapper requires `uv` and delegates all arguments to an isolated `uv tool run --from memex-mcp memex` execution.
- Dependencies include Graphiti with Google GenAI, Google Gemini client, tree-sitter language pack, watchdog, MCP, FastAPI/Uvicorn, APScheduler, Neo4j, Pydantic, Anthropic, Rich, and optional cluster/OTel extras.
- MCP server can run stdio, HTTP, or both; startup validates config and checks Neo4j unless `MEMEX_INTROSPECTION_ONLY=1` is set.
- Daemon mode writes `.memex/daemon.pid` or registry PID state, installs git hooks in watched repos, starts filesystem observers and commit pollers, and can watch a single repo or registry-listed repos.

## Runtime behavior

- Read tools return Markdown/text briefings, not raw graph dumps, for project context, symbol context, recent decisions, open problems, stale edges, broad search, predicted impact, and context briefing.
- Write tools record decisions/problems/resolutions and invalidate edges; schema source defines write policies where locked nodes are intended for watcher/cluster/summarizer and open nodes can be agent-written.
- Tree-sitter extraction produces `SymbolDelta` entries for added/modified/removed functions/classes; Python call extraction maps call sites to enclosing functions and emits `CallEdge` items.
- Graph writer persists structured Symbol nodes via Cypher `MERGE` before best-effort Graphiti natural-language episodes, so structured traversal can survive LLM/Graphiti episode failures.
- Context briefing assembles cluster summaries, high-confidence recent decisions, problems, and stale edges under a caller-provided token cap, truncating sections with an approximate `len/4` estimator.

## Token-saving mechanism

- Primary mechanism: precompute and retrieve compact graph-derived context instead of repeatedly scanning repository history/source and conversation state.
- Surfaces include `get_project_context`, `get_symbol_context`, `search_context`, `predict_impact`, and `get_context_briefing`; these collapse graph, decision, problem, cluster, and stale-edge data into bounded Markdown.
- Composite search increments access counts and applies recency/confidence/rehearsal scoring in source; context briefing explicitly stops/truncates at `max_tokens`.

## Benchmarks and claims

- README/package claims were not used as decision evidence.
- This pass inspected source and tests only; no benchmark-audit or reproduction evidence is promoted.
- Approximate token budgets in code are heuristic character-count controls, not provider-billed measurements.

## Compatibility notes

- Broad context owner: Memex overlaps with code graph, repository watcher, git hooks, memory, temporal graph, Graphiti/Neo4j, LLM summarization, MCP, HTTP server, and context-briefing surfaces.
- Compatibility-safe use requires deciding whether Memex or another tool owns repository watchers/git hooks, graph schema, memory writes, decision/problem nodes, and context-briefing authority.
- It may pair with a source-only graph tool if Memex is restricted to decisions/problems/session continuity, but overlapping symbol/call retrieval should be explicitly bounded.

## Failure modes and limits

- Requires Neo4j connectivity for normal MCP startup; Gemini/Graphiti failures can skip natural-language episodes, though structured Symbol writes are attempted first.
- Python call-edge extraction only is implemented in inspected source; symbols cover more extensions but call graph precision/recall differs by language.
- Watcher installs git hooks and writes `.memex`/registry state, adding repository side effects.
- Token accounting uses `len(text)//4`; not provider-billed accounting.
- Some query functions are documented as scaffolded/safe defaults until cluster/composite backing data exists.

## Open questions

- How are credentials and API quotas handled for Gemini/Graphiti in agent deployments?
- Which git hooks are installed and how cleanly are they removed?
- What is the observed false-positive/false-negative rate for symbol and Python call extraction on target repositories?

## Next review tasks

- [ ] Inspect `memex/cli.py`, `tools_write.py`, `git_hook.py`, `handlers.py`, and `graph/client.py` before any deployment recommendation.
- [ ] Run a local introspection-only MCP tool-list smoke test and a Neo4j-backed fixture if services are available.
- [ ] Map watcher side effects and uninstall/disable paths.
- [ ] Separately inspect any benchmark artifacts/raw outputs before effectiveness claims.
