# Tool dossier: DietrichGebert/ponytail

## Identity

- Repository: `DietrichGebert/ponytail`
- URL: https://github.com/DietrichGebert/ponytail
- Version/ref inspected: local shallow clone `c4d1925ae9b7`, 2026-06-26
- Date inspected: 2026-06-26
- Evidence stage: source-logic (local shallow clone; representative runtime, instruction builder, mode tracker, activation hook, MCP server, tests, and benchmark judge inspected)

## Summary

Ponytail is an artifact/code-minimization ruleset distributed through multiple agent plugin formats. Source inspection confirms persistent mode state, instruction filtering by mode, activation hooks, an MCP prompt/tool server, behavior tests, and an LLM-judge benchmark harness for over-engineering.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository source tree | `sources/discovery/2026-06-26-source-logic-uplift-source-structures.json` | Local shallow clone tree used to identify source, hook, MCP, test, benchmark, and runtime paths. |
| Runtime/source content | `sources/discovery/2026-06-26-source-logic-uplift-code-inspection.json` | Representative implementation files read from local clone with byte counts, SHA-256 prefixes, and behavior excerpts. |
| README/docs | README/docs and skill files where present. | README claims remain discovery evidence; source findings below control this evidence stage. |
| Tests/benchmarks | Test and benchmark paths identified; representative tests inspected where listed. | Benchmark-method review remains benchmark-audit work. |

## Initial source-structure finding

Local tree inspection found 149 files and 88 files matching integration, source, test, benchmark, hook, MCP, or documentation patterns. Relevant paths include:

- `hooks/ponytail-instructions.js`
- `hooks/ponytail-mode-tracker.js`
- `hooks/copilot-hooks.json`
- `hooks/ponytail-activate.js`
- `hooks/ponytail-subagent.js`
- `hooks/ponytail-statusline.ps1`
- `hooks/ponytail-config.js`
- `hooks/claude-codex-hooks.json`
- `hooks/ponytail-runtime.js`
- `hooks/ponytail-statusline.sh`
- `ponytail-mcp/README.md`
- `ponytail-mcp/package.json`
- `ponytail-mcp/index.js`
- `ponytail-mcp/instructions.js`
- `ponytail-mcp/test/instructions.test.js`
- `tests/hooks.test.js`
- `tests/opencode-plugin.test.js`
- `tests/copilot-plugin.test.js`
- `tests/openclaw-skills.test.js`
- `tests/behavior.test.js`
- `tests/uninstall.test.js`
- `tests/correctness.test.js`
- `tests/hermes-plugin.test.js`
- `tests/gemini-extension.test.js`
- `tests/commands.test.js`
- `tests/hooks-windows.test.js`
- `benchmarks/promptfooconfig.gemini.yaml`
- `benchmarks/model-email.js`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-source-logic-uplift-code-inspection.json`.

- `hooks/ponytail-runtime.js` stores active mode in a `.ponytail-active` state file under Claude/Codex/Copilot plugin data directories and provides set/clear/read helpers.
- `hooks/ponytail-instructions.js` builds mode-specific instructions by loading the skill body and filtering tables/examples to the effective mode.
- `hooks/ponytail-mode-tracker.js` reads UserPromptSubmit JSON from stdin, detects `/ponytail` commands, and persists or clears mode state.
- `hooks/ponytail-activate.js` emits hidden SessionStart context or no-op output depending on configured/default mode and host behavior.
- `ponytail-mcp/index.js` exposes Ponytail over stdio as both an MCP prompt and `ponytail_instructions` tool for hosts that pull context via MCP.
- `ponytail-mcp/instructions.js` centralizes mode resolution so MCP output uses the same instruction builder as hooks/extensions.
- `tests/behavior.test.js` tests the benchmark behavior gate against known overbuild/minimality examples.
- `benchmarks/agentic/judge.py` defines an auditable LLM-judge rubric for over-engineering with fixed judge model, temperature 0, named constructs, and self-test gating.

## Installation and integration behavior

- Tool: Ponytail
- Primary intervention surface: Artifact and code-minimization policy layer with hook/plugin/MCP delivery paths
- Integration status: source and integration paths identified; source logic inspected for representative runtime files.
- Disable/uninstall path: partially inspected where representative files expose it; full host-by-host review remains open.
- Failure behavior if dependency is missing: partially inspected in representative code/tests; complete deployment failure-mode review remains open.

## Runtime behavior

- Intervention surface: Artifact and code-minimization policy layer with hook/plugin/MCP delivery paths
- Input captured: implementation-specific inputs are described in code-detail findings.
- Output emitted: implementation-specific outputs are described in code-detail findings.
- State/cache/files written: representative state and recovery behavior identified where present.
- Network/subprocess behavior: not exhaustively reviewed; benchmark/reproduction review remains required.
- Raw-output recovery path: recorded where present; otherwise open for benchmark-audit/reproduction review.
- Security/privacy considerations: host hooks, local state, indexes, memory, or runtime boundaries should be reviewed before sensitive deployment.

## Token-saving mechanism

- Addressable token surface: Artifact and code-minimization policy layer with hook/plugin/MCP delivery paths
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation exists.
- Quality-preservation mechanism: partially identified via guards, budgets, tests, profile controls, or explicit caveats where present.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, extra tool calls, stale indexes, skipped rewrites, duplicate context authorities, correction turns, or increased latency.

## Compatibility notes

Artifact/code-minimization policy owner. It can coexist with one terminal compactor, one retrieval authority, and one memory authority, but should not be combined casually with another behavior/artifact-policy controller such as Bonsai, Whippet, or aggressive terse-output rules without task-level evaluation.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- It changes implementation policy rather than compressing an input stream; poor fit can under-build or reduce explanation clarity.
- Mode state and hook activation vary by host/plugin data directory.
- Benchmark judge relies on an LLM and needs raw output/cost/pass-rate review before procurement claims.
- No reviewed benchmark covers combining Ponytail with a terse-output controller.

## Open questions and next review tasks

- [ ] Review plugin manifests and uninstall behavior across hosts.
- [ ] Inspect benchmark raw results and cost accounting.
- [ ] Benchmark with and without Ponytail on the same stack candidates.
