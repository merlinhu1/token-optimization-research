# Tool dossier: rtk-ai/rtk

## Identity

- Repository: `rtk-ai/rtk`
- URL: https://github.com/rtk-ai/rtk
- Version/ref inspected: GitHub `HEAD` tree via API, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 2-integration (initial tree and integration-path review)

## Summary

RTK is a shell and tool-output compaction layer for AI coding agents. It appears to integrate through agent-specific hooks, rules, and command wrappers rather than through a general prompt-only instruction.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| README/docs | README path identified; not sufficient as sole evidence. | README claims require source and benchmark follow-up. |
| Installer/config/plugin files | See initial source-structure finding below. | Integration review has started. |
| Runtime source | Identified for follow-up. | Not yet complete. |
| Tests | Test files identified for follow-up. | Not yet interpreted. |
| Benchmarks/evaluations | Benchmark files identified where present. | Methods and raw outputs require review. |

## Initial source-structure finding

GitHub recursive tree inspection found agent-specific hook/config directories including `hooks/claude/`, `hooks/codex/`, `hooks/hermes/`, `hooks/opencode/`, `hooks/copilot/`, `.github/hooks/rtk-rewrite.json`, `hooks/README.md`, `INSTALL.md`, and tests such as `hooks/claude/test-rtk-rewrite.sh` and `hooks/hermes/tests/test_rtk_rewrite_plugin.py`.

## Compatibility notes

This dossier is not yet a deployment-grade recommendation. It records initial evidence needed for stack compatibility analysis. The tool should not be promoted beyond provisional status until the next review tasks are complete.

## Open questions and next review tasks

- [ ] Inspect Rust command matcher/dispatcher and passthrough logic.
- [ ] Inspect hook rewrite behavior for Claude and Codex.
- [ ] Verify whether full raw output is recoverable after compaction.
- [ ] Review external tokbench counter-evidence and scope.
