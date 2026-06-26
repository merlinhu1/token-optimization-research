# Tool dossier: zilliztech/claude-context

## Identity

- Repository: `zilliztech/claude-context`
- URL: https://github.com/zilliztech/claude-context
- Version/ref inspected: GitHub `HEAD` tree and representative raw implementation files via API, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 3-source-behavior (representative implementation files inspected; benchmark/reproduction review remains open)
- Stars at inspection: 11,966
- Forks at inspection: 891
- License: MIT
- Updated at: 2026-06-26T06:16:51Z

## Summary

Claude Context indexes a codebase into code chunks and exposes MCP tools for semantic code search/sync, aiming to replace broad file reads with retrieved code context.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-06-26-eight-more-tool-source-structures.json` | Used to identify installer, plugin, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime source | `sources/discovery/2026-06-26-eight-more-tool-code-inspection.json` | Representative implementation files fetched from GitHub HEAD with SHA-256 prefixes and behavior excerpts. |
| README/docs | README path identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 177 files and 142 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `packages/core/src/context.abort.test.ts`
- `packages/core/src/context.embedding-error.test.ts`
- `packages/core/src/context.ignore-patterns.test.ts`
- `packages/core/src/context.splitter.test.ts`
- `packages/core/src/context.ts`
- `packages/core/src/embedding/base-embedding.ts`
- `packages/core/src/embedding/gemini-embedding.test.ts`
- `packages/core/src/embedding/gemini-embedding.ts`
- `packages/core/src/embedding/index.ts`
- `packages/core/src/embedding/ollama-embedding.ts`
- `packages/core/src/embedding/openai-embedding.ts`
- `packages/core/src/embedding/voyageai-embedding.test.ts`
- `packages/core/src/embedding/voyageai-embedding.ts`
- `packages/core/src/index.ts`
- `packages/core/src/splitter/ast-splitter.ts`
- `packages/core/src/splitter/index.ts`
- `packages/core/src/splitter/langchain-splitter.ts`
- `packages/core/src/sync/merkle.ts`
- `packages/core/src/sync/synchronizer.ts`
- `packages/core/src/types.ts`
- `packages/core/src/utils/env-manager.ts`
- `packages/core/src/utils/ignore-matcher.ts`
- `packages/core/src/utils/index.ts`
- `packages/core/src/vectordb/index.ts`
- `packages/core/src/vectordb/milvus-restful-vectordb.ts`
- `packages/core/src/vectordb/milvus-vectordb.ts`
- `packages/core/src/vectordb/types.ts`
- `packages/core/src/vectordb/zilliz-utils.ts`
- `packages/mcp/src/config.ts`
- `packages/mcp/src/embedding.ts`
- `packages/mcp/src/handlers.get-indexing-status.test.ts`
- `packages/mcp/src/handlers.ts`
- `packages/mcp/src/index.ts`
- `packages/mcp/src/snapshot.request-options.test.ts`
- `packages/mcp/src/snapshot.ts`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-eight-more-tool-code-inspection.json`.

- `packages/core/src/context.ts` implements indexing/search context and defines `IndexAbortError` for cancelling in-flight indexing.
- `packages/core/src/splitter/ast-splitter.ts` chunks code through tree-sitter AST nodes, with LangChain fallback and chunk-size/overlap controls.
- `packages/core/src/vectordb/milvus-vectordb.ts` manages Milvus/Zilliz vector database connections, schema fields, search options, and hybrid search behavior.
- `packages/mcp/src/handlers.ts` exposes MCP tool handlers and tracks active background indexing tasks so `clear_index` can cancel/await ongoing indexing before dropping collections.
- `packages/mcp/src/sync.ts` implements background sync controls, sync lock staleness, and file synchronizer integration.

## Installation and integration behavior

- Tool: Claude Context
- Primary intervention surface: MCP semantic code search backed by AST splitting, embeddings, and Milvus/Zilliz vector database
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative runtime files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: MCP semantic code search backed by AST splitting, embeddings, and Milvus/Zilliz vector database
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: MCP semantic code search backed by AST splitting, embeddings, and Milvus/Zilliz vector database
- Reduction method: implementation-level mechanism identified in representative source files.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Semantic code retrieval authority. It overlaps with CodeGraph, Serena, code-review-graph, jcodemunch, CocoIndex Code, and LeanCTX retrieval.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Requires vector database and embedding setup; operational complexity is higher than local grep/tree tools.
- Chunking/search quality depends on language parsing, embeddings, and collection freshness.
- Hybrid search performance and provider-billed savings require benchmark review.

## Open questions and next review tasks

- [ ] Inspect MCP handler schemas and default search result budgets.
- [ ] Review evaluation case studies and raw conversation logs.
- [ ] Test vector DB failure modes and index-clear/sync race behavior.

