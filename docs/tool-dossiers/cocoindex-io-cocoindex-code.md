# Tool dossier: cocoindex-io/cocoindex-code

## Identity

- Repository: `cocoindex-io/cocoindex-code`
- URL: https://github.com/cocoindex-io/cocoindex-code
- Version/ref inspected: GitHub `HEAD` tree and representative raw implementation files via API, 2026-06-26
- Date inspected: 2026-06-26
- Evidence stage: source-logic (representative implementation files inspected; benchmark/reproduction review remains open)
- Stars at inspection: 2,245
- Forks at inspection: 182
- License: Apache-2.0
- Updated at: 2026-06-26T03:56:46Z

## Summary

CocoIndex Code indexes code into chunks with embeddings and exposes semantic search plus local structural grep for agent code navigation.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-06-26-eight-more-tool-source-structures.json` | Used to identify installer, plugin, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime source | `sources/discovery/2026-06-26-eight-more-tool-code-inspection.json` | Representative implementation files fetched from GitHub HEAD with SHA-256 prefixes and behavior excerpts. |
| README/docs | README path identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 71 files and 48 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `src/cocoindex_code/__init__.py`
- `src/cocoindex_code/__main__.py`
- `src/cocoindex_code/_daemon_paths.py`
- `src/cocoindex_code/chunking.py`
- `src/cocoindex_code/cli.py`
- `src/cocoindex_code/client.py`
- `src/cocoindex_code/daemon.py`
- `src/cocoindex_code/embedder_defaults.py`
- `src/cocoindex_code/embedder_params.py`
- `src/cocoindex_code/file_walk.py`
- `src/cocoindex_code/grep.py`
- `src/cocoindex_code/indexer.py`
- `src/cocoindex_code/litellm_embedder.py`
- `src/cocoindex_code/project.py`
- `src/cocoindex_code/protocol.py`
- `src/cocoindex_code/query.py`
- `src/cocoindex_code/schema.py`
- `src/cocoindex_code/server.py`
- `src/cocoindex_code/settings.py`
- `src/cocoindex_code/shared.py`
- `tests/conftest.py`
- `tests/e2e_docker/__init__.py`
- `tests/e2e_docker/conftest.py`
- `tests/e2e_docker/test_docker_workspace.py`
- `tests/e2e_docker_fixtures/sample_project/README.md`
- `tests/e2e_docker_fixtures/sample_project/lib/utils.ts`
- `tests/e2e_docker_fixtures/sample_project/src/auth.py`
- `tests/e2e_docker_fixtures/sample_project/src/handlers.py`
- `tests/example_toml_chunker.py`
- `tests/test_backward_compat.py`
- `tests/test_chunker_registry.py`
- `tests/test_cli_helpers.py`
- `tests/test_client.py`
- `tests/test_daemon.py`
- `tests/test_e2e.py`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-eight-more-tool-code-inspection.json`.

- `src/cocoindex_code/indexer.py` defines the indexing flow using local filesystem and SQLite connectors, recursive splitting, language detection, chunk IDs, and vec0 table definitions.
- `src/cocoindex_code/server.py` implements a FastMCP server with typed models for code chunk search results and codebase understanding tools.
- `src/cocoindex_code/query.py` performs vector similarity search using sqlite-vec `vec0`, with KNN and fallback/full-scan query paths and language filtering.
- `src/cocoindex_code/chunking.py` exposes a public custom chunker registry API for language-specific chunking extensions.
- `src/cocoindex_code/grep.py` implements local structural code search without embeddings, daemon, or index, using code-match patterns over files.

## Installation and integration behavior

- Tool: CocoIndex Code
- Primary intervention surface: Embedded AST/vector code search CLI and MCP server
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative runtime files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Embedded AST/vector code search CLI and MCP server
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Embedded AST/vector code search CLI and MCP server
- Reduction method: implementation-level mechanism identified in representative source files.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Code retrieval/search authority. It overlaps with CodeGraph, Serena, claude-context, jcodemunch, and LeanCTX retrieval; its structural grep mode can be a narrower sidecar if not duplicating the primary retrieval engine.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Embedding/index setup affects semantic search availability.
- Custom chunkers can change result semantics and freshness.
- Claimed savings require benchmark review against agent tasks, not just search-result compactness.

## Open questions and next review tasks

- [ ] Inspect server tool schemas and result size controls.
- [ ] Review daemon lifecycle/index refresh tests.
- [ ] Benchmark semantic search and grep modes separately.
