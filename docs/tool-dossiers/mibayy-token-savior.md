# Tool dossier: Mibayy/token-savior

## Identity

- Repository: `Mibayy/token-savior`
- URL: https://github.com/Mibayy/token-savior
- Version/ref inspected: local shallow clone `ff42ef14cc97`, 2026-06-26
- Date inspected: 2026-06-26
- Evidence stage: source-logic (local shallow clone; representative MCP server, tool schemas, compact ops, bash rewriter, memory DB, query API, project indexer, and tests inspected)

## Summary

Token Savior is an integrated MCP/profile stack combining structural code navigation, project indexing, memory operations, compact summaries, and optional Bash command rewriting. Source inspection confirms server/tool schemas, compact change summaries, safety-oriented rewrite rules, memory DB façade, and retrieval/indexing APIs.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository source tree | `sources/discovery/2026-06-26-source-logic-uplift-source-structures.json` | Local shallow clone tree used to identify source, hook, MCP, test, benchmark, and runtime paths. |
| Runtime/source content | `sources/discovery/2026-06-26-source-logic-uplift-code-inspection.json` | Representative implementation files read from local clone with byte counts, SHA-256 prefixes, and behavior excerpts. |
| README/docs | README/docs and skill files where present. | README claims remain discovery evidence; source findings below control this evidence stage. |
| Tests/benchmarks | Test and benchmark paths identified; representative tests inspected where listed. | Benchmark-method review remains benchmark-audit work. |

## Initial source-structure finding

Local tree inspection found 336 files and 319 files matching integration, source, test, benchmark, hook, MCP, or documentation patterns. Relevant paths include:

- `src/token_savior/server_state.py`
- `src/token_savior/server.py`
- `src/token_savior/server_runtime.py`
- `src/token_savior/tool_schemas.py`
- `src/token_savior/compact_ops.py`
- `hooks/bash_rewriter_hook.py`
- `tests/test_bash_rewriter.py`
- `src/token_savior/bash_rewriter/__init__.py`
- `src/token_savior/bash_rewriter/rules.py`
- `hooks/memory-precompact.sh`
- `hooks/memory-userprompt.sh`
- `hooks/memory-session-stop.sh`
- `hooks/memory-posttooluse.sh`
- `hooks/memory-pretooluse.sh`
- `hooks/memory-hooks-config.json`
- `hooks/memory-session-start.sh`
- `tests/test_memory_citation_uri.py`
- `tests/test_memory_auto_extract.py`
- `tests/test_memory_session_rollup.py`
- `tests/test_memory_public_surface.py`
- `tests/test_memory_vector_setup.py`
- `tests/test_memory_vector_indexation.py`
- `tests/test_memory_file_context.py`
- `tests/test_memory_hybrid_search.py`
- `tests/test_memory_db.py`
- `tests/test_memory_viewer.py`
- `tests/test_memory_narrative_fields.py`
- `scripts/migrate_memory_md.py`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-source-logic-uplift-code-inspection.json`.

- `src/token_savior/server.py` exposes project-wide structural query functions as MCP tools and documents tool-selection guidance that prefers symbol/context tools over raw search for many queries.
- `src/token_savior/tool_schemas.py` defines MCP tool schemas, profile filtering, project parameters, compressed-output toggles, and batch-mode limits.
- `src/token_savior/compact_ops.py` returns compact symbol-oriented summaries of worktree or ref-based changes with maximum file/symbol limits.
- `src/token_savior/bash_rewriter/rules.py` defines Bash rewrite safety gates, verbose-intent passthrough, and command-specific rewrite logic.
- `hooks/bash_rewriter_hook.py` implements a Claude Code PreToolUse hook that is off by default, rewrites Bash input only when enabled, and supports optional JSONL audit logging.
- `src/token_savior/memory_db.py` centralizes SQLite DB/session/migration access and re-exports higher-level memory budget/search/session APIs.
- `src/token_savior/query_api.py` provides structural navigation APIs over single-file and project-wide indexes.
- `src/token_savior/project_indexer.py` builds cross-file dependency/import graphs and a global symbol table while excluding VCS/cache/vendor/checkpoint paths.
- `tests/test_server_tools.py` validates profile-based tool exposure.
- `tests/test_bash_rewriter.py` checks unsafe-command passthrough, verbose-intent passthrough, unknown command passthrough, and concrete rewrites.

## Installation and integration behavior

- Tool: Token Savior
- Primary intervention surface: Integrated MCP owner for retrieval, memory, compact operations, and Bash command rewriting
- Integration status: source and integration paths identified; source logic inspected for representative runtime files.
- Disable/uninstall path: partially inspected where representative files expose it; full host-by-host review remains open.
- Failure behavior if dependency is missing: partially inspected in representative code/tests; complete deployment failure-mode review remains open.

## Runtime behavior

- Intervention surface: Integrated MCP owner for retrieval, memory, compact operations, and Bash command rewriting
- Input captured: implementation-specific inputs are described in code-detail findings.
- Output emitted: implementation-specific outputs are described in code-detail findings.
- State/cache/files written: representative state and recovery behavior identified where present.
- Network/subprocess behavior: not exhaustively reviewed; benchmark/reproduction review remains required.
- Raw-output recovery path: recorded where present; otherwise open for benchmark-audit/reproduction review.
- Security/privacy considerations: host hooks, local state, indexes, memory, or runtime boundaries should be reviewed before sensitive deployment.

## Token-saving mechanism

- Addressable token surface: Integrated MCP owner for retrieval, memory, compact operations, and Bash command rewriting
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation exists.
- Quality-preservation mechanism: partially identified via guards, budgets, tests, profile controls, or explicit caveats where present.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, extra tool calls, stale indexes, skipped rewrites, duplicate context authorities, correction turns, or increased latency.

## Compatibility notes

Integrated stack owner across retrieval, memory, and Bash compaction. Do not combine with separate retrieval engines, automatic memory injectors, or terminal compactors unless those surfaces are disabled or benchmarked together.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Because it owns multiple surfaces, partial adoption must be configured carefully to avoid duplicate retrieval/memory/terminal compaction.
- Bash rewriting is opt-in and skips unsafe/verbose/unknown commands, so savings vary by command mix.
- Project indexing quality depends on language annotators and exclusion rules.
- Benchmark artifacts exist but still need benchmark-audit review.

## Open questions and next review tasks

- [ ] Review server handler dispatch and profile subsets end to end.
- [ ] Inspect memory retention/redaction and vector setup paths.
- [ ] Review retrieval benchmark raw outputs and run stack-level reproduction.
