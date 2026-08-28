# Tool dossier: safishamsi/graphify

## Identity

- Repository: `safishamsi/graphify`
- URL: https://github.com/safishamsi/graphify
- Version/ref inspected: `0.9.48` release at commit `b2cd36267456c166788c95be6e68574064a92a42`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: b2cd36267456c166788c95be6e68574064a92a42
- Commit URL: https://github.com/safishamsi/graphify/commit/b2cd36267456c166788c95be6e68574064a92a42
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 0.9.48 release checkout from the batch release corpus, the same bytes its lanes install; CLI, installer, extraction, graph build/query, MCP server, hooks, and representative tests)
- License: package metadata points to `LICENSE`

## Summary

Graphify is a Python CLI/skill package that builds `graphify-out/graph.json` from source/document corpora, installs host-specific agent skills/instructions, serves graph queries over MCP, and can keep graphs fresh via git hooks/watch/update paths. Source inspection supports a source-logic finding for mechanism and integration behavior, not measured token savings.

## Evidence inventory

| Evidence type | Files inspected | Notes |
|---|---|---|
| Manifest/entrypoints | `pyproject.toml`, `graphify/__main__.py` | `graphify` and `graphify-mcp` console scripts; optional extras for MCP, watch, DB, provider, document/video support. |
| Extraction/build logic | `graphify/extract.py`, `graphify/build.py` | Tree-sitter/manifest/MCP/package extraction, ID normalization, dedupe, NetworkX graph assembly. |
| Query/MCP runtime | `graphify/serve.py` | Loads graph JSON with size checks; scores query terms, IDF/trigram candidate generation, BFS/DFS, context filters. |
| Hooks/integration | `graphify/hooks.py`, `graphify/__main__.py` | Skill install paths for many hosts; git post-commit/post-checkout hook launcher and rebuild path. |
| Tests | `tests/test_query_cli.py`, `tests/test_serve.py`, `tests/test_hooks.py`, `tests/test_extract.py` | Representative tests pin query context filters, graph size rejection, MCP helper scoring/traversal, hook install/uninstall, and extractor ID/edge behavior. |

## Installation and integration behavior

- `pyproject.toml` publishes package `graphifyy` with scripts `graphify = graphify.__main__:main` and `graphify-mcp = graphify.serve:_main`.
- CLI install code writes host-specific skill files and always-on instruction blocks for Claude, Codex, OpenCode, Kilo, Gemini, VS Code, Hermes, Kiro, Pi, Devin, and others.
- Project/global skill destinations are computed per host; references sidecars are installed atomically and `.graphify_version` stamps are refreshed.
- Git hook integration writes marked `post-commit` and `post-checkout` sections; hook payload locates a Python able to import graphify, then calls `graphify.watch._rebuild_code` with timeout/resource guards.
- Uninstall paths exist for skill files, always-on sections, platform hooks/plugins, and git hooks; user/project scope is distinct in installer code.

## Runtime behavior

- `extract.py` dispatches deterministic AST extraction via tree-sitter-backed extractors plus manifest/MCP config ingestion, with `_safe_extract` converting per-file failures into warnings and empty results.
- `build.py` validates extractions, normalizes source paths/IDs, remaps older semantic IDs, deduplicates nodes/edges, and writes graph structures through NetworkX.
- `serve.py` loads `.json` graph files only, enforces a graph file size cap, converts `edges` to `links` when needed, warns on legacy node IDs, then supports query scoring and graph traversal.
- CLI query paths support explicit/heuristic context filters and a token/output budget argument; tests verify call/import filtering and oversized graph rejection.
- Hooks can rebuild in the background after commits/checkouts, which improves freshness but also creates state/process behavior outside a single agent turn.

## Token-saving mechanism

- Addressable token surface: code/document context retrieval for agents that would otherwise paste or read broad files.
- Reduction method: graph extraction turns a corpus into nodes/edges; query/MCP/CLI paths return scored/traversed subgraphs instead of full-corpus text; skill references use progressive disclosure sidecars for host instructions.
- Quality-preservation mechanisms seen in source: extracted/inferred confidence fields, source file/location fields, query context filters, graph file caps, ID normalization/dedupe, and tests for query selection and extractor graph integrity.
- Cases where savings may not translate to billed reductions: rebuild overhead, LLM-backed semantic extraction/labeling, stale or oversized graphs, extra tool turns, duplicate retrieval authorities, and provider prompt-cache effects.

## Benchmarks and claims

No benchmark-audit was performed. `graphify benchmark` is advertised in CLI help and benchmark files exist in the tree, but benchmark harness/raw outputs/method were not inspected for this dossier. Treat token-reduction claims as unmeasured until benchmark artifacts are reviewed.

## Compatibility notes

Graphify is a code/document graph retrieval and host-instruction authority. In a compatibility-safe stack, avoid running it as a second primary code graph beside Serena, CodeGraph, SwarmVault graph retrieval, MaestroGraph, or LeanCTX unless a benchmark-audit/reproduction shows complementary rather than duplicate context.

## Failure modes and limits

- Extraction depends on supported tree-sitter grammars and per-language resolver quality.
- Optional dependencies gate MCP, watch, DB, document/video, provider, and semantic-labeling features.
- Hooks can silently skip if no importable graphify Python is found; source code prints diagnostics but exits non-fatally in some locator failure cases.
- Local graph freshness is a continuing concern; manual update/rebuild may be needed after edits.
- MCP/query quality depends on graph size, node labels, normalized IDs, and relation/context annotations.

## Open questions

- Which optional extras are required for the target agent stack?
- How much graph rebuild/LLM extraction overhead is incurred on representative repositories?
- Are git hooks acceptable in the intended deployment/security model?

## Next review tasks

- [ ] Inspect `graphify/benchmark.py` and raw benchmark artifacts before citing any measured token reduction.
- [ ] Run graphify on a fixed target workload and compare provider-billed usage against a no-graph baseline.
- [ ] Review full MCP tool schema and host install/uninstall paths for the specific platform under consideration.
