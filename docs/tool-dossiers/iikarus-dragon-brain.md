# Tool dossier: iikarus/Dragon-Brain

## Identity

- Repository: `iikarus/Dragon-Brain`
- URL: https://github.com/iikarus/Dragon-Brain
- Local clone inspected: `/tmp/token-leads-20260629/iikarus__Dragon-Brain`
- Version/ref inspected: local shallow clone commit `8877153df6eb`
- Snapshot status: pinned-commit
- Commit inspected: 8877153df6eb
- Commit URL: https://github.com/iikarus/Dragon-Brain/commit/8877153df6eb
- Source artifact path: `sources/discovery/2026-06-29-graph-leads-c-source-logic.json`
- Date inspected: 2026-06-29
- Evidence stage: source-logic
- License observed in manifest: MIT

## Summary

Dragon-Brain is an MCP-exposed persistent memory service rather than a source-code indexer. Source logic shows a Python FastMCP server that manages entities, relationships, observations, sessions, temporal queries, graph traversal, hybrid memory search, and token-budgeted context selection using FalkorDB, Qdrant, embeddings, FTS, and reranking components.

## Evidence inventory

| Evidence type | Source file paths inspected | Notes |
|---|---|---|
| Manifest/entrypoints | `pyproject.toml` | Package scripts `dragon-brain` and `claude-memory` point to `claude_memory.server:main`; declares FalkorDB/Qdrant/MCP/embedding/Streamlit/FastAPI deps. |
| MCP server | `src/claude_memory/server.py` | FastMCP server registers create/update/delete/search/traversal/session/timeline/hologram/stats tools and launches stdio transport. |
| Service composition | `src/claude_memory/tools.py` | `MemoryService` composes CRUD, search, temporal, analysis, radar mixins; wires AsyncMemoryRepository, Qdrant vector store, OntologyManager, locks, router, activation, FTS, reranker. |
| Graph repository | `src/claude_memory/repository.py` | FalkorDB data-access layer for nodes/edges/raw Cypher with retry; production async path is referenced in `repository_async.py`. |
| Search behavior | `src/claude_memory/search.py` | Search/traversal mixin handles neighbors, shortest path, cross-domain patterns, evolution, point-in-time query, and snapshot diffs. |
| Vector store | `src/claude_memory/vector_store.py` | Async Qdrant collection setup, HNSW threshold, payload index, vector search, MMR, ID retrieval with cosine scoring. |
| Context budget | `src/claude_memory/context_manager.py` | Heuristic `len(text)//4` token estimator; includes full nodes until budget tight, then skeleton/truncated nodes. |
| Tests | `tests/unit/test_server.py` plus local test tree listing | Server tests patch external backends and verify MCP wrappers build params/delegate correctly. |

## Installation and integration behavior

- Python package exposes `dragon-brain` and `claude-memory` console scripts that invoke `claude_memory.server:main`.
- `server.py` eagerly instantiates `EmbeddingService`, `MemoryService`, `ClusteringService`, and `LibrarianAgent` at import time, then registers tools on a global `FastMCP("claude-memory")` instance.
- Runtime dependencies include FalkorDB for graph storage, Qdrant for vectors, sentence-transformers/embedding service, Redis lock paths, FTS store, reranker client, and optional FastAPI/Streamlit surfaces.
- `main()` configures logging, starts a fire-and-forget update check, then calls `mcp.run()` for stdio transport.

## Runtime behavior

- MCP tools convert call arguments into Pydantic parameter objects and delegate to `MemoryService` methods.
- Memory graph writes include entities, relationships, observations, sessions, breakthroughs, archive/prune operations, and extra temporal/librarian tools configured from `tools_extra`.
- Search paths combine graph traversal, vector retrieval, temporal filters, MMR, channel health metadata, reranking, and FTS-backed lexical search depending on selected strategy.
- Qdrant collection creation is lazy; created vectors are stored with payload, `name` text index, and cosine distance.
- Context optimization is a simple token-budget pass that truncates node descriptions when full content would exceed budget.

## Token-saving mechanism

- Primary mechanism: retrieve selected memory/graph nodes instead of replaying all historical project/session context into the prompt.
- Search mechanisms include semantic vector search, graph traversal, temporal filters, associative strategies, MMR diversity, FTS, and reranking; outputs can be constrained by `limit`, `offset`, strategy, and context-budget logic.
- Source logic supports persistence and retrieval, but this pass did not find automatic source-code indexing comparable to a code graph tool; token savings would come from remembered entity/session retrieval rather than codebase map replacement.

## Benchmarks and claims

- Manifest keywords/descriptions mention memory and evaluation claims, but README/manifest claims are not decision evidence.
- No benchmark artifact or raw provider-token accounting was inspected in this pass; status remains source-logic only.
- The inspected tests are implementation/unit checks, not effectiveness evidence for token reduction.

## Compatibility notes

- Dragon-Brain owns an agent-memory surface: graph memory, vector memory, session state, temporal recall, and librarian/cluster analysis.
- Compatibility-safe stacks should avoid giving another tool conflicting authority over persistent memory writes, vector collection schemas, graph entity semantics, or session summaries.
- It can coexist with a code graph indexer if ownership is split clearly: Dragon-Brain for durable project/session memory; code graph tool for source symbol/call retrieval.

## Failure modes and limits

- Startup/import path can depend on external services because global service objects are constructed at module import.
- Requires FalkorDB and Qdrant availability for the main graph/vector paths; search catches some infrastructure errors and returns degraded metadata, but write paths can fail hard.
- Context token accounting is approximate (`len/4`) and not provider-billed accounting.
- Update-check task may perform network work at startup.
- Not a direct code parser/indexer in inspected source; source-code token reduction would require another component or manual memory population.

## Open questions

- Which deployment path starts FalkorDB/Qdrant/Redis, and how are credentials managed in production?
- What data model conventions prevent memory drift, duplicate entities, or stale facts across long sessions?
- Are vector dimensions and embedding providers configurable enough for target agent environments?

## Next review tasks

- [ ] Inspect `repository_async.py`, `search_channels.py`, `router.py`, `reranker.py`, and CRUD mixins for deeper write/search semantics.
- [ ] Run a local degraded-startup smoke test with mocked or absent backends to confirm failure behavior.
- [ ] Map memory-write governance and deletion/archive behavior before combining with other memory tools.
- [ ] If effectiveness claims matter, separately inspect benchmark artifacts/raw outputs before any benchmark-audit wording.
