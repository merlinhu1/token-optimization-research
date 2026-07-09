# Tool dossier: manojmallick/sigmap

## Identity

- Repository: `manojmallick/sigmap`
- URL: https://github.com/manojmallick/sigmap
- Version/ref inspected: local shallow clone `569320994751`, 2026-07-01
- Snapshot status: pinned-commit
- Commit inspected: 569320994751935ab25bf4a9b5bd07aee99cc53b
- Commit URL: https://github.com/manojmallick/sigmap/commit/569320994751935ab25bf4a9b5bd07aee99cc53b
- Source artifact path: `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json`
- Date inspected: 2026-07-01
- Evidence stage: source-logic (fresh pinned shallow clone; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection: 530
- Forks at inspection: 37
- License: MIT
- Updated at: 2026-06-26T03:25:38Z

## Summary

SigMap extracts code signatures and exposes an MCP server with tools for context reads, signature search, maps, impact, routing, and session memory.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 499 files and 365 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `src/mcp/handlers.js`
- `src/mcp/install.js`
- `src/mcp/server.js`
- `src/mcp/tools.js`
- `src/retrieval/ranker.js`
- `src/retrieval/tokenizer.js`
- `src/graph/builder.js`
- `src/graph/impact.js`
- `src/session/memory.js`
- `src/session/notes.js`
- `benchmarks/R_LANGUAGE_BENCHMARKS.md`
- `benchmarks/R_LANGUAGE_SETUP.md`
- `benchmarks/latest.json`
- `benchmarks/llm-ablation-tasks.json`
- `benchmarks/reports/benchmark-matrix.json`
- `benchmarks/reports/quality.json`
- `benchmarks/reports/retrieval.json`
- `benchmarks/reports/task-benchmark.json`
- `benchmarks/reports/token-reduction.json`
- `benchmarks/reports/token-reduction.md`
- `benchmarks/task-metadata.json`
- `benchmarks/tasks/abseil-cpp.jsonl`
- `benchmarks/tasks/akka.jsonl`
- `benchmarks/tasks/axios.jsonl`
- `benchmarks/tasks/express.jsonl`
- `benchmarks/tasks/fastapi.jsonl`
- `benchmarks/tasks/fastify.jsonl`
- `benchmarks/tasks/flask.jsonl`
- `benchmarks/tasks/gin.jsonl`
- `benchmarks/tasks/laravel.jsonl`
- `benchmarks/tasks/okhttp.jsonl`
- `benchmarks/tasks/rails.jsonl`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`.

### Fresh pinned-source refresh

The 2026-07-01 refresh pins the inspected source to `569320994751935ab25bf4a9b5bd07aee99cc53b` and records a fresh tree plus selected implementation excerpts in `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` and `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`. Representative files captured for this refresh include `benchmarks/R_LANGUAGE_BENCHMARKS.md`, `benchmarks/R_LANGUAGE_SETUP.md`, `src/graph/builder.js`, `src/graph/impact.js`, `src/mcp/handlers.js`, `src/mcp/install.js`. Treat benchmark, savings, and deployment claims below as source-logic only unless a benchmark-audit or reproduction artifact is explicitly cited.


- `src/mcp/server.js` is a zero-dependency JSON-RPC line server that lists tools and dispatches calls over stdin/stdout.
- `src/mcp/tools.js` defines 17 MCP tools including context reads, signature search, impact, memory, diff context, and architecture overview.
- `src/retrieval/ranker.js` ranks files by keyword overlap, symbol matches, prefix/path matches, graph boosts, and learned weights.
- `src/graph/builder.js` builds forward/reverse dependency graphs for many language families from import/require patterns.
- `src/session/memory.js` stores short-lived coding-session context with a TTL for merge/read/clear workflows.

## Installation and integration behavior

- Tool: SigMap
- Primary intervention surface: Signature-map code retrieval, dependency graph, session memory, and MCP tools
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Signature-map code retrieval, dependency graph, session memory, and MCP tools
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Signature-map code retrieval, dependency graph, session memory, and MCP tools
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation is present.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes/state, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Code retrieval/signature authority plus light memory. It overlaps with CodeGraph, Serena, jcodemunch, CocoIndex Code, code-review-graph, and LeanCTX retrieval.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Signature extraction/ranking can miss dynamic behavior or unsupported language patterns.
- Session memory TTL and format may conflict with longer-lived memory systems.
- Benchmark claims require raw task/harness review before ranking.

## Open questions and next review tasks

- [ ] Inspect extraction dispatch and per-language parsers.
- [ ] Review benchmark reports/tasks and failure semantics.
- [ ] Compare retrieval output budgets against CodeGraph/Serena/jcodemunch.
