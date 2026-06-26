# Tool dossier: tirth8205/code-review-graph

## Identity

- Repository: `tirth8205/code-review-graph`
- URL: https://github.com/tirth8205/code-review-graph
- Version/ref inspected: GitHub `HEAD` tree and representative raw implementation files via API, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 3-source-behavior (representative implementation files inspected; benchmark/reproduction review remains open)
- Stars at inspection: 18,917
- Forks at inspection: 2,030
- License: MIT
- Updated at: 2026-06-26T07:50:55Z

## Summary

Code Review Graph builds a local graph/index of code and changes so agents can request ranked, compact code-review context instead of reading whole files or broad diffs.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-06-26-eight-more-tool-source-structures.json` | Used to identify installer, plugin, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime source | `sources/discovery/2026-06-26-eight-more-tool-code-inspection.json` | Representative implementation files fetched from GitHub HEAD with SHA-256 prefixes and behavior excerpts. |
| README/docs | README path identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 287 files and 227 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `code_review_graph/context_savings.py`
- `code_review_graph/eval/__init__.py`
- `code_review_graph/eval/benchmarks/__init__.py`
- `code_review_graph/eval/benchmarks/agent_baseline.py`
- `code_review_graph/eval/benchmarks/build_performance.py`
- `code_review_graph/eval/benchmarks/flow_completeness.py`
- `code_review_graph/eval/benchmarks/impact_accuracy.py`
- `code_review_graph/eval/benchmarks/multi_hop_retrieval.py`
- `code_review_graph/eval/benchmarks/search_quality.py`
- `code_review_graph/eval/benchmarks/token_efficiency.py`
- `code_review_graph/eval/configs/code-review-graph.yaml`
- `code_review_graph/eval/configs/express.yaml`
- `code_review_graph/eval/configs/fastapi.yaml`
- `code_review_graph/eval/configs/flask.yaml`
- `code_review_graph/eval/configs/gin.yaml`
- `code_review_graph/eval/configs/httpx.yaml`
- `code_review_graph/eval/reporter.py`
- `code_review_graph/eval/runner.py`
- `code_review_graph/eval/scorer.py`
- `code_review_graph/eval/token_benchmark.py`
- `code_review_graph/graph.py`
- `code_review_graph/graph_diff.py`
- `code_review_graph/search.py`
- `code_review_graph/tools/context.py`
- `code-review-graph-vscode/src/backend/cli.ts`
- `code-review-graph-vscode/src/backend/sqlite.ts`
- `code-review-graph-vscode/src/backend/watcher.ts`
- `code-review-graph-vscode/src/extension.ts`
- `code-review-graph-vscode/src/features/blastRadius.ts`
- `code-review-graph-vscode/src/features/cursorResolver.ts`
- `code-review-graph-vscode/src/features/navigation.ts`
- `code-review-graph-vscode/src/features/reviewAssistant.ts`
- `code-review-graph-vscode/src/features/scmDecorations.ts`
- `code-review-graph-vscode/src/features/search.ts`
- `code-review-graph-vscode/src/onboarding/installer.ts`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-eight-more-tool-code-inspection.json`.

- `code_review_graph/graph.py` implements SQLite-backed node/edge storage with indexes for file path, kind, qualified names, and source/target edge queries.
- `code_review_graph/search.py` combines FTS5/BM25 and vector embeddings using reciprocal rank fusion, plus identifier extraction and kind/context boosting.
- `code_review_graph/context_savings.py` estimates context savings using file sizes and a character-per-token approximation, separating savings estimates from exact provider accounting.
- `code_review_graph/tools/context.py` exposes `get_minimal_context`, combining graph stats, communities, flows, risk, and next-tool suggestions into a compact response.
- `code_review_graph/eval/benchmarks/token_efficiency.py` compares naive full-file tokens, diff tokens, and graph-based context tokens, and excludes failed tool calls from aggregate measurements.

## Installation and integration behavior

- Tool: Code Review Graph
- Primary intervention surface: SQLite-backed code graph, hybrid search, and minimal review context assembly
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative runtime files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: SQLite-backed code graph, hybrid search, and minimal review context assembly
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: SQLite-backed code graph, hybrid search, and minimal review context assembly
- Reduction method: implementation-level mechanism identified in representative source files.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Code retrieval/review context authority. It overlaps with CodeGraph, Serena, jcodemunch, claude-context, Token Savior retrieval, and LeanCTX graph/read tools.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- SQLite and embedding index freshness determine retrieval reliability.
- Token-efficiency benchmarks use approximate token counting unless reproduced with provider usage.
- Review-context optimization may not generalize to non-review coding tasks.

## Open questions and next review tasks

- [ ] Inspect daemon/index invalidation and workspace watcher behavior.
- [ ] Review benchmark corpora and expected outputs.
- [ ] Compare retrieval quality against CodeGraph, Serena, and jcodemunch on same tasks.
