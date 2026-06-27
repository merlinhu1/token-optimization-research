# Tool dossier: colbymchenry/codegraph

## Identity

- Repository: `colbymchenry/codegraph`
- URL: https://github.com/colbymchenry/codegraph
- Version/ref inspected: local shallow clone `4077ed19b7d8`, 2026-06-26
- Snapshot status: pinned-commit
- Commit inspected: 4077ed19b7d8
- Commit URL: https://github.com/colbymchenry/codegraph/commit/4077ed19b7d8
- Source artifact path: `sources/discovery/2026-06-26-source-logic-uplift-source-structures.json`
- Date inspected: 2026-06-26
- Evidence stage: source-logic (local shallow clone; representative CLI, context builder/formatter, search parser, DB queries, API, output-budget, and staleness tests inspected)

## Summary

CodeGraph builds a local code knowledge graph and provides task-oriented context construction, symbol/file search, graph traversal, and installer/daemon workflows. Source inspection confirms explicit context formatting, query parsing, output budgets, and staleness-signal tests.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository source tree | `sources/discovery/2026-06-26-source-logic-uplift-source-structures.json` | Local shallow clone tree used to identify source, hook, MCP, test, benchmark, and runtime paths. |
| Runtime/source content | `sources/discovery/2026-06-26-source-logic-uplift-code-inspection.json` | Representative implementation files read from local clone with byte counts, SHA-256 prefixes, and behavior excerpts. |
| README/docs | README/docs and skill files where present. | README claims remain discovery evidence; source findings below control this evidence stage. |
| Tests/benchmarks | Test and benchmark paths identified; representative tests inspected where listed. | Benchmark-method review remains benchmark-audit work. |

## Initial source-structure finding

Local tree inspection found 391 files and 350 files matching integration, source, test, benchmark, hook, MCP, or documentation patterns. Relevant paths include:

- `src/bin/uninstall.ts`
- `src/bin/codegraph.ts`
- `src/bin/fatal-handler.ts`
- `src/bin/node-version-check.ts`
- `src/context/formatter.ts`
- `src/context/markers.ts`
- `src/context/index.ts`
- `src/search/query-parser.ts`
- `src/search/query-utils.ts`
- `src/db/migrations.ts`
- `src/db/queries.ts`
- `src/db/schema.sql`
- `src/db/sqlite-adapter.ts`
- `src/db/index.ts`
- `src/index.ts`
- `telemetry-worker/src/index.ts`
- `__tests__/explore-synth-constant-endpoints.test.ts`
- `__tests__/explore-corroboration-ranking.test.ts`
- `__tests__/explore-blast-radius.test.ts`
- `__tests__/explore-output-budget.test.ts`
- `__tests__/mcp-files-path-normalization.test.ts`
- `__tests__/mcp-unindexed.test.ts`
- `__tests__/mcp-tool-allowlist.test.ts`
- `__tests__/mcp-catchup-gate.test.ts`
- `__tests__/mcp-roots.test.ts`
- `__tests__/mcp-initialize.test.ts`
- `__tests__/mcp-ppid-watchdog.test.ts`
- `__tests__/mcp-debounce-env.test.ts`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-source-logic-uplift-code-inspection.json`.

- `src/bin/codegraph.ts` exposes install, init, index, sync, status, query, files, context, callers, callees, and impact commands.
- `src/context/index.ts` builds task context by combining full-text search, graph traversal, query-derived symbols, path scoring, and relevance signals.
- `src/context/formatter.ts` formats task context as compact Markdown or JSON, prioritizing entry points and limiting code blocks to key symbols.
- `src/search/query-parser.ts` parses field-qualified queries such as kind/name/path/language filters and composes filters with free text.
- `src/db/queries.ts` implements prepared graph/search queries with path/value heuristics and result scoring.
- `src/index.ts` wires indexing, graph traversal, context builder, file watcher/sync, and project directory state into the public API.
- `__tests__/explore-output-budget.test.ts` pins adaptive output budgets so explore results remain under inline tool-result ceilings for small/medium/large projects.
- `__tests__/mcp-staleness-banner.test.ts` verifies MCP responses warn when referenced files or project files are pending index sync.

## Installation and integration behavior

- Tool: CodeGraph
- Primary intervention surface: Code retrieval and graph-indexing authority exposed through CLI/MCP-oriented workflows
- Integration status: source and integration paths identified; source logic inspected for representative runtime files.
- Disable/uninstall path: partially inspected where representative files expose it; full host-by-host review remains open.
- Failure behavior if dependency is missing: partially inspected in representative code/tests; complete deployment failure-mode review remains open.

## Runtime behavior

- Intervention surface: Code retrieval and graph-indexing authority exposed through CLI/MCP-oriented workflows
- Input captured: implementation-specific inputs are described in code-detail findings.
- Output emitted: implementation-specific outputs are described in code-detail findings.
- State/cache/files written: representative state and recovery behavior identified where present.
- Network/subprocess behavior: not exhaustively reviewed; benchmark/reproduction review remains required.
- Raw-output recovery path: recorded where present; otherwise open for benchmark-audit/reproduction review.
- Security/privacy considerations: host hooks, local state, indexes, memory, or runtime boundaries should be reviewed before sensitive deployment.

## Token-saving mechanism

- Addressable token surface: Code retrieval and graph-indexing authority exposed through CLI/MCP-oriented workflows
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation exists.
- Quality-preservation mechanism: partially identified via guards, budgets, tests, profile controls, or explicit caveats where present.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, extra tool calls, stale indexes, skipped rewrites, duplicate context authorities, correction turns, or increased latency.

## Compatibility notes

Code retrieval/indexing authority. It overlaps with Serena, SigMap, jcodemunch MCP, CocoIndex Code, Code Review Graph, LeanCTX retrieval, and Token Savior retrieval. Use one primary retrieval authority per stack.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Retrieval quality depends on index freshness, supported languages/framework extractors, and generated-file filtering.
- Daemon/watch state introduces stale-index and multi-repo boundary concerns.
- Output-budget tests constrain response size but do not prove task success or billed-token savings.
- benchmark-audit review of agent-eval scripts remains open.

## Open questions and next review tasks

- [ ] Review MCP tool schemas and daemon lifecycle more deeply.
- [ ] Run same-task retrieval comparisons against Serena, SigMap, jcodemunch, and LeanCTX.
- [ ] Inspect agent-eval benchmark raw outputs and scoring before ranking.
