# Tool dossier: agentforce314/clawcodex

## Identity

- Repository: `agentforce314/clawcodex`
- URL: https://github.com/agentforce314/clawcodex
- Version/ref inspected: local shallow clone `31a1670fe33f`, 2026-07-01
- Snapshot status: pinned-commit
- Commit inspected: 31a1670fe33f4d8cbe23d22300a4e971b6420023
- Commit URL: https://github.com/agentforce314/clawcodex/commit/31a1670fe33f4d8cbe23d22300a4e971b6420023
- Source artifact path: `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json`
- Date inspected: 2026-07-01
- Evidence stage: source-logic (fresh pinned shallow clone; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection: 653
- Forks at inspection: None
- License: UNKNOWN-local-clone
- Updated at: local shallow clone 2026-06-26

## Summary

ClawCodex is a Python Claude Code-style coding agent/rebuild with token estimation, context/prefetch optimizations, compression pipeline tests, and cost tracking.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 1,422 files and 1,358 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `src/cost_tracker.py`
- `src/replLauncher.py`
- `src/secret_store.py`
- `src/init.py`
- `src/deferred_init.py`
- `src/token_estimation.py`
- `src/history.py`
- `src/costHook.py`
- `src/tasks_core.py`
- `src/cli.py`
- `src/__init__.py`
- `src/prefetch.py`
- `src/projectOnboardingState.py`
- `src/config.py`
- `src/task_registry.py`
- `tests/test_mcp_normalization.py`
- `tests/test_mcp_critic_blockers.py`
- `tests/test_compression_pipeline.py`
- `tests/test_mcp_transport.py`
- `tests/test_context_analyzer.py`
- `tests/test_mcp_client_full.py`
- `tests/test_cost_tracker_facade.py`
- `tests/test_mcp_string_utils.py`
- `tests/test_mcp_phase4_callback_and_provider.py`
- `tests/test_mcp_critic_majors.py`
- `tests/test_tool_registry_pipeline.py`
- `tests/test_memory_prefetch.py`
- `tests/test_tool_hooks.py`
- `tests/test_mcp_config_full.py`
- `tests/test_tool_list_parsing.py`
- `tests/test_cost_tracker_full.py`
- `tests/test_mcp_phase4_oauth_helpers.py`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`.

### Fresh pinned-source refresh

The 2026-07-01 refresh pins the inspected source to `31a1670fe33f4d8cbe23d22300a4e971b6420023` and records a fresh tree plus selected implementation excerpts in `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` and `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`. Representative files captured for this refresh include `src/__init__.py`, `src/cli.py`, `src/costHook.py`, `src/cost_tracker.py`, `src/deferred_init.py`, `src/history.py`. Treat benchmark, savings, and deployment claims below as source-logic only unless a benchmark-audit or reproduction artifact is explicitly cited.


- `src/token_estimation.py` implements rough and tiktoken-backed token counting plus memoization for repeated compaction/context-analysis calls.
- `src/history.py` stores session history events and renders them to Markdown.
- `src/prefetch.py` starts keychain/settings subprocess prefetch work early and drains cached handles later to overlap startup latency.
- `src/cost_tracker.py` centralizes API usage cost accumulation through shared bootstrap state and model pricing.
- `tests/test_compression_pipeline.py` exercises compression-pipeline orchestration, context collapse, auto-compact thresholds, and tool-result blocks.

## Installation and integration behavior

- Tool: ClawCodex
- Primary intervention surface: Replacement AI coding agent with token estimation, compaction pipeline, memory/history, and cost tracking
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Replacement AI coding agent with token estimation, compaction pipeline, memory/history, and cost tracking
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Replacement AI coding agent with token estimation, compaction pipeline, memory/history, and cost tracking
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation is present.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes/state, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Replacement-agent/runtime surface, not a small add-on. It should generally be evaluated as an alternative agent stack rather than combined with Claude Code/Codex hook-layer tools.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Large replacement-agent surface creates compatibility and trust-boundary risk.
- Token-saving claims combine many mechanisms and need task-level reproduction.
- Source tree includes extensive demos/wiki/tests; production runtime boundaries require deeper mapping.

## Open questions and next review tasks

- [ ] Inspect `src.services.compact` implementation files referenced by tests.
- [ ] Review tool execution, permission, MCP, and memory subsystems.
- [ ] Run independent task benchmark before ranking against add-on tool stacks.
