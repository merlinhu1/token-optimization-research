# Tool dossier: colbymchenry/codegraph

## Identity

- Repository: `colbymchenry/codegraph`
- URL: https://github.com/colbymchenry/codegraph
- Version/ref inspected: GitHub `HEAD` tree via API, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 2-integration (initial tree and integration-path review)

## Summary

CodeGraph is a local code retrieval and graph-indexing system exposed to agents through MCP and installer wiring. It targets source-code exploration rather than terminal-output compaction.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| README/docs | README path identified; not sufficient as sole evidence. | README claims require source and benchmark follow-up. |
| Installer/config/plugin files | See initial source-structure finding below. | Integration review has started. |
| Runtime source | Identified for follow-up. | Not yet complete. |
| Tests | Test files identified for follow-up. | Not yet interpreted. |
| Benchmarks/evaluations | Benchmark files identified where present. | Methods and raw outputs require review. |

## Initial source-structure finding

GitHub recursive tree inspection found installer and MCP-focused tests including `__tests__/installer.test.ts`, `__tests__/installer-targets.test.ts`, `__tests__/mcp-daemon.test.ts`, `__tests__/mcp-staleness-banner.test.ts`, `__tests__/mcp-tool-allowlist.test.ts`, `__tests__/explore-output-budget.test.ts`, `__tests__/context-ranking.test.ts`, and evaluation files under `__tests__/evaluation/`.

## Compatibility notes

This dossier is not yet a deployment-grade recommendation. It records initial evidence needed for stack compatibility analysis. The tool should not be promoted beyond provisional status until the next review tasks are complete.

## Open questions and next review tasks

- [ ] Inspect MCP tool schemas and output budgets.
- [ ] Inspect indexer and watcher staleness behavior.
- [ ] Review benchmark task definitions and scoring.
- [ ] Compare retrieval authority overlap with Serena and Token Savior.

