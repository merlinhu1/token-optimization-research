# Tool dossier: DietrichGebert/ponytail

## Identity

- Repository: `DietrichGebert/ponytail`
- URL: https://github.com/DietrichGebert/ponytail
- Version/ref inspected: GitHub `HEAD` tree via API, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 2-integration (initial tree and integration-path review)

## Summary

Ponytail is an artifact/code-minimization ruleset distributed through multiple agent plugin formats. It targets implementation scope and dependency restraint, not shell-output compaction or code retrieval.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| README/docs | README path identified; not sufficient as sole evidence. | README claims require source and benchmark follow-up. |
| Installer/config/plugin files | See initial source-structure finding below. | Integration review has started. |
| Runtime source | Identified for follow-up. | Not yet complete. |
| Tests | Test files identified for follow-up. | Not yet interpreted. |
| Benchmarks/evaluations | Benchmark files identified where present. | Methods and raw outputs require review. |

## Initial source-structure finding

GitHub recursive tree inspection found plugin manifests for Claude, Codex, Devin, GitHub Copilot, OpenCode, Pi, and generic agents, including `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.github/plugin/plugin.json`, `.opencode/plugins/ponytail.mjs`, `hooks/claude-codex-hooks.json`, `hooks/ponytail-activate.js`, and benchmark files under `benchmarks/` and `benchmarks/results/`.

## Compatibility notes

This dossier is not yet a deployment-grade recommendation. It records initial evidence needed for stack compatibility analysis. The tool should not be promoted beyond provisional status until the next review tasks are complete.

## Open questions and next review tasks

- [ ] Inspect hook activation and mode-tracking scripts.
- [ ] Inspect rules/instructions to identify safety exceptions and overconstraint risk.
- [ ] Review benchmark harness and raw result files.
- [ ] Compare with Bonsai, Whippet, Caveman, scrooge-mode, and concise using the same rubric.
