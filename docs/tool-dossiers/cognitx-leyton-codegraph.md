# Tool dossier: cognitx-leyton/codegraph

## Identity

- Repository: `cognitx-leyton/codegraph`
- URL: https://github.com/cognitx-leyton/codegraph
- Local clone inspected: `/tmp/token-leads-20260629/cognitx-leyton__codegraph`
- Version/ref inspected: local shallow clone `ba5e0039b24d`, 2026-06-29
- Date inspected: 2026-06-29
- Evidence stage: source-logic (local shallow clone; representative Python package manifest, CLI, MCP server, parser/resolver/loader, hooks, init, tests, and benchmark command wiring inspected)

## Summary

CognitX CodeGraph is a Python/Neo4j code-knowledge-graph system for TypeScript/TSX and optional Python parsing. Source inspection confirms a Typer CLI, Docker/Neo4j scaffolding, tree-sitter parsers, import/cross-file resolver, Neo4j loader with constraints/indexes, git hooks for incremental reindexing, and a FastMCP stdio server with read-oriented graph query tools plus gated write tools. Its token-saving path is graph queries over indexed architecture instead of broad source reading; it requires Neo4j and up-front indexing.

## Evidence inventory

| Evidence type | Files inspected | Notes |
|---|---|---|
| Manifest/entrypoints | `codegraph/pyproject.toml`, `codegraph/requirements.txt` (identified), `codegraph/docker-compose.yml` (identified) | Package installs `codegraph` CLI and `codegraph-mcp`; extras cover MCP, Python parser, watch, benchmark, docs, semantic/audio extraction. |
| CLI/runtime | `codegraph/codegraph/cli.py`, `codegraph/codegraph/init.py`, `codegraph/codegraph/config.py` (identified), `codegraph/codegraph/docker_setup.py` (identified), `codegraph/codegraph/hooks.py` | CLI commands for init/clone/index/query/wipe/stats/export/benchmark/hooks/install; init scaffolds Docker/commands/workflows. |
| MCP source | `codegraph/codegraph/mcp.py`, `codegraph/queries.md` (identified), `codegraph/tests/test_mcp.py` (identified) | FastMCP stdio server registers Cypher prompts and many query tools over Neo4j. |
| Parse/index/load source | `codegraph/codegraph/parser.py`, `codegraph/codegraph/py_parser.py`, `codegraph/codegraph/resolver.py`, `codegraph/codegraph/loader.py`, `codegraph/codegraph/schema.py` (identified), `codegraph/codegraph/ignore.py` (identified), `codegraph/codegraph/cache.py` (identified) | Tree-sitter TS/TSX/Python extraction, import resolution, node/edge schema, Neo4j constraints/indexes, and incremental hash/cache paths inspected/identified. |
| Tests/benchmark paths | `codegraph/tests/test_py_parser.py`, `codegraph/tests/test_mcp.py`, `codegraph/tests/test_benchmark.py`, `codegraph/codegraph/benchmark.py` (identified), `codegraph/tests/test_hooks.py` | Tests and benchmark command paths exist; benchmark method/raw outputs were not audited. |

## Installation and integration behavior

- `pyproject.toml` defines `cognitx-codegraph` with console scripts `codegraph = codegraph.cli:app` and `codegraph-mcp = codegraph.mcp:main`.
- Required runtime dependencies include tree-sitter TypeScript, Neo4j driver, Typer, Rich, and PyYAML. MCP, Python parsing, watcher, benchmark, analysis, docs, semantic, and transcribe features are optional extras.
- `codegraph init` detects a repo, writes templates such as `.claude/commands`, CI arch-check workflow, policy/config files, Docker compose, and optional CLAUDE.md snippet; it can start/reuse a shared `codegraph-neo4j` container and run first index.
- CLI install/uninstall/hook surfaces exist; `hooks.py` appends marked codegraph sections to git hooks while respecting `core.hooksPath` and preserving other hook content.
- Git hook snippets run `python -m codegraph.cli index . --since ... --json` after commit/checkout and try to locate a safe Python interpreter that can import `codegraph`.

## Runtime behavior

- `cli.py` defaults to an interactive REPL with no subcommand; explicit commands include init, clone, index, validate, arch-check, audit, query, wipe, stats, export, and benchmark.
- `index` connects to Neo4j, parses configured packages, optionally runs incremental modes (`--since` via `git diff --name-status`, or `--update` via SHA256 cache), writes graph data, then auto-exports HTML/JSON, auto-runs benchmark command wiring, and auto-generates analysis/report unless suppressed.
- `TsParser` uses tree-sitter TypeScript/TSX and extracts files, classes, functions, interfaces, NestJS decorators/controllers/endpoints, TypeORM columns, GraphQL operations, React hooks/components, REST URLs, and framework-specific flags.
- `PyParser` is optional; it extracts Python files/classes/functions/methods/imports/decorators/routes at a staged level and raises a clear error if `tree-sitter-python` is not installed.
- `resolver.py` resolves TypeScript paths, NodeNext `.js` imports back to TS sources, workspace/barrel/alias imports, and Python package layouts, then links cross-file edges.
- `loader.py` initializes Neo4j uniqueness constraints and property indexes, wipes or scoped-wipes graph data, and batches MERGE operations for File/Class/Function/Method/Interface/Endpoint/GraphQL/Hook/Document/Concept/Decision and relationship nodes/edges.
- `mcp.py` creates a FastMCP server, lazily opens a Neo4j driver, registers Cypher snippets from `queries.md` as prompts, validates interpolated `limit`/`max_depth` values, and uses read-only sessions for read tools.
- MCP tools include raw read-only `query_graph`, schema/package listing, class/function finders, callers/callees, controller endpoints, package files, hook usage, GraphQL callers, injected-service rankings, and edge-group descriptions. Write tools are gated by `--allow-write` according to module comments.

## Token-saving mechanism

- Main mechanism: map framework-aware source structure into Neo4j and let agents answer architecture questions through focused Cypher/MCP tools instead of reading many files.
- `describe_schema` and named MCP tools guide agents toward structured queries with bounded `limit` values rather than ad hoc file scans.
- CLI JSON output and HTML/JSON export provide machine-readable graph surfaces; benchmark command wiring suggests intended token-reduction evaluation, but effectiveness was not audited.
- Savings may not translate if Neo4j is unavailable, graph indexes are stale, parser coverage misses relevant language constructs, raw `query_graph` returns too broad a result, or setup/indexing/benchmark side effects add extra turns.

## Benchmarks and claims

| Claim area | Source inspected | Reviewed method | Caveats |
|---|---|---|---|
| Token-reduction benchmark command/wiring exists. | `cli.py` benchmark command and auto-benchmark calls; `pyproject.toml` benchmark extra; test path identified. | Source-logic only. | `benchmark.py`, tasks, token accounting, and raw outputs were not inspected, so no benchmark-audit claim. |
| Graph query safety and read-only MCP behavior. | `mcp.py` read sessions, validation helpers, comments, and tool implementations. | Source-logic. | Needs live Neo4j verification to confirm driver/database permissions in deployment. |

## Compatibility notes

- CodeGraph is a heavy local graph authority backed by Neo4j. It overlaps with Cartog, Serena, LeanCTX, and other code-index MCP servers; choose one as primary for live source retrieval unless benchmarked together.
- It can pair with external memory/history tools if CodeGraph owns current source architecture and memory owns durable decisions.
- Docker/Neo4j ports (`7688`, `7475`) and git hooks may conflict with existing developer infrastructure.

## Failure modes and limits

- Requires a running Neo4j service for most useful operations; default connection is `bolt://localhost:7688` with default credentials unless overridden.
- Indexing can mutate/wipe graph data (`wipe=True` default for full index) unless incremental/no-wipe modes are chosen correctly.
- Parser maturity differs by language: TS/TSX is primary; Python parser labels itself staged/minimum viable with several out-of-scope items in comments.
- Raw `query_graph` accepts arbitrary Cypher but uses read-only sessions; bad queries still return errors and overly broad read queries may produce large outputs up to validated limits.
- Auto-export, auto-benchmark, and auto-analysis after indexing can add time/side effects unless suppressed.
- Hook-installed background reindexing may fail silently or block depending on git hook context and local Python/package environment.

## Open questions

- Which MCP write tools exist below the inspected section and exactly how `--allow-write` gates them?
- What are realistic graph sizes and MCP result sizes for target repos?
- Does staged Python support cover the token-research workloads, or should this be TS/Nest/React scoped?

## Next review tasks

- [ ] Inspect `benchmark.py`, `tests/test_benchmark.py`, and any raw `codegraph-out/benchmark.json` only if advancing to benchmark-audit.
- [ ] Run a sandbox Neo4j/index smoke test and verify MCP read-only query behavior.
- [ ] Inspect install/uninstall command implementations and MCP write-tool gating end-to-end.
