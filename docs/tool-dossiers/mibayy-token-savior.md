# Tool dossier: Mibayy/token-savior

## Identity

- Repository: `Mibayy/token-savior`
- URL: https://github.com/Mibayy/token-savior
- Version/ref inspected: `4.21.0` release at commit `1e5984b452c5b98e6376a7250b3213f5c3500626`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: 1e5984b452c5b98e6376a7250b3213f5c3500626
- Commit URL: https://github.com/Mibayy/token-savior/commit/1e5984b452c5b98e6376a7250b3213f5c3500626
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 4.21.0 release checkout from the batch release corpus, the same bytes its lanes install; representative MCP server, tool schemas, compact ops, bash rewriter, memory DB, query API, project indexer, and tests inspected)

## Summary

Token Savior is an integrated MCP/profile stack combining structural code navigation, project indexing, memory operations, compact summaries, and optional Bash command rewriting. Source inspection confirms server/tool schemas, compact change summaries, safety-oriented rewrite rules, memory DB façade, and retrieval/indexing APIs.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository source tree | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Local shallow clone tree used to identify source, hook, MCP, test, benchmark, and runtime paths. |
| Runtime/source content | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Representative implementation files read from local clone with byte counts, SHA-256 prefixes, and behavior excerpts. |
| README/docs | README/docs and skill files where present. | README claims remain discovery evidence; source findings below control this evidence stage. |
| Tests/benchmarks | Test and benchmark paths identified; representative tests inspected where listed. | Benchmark-method review remains benchmark-audit work. |

## Initial source-structure finding

Tree inspection of the pinned `4.21.0` release checkout found 444 files: 374 source, 19 documentation, 218 test/benchmark, and 67 matching installer, host-integration, hook, plugin, skill, MCP, or configuration patterns.

Integration code — what actually performs a host install, and therefore what an install protocol must be written against:

- `hooks/__init__.py`
- `hooks/bash_rewriter_hook.py`
- `hooks/openclaw/token-savior-memory/handler.js`
- `hooks/tool_capture_hook.py`
- `hooks/ts_discipline_guard.py`
- `scripts/deroot_hooks.py`
- `scripts/generer_bundles_hooks.py`
- `src/token_savior/__init__.py`
- `src/token_savior/bash_rewriter/__init__.py`
- `src/token_savior/cli_init/__init__.py`
- `src/token_savior/cli_init/agent_paths.py`
- `src/token_savior/cli_init/merger.py`
- `src/token_savior/cli_init/vocabulaire_clients.py`
- `src/token_savior/code_mode/__init__.py`
- `src/token_savior/compactors/__init__.py`
- `src/token_savior/config_analyzer.py`
- `src/token_savior/daemon_client.py`
- `src/token_savior/discover/__init__.py`
- `src/token_savior/memory/__init__.py`
- `src/token_savior/memory/ledger_hook.py`
- `src/token_savior/memory/precondition_hook.py`
- `src/token_savior/memory/preflight_hook.py`
- `src/token_savior/memory/rules_hook.py`
- `src/token_savior/server_handlers/__init__.py`
- `src/token_savior/utils/__init__.py`

Host-integration documentation shipped in the release:

- `AGENTS.md`
- `CLAUDE.md`
- `hooks/openclaw/token-savior-memory/HOOK.md`
- `llms-install.md`


## Code-detail inspection findings

### Pinned-release refresh (2026-08-28)

This dossier previously described `ff42ef14cc97`, read from GitHub HEAD on 2026-06-26. That is not the code any lane runs. `BATCH_RELEASES` pins this tool to the **4.21.0** release at `1e5984b452c5`, and the runner rewrites every lane path onto it, so the reading below is now taken from that pinned checkout instead. Inspecting the corpus checkout rather than a fresh network fetch keeps the reading reproducible after upstream HEAD moves again.

Upstream shipped **25 releases** between 2026-06-26 and this pin (`CHANGELOG.md`). A protocol derived from the older reading is how the 2026-08-22 review found five drifts and one blocking defect, so any integration step below is worth re-checking against the pinned release rather than trusted.

4 of those releases name an install surface in their own title:

- v4.18.1 — Two clients on one repository, now covered by tests (2026-07-26)
- v4.14.0 — The client tells us which projects are open (2026-07-26)
- v4.12.2 — `pip install token-savior-recall` produced a server that could not start (2026-07-26)
- v4.8.0 — Observations as MCP resources (2026-07-04)

The official install guide this tool is evaluated against is `source/README.md` at sha256 `e78f621c63cf9795…` in the pinned release.

Evidence artifact: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.

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
