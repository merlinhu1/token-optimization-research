# Tool dossier: Mibayy/token-savior

## Identity

- Repository: `Mibayy/token-savior`
- URL: https://github.com/Mibayy/token-savior
- Version/ref inspected: GitHub `HEAD` tree via API, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 2-integration (initial tree and integration-path review)

## Summary

Token Savior is an integrated MCP/profile stack combining code retrieval, memory, and command-output compaction. It should be treated as a stack owner rather than combined casually with overlapping retrieval or output tools.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| README/docs | README path identified; not sufficient as sole evidence. | README claims require source and benchmark follow-up. |
| Installer/config/plugin files | See initial source-structure finding below. | Integration review has started. |
| Runtime source | Identified for follow-up. | Not yet complete. |
| Tests | Test files identified for follow-up. | Not yet interpreted. |
| Benchmarks/evaluations | Benchmark files identified where present. | Methods and raw outputs require review. |

## Initial source-structure finding

GitHub recursive tree inspection found MCP/profile examples, hook configs, compactors, CLI init paths, and benchmark directories, including `docs/mcp_toolset.example.json`, `hooks/bash_rewriter_hook.py`, `hooks/tool_capture_hook.py`, `src/token_savior/cli_init/agent_paths.py`, `src/token_savior/compactors/`, `tests/test_cli_init.py`, and `tests/benchmarks/` result files.

## Compatibility notes

This dossier is not yet a deployment-grade recommendation. It records initial evidence needed for stack compatibility analysis. The tool should not be promoted beyond provisional status until the next review tasks are complete.

## Open questions and next review tasks

- [ ] Inspect MCP server handlers and tool schemas.
- [ ] Inspect bash rewriter fallback and raw-output capture behavior.
- [ ] Review benchmark task definitions and token accounting.
- [ ] Determine where memory and retrieval overlap with LeanCTX/Headroom.
