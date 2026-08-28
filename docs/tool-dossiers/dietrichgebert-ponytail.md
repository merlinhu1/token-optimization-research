# Tool dossier: DietrichGebert/ponytail

## Identity

- Repository: `DietrichGebert/ponytail`
- URL: https://github.com/DietrichGebert/ponytail
- Version/ref inspected: `4.9.0` release at commit `0a4dd63ad4541f4f655c4108a295916f3c1d8fda`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: 0a4dd63ad4541f4f655c4108a295916f3c1d8fda
- Commit URL: https://github.com/DietrichGebert/ponytail/commit/0a4dd63ad4541f4f655c4108a295916f3c1d8fda
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 4.9.0 release checkout from the batch release corpus, the same bytes its lanes install; representative runtime, instruction builder, mode tracker, activation hook, MCP server, tests, and benchmark judge inspected)

## Summary

Ponytail is an artifact/code-minimization ruleset distributed through multiple agent plugin formats. Source inspection confirms persistent mode state, instruction filtering by mode, activation hooks, an MCP prompt/tool server, behavior tests, and an LLM-judge benchmark harness for over-engineering.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository source tree | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Local shallow clone tree used to identify source, hook, MCP, test, benchmark, and runtime paths. |
| Runtime/source content | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Representative implementation files read from local clone with byte counts, SHA-256 prefixes, and behavior excerpts. |
| README/docs | README/docs and skill files where present. | README claims remain discovery evidence; source findings below control this evidence stage. |
| Tests/benchmarks | Test and benchmark paths identified; representative tests inspected where listed. | Benchmark-method review remains benchmark-audit work. |

## Initial source-structure finding

Tree inspection of the pinned `4.9.0` release checkout found 156 files: 51 source, 56 documentation, 55 test/benchmark, and 74 matching installer, host-integration, hook, plugin, skill, MCP, or configuration patterns.

Integration code — what actually performs a host install, and therefore what an install protocol must be written against:

- `.opencode/plugins/ponytail-frontmatter.cjs`
- `.opencode/plugins/ponytail.mjs`
- `__init__.py`
- `hooks/ponytail-activate.js`
- `hooks/ponytail-config.js`
- `hooks/ponytail-instructions.js`
- `hooks/ponytail-mode-tracker.js`
- `hooks/ponytail-runtime.js`
- `hooks/ponytail-subagent.js`
- `ponytail-mcp/index.js`
- `ponytail-mcp/instructions.js`
- `scripts/build-openclaw-skills.js`
- `scripts/publish-openclaw-skills.js`
- `scripts/uninstall.js`

Host-integration documentation shipped in the release:

- `.agents/rules/ponytail.md`
- `.openclaw/skills/ponytail-audit/SKILL.md`
- `.openclaw/skills/ponytail-debt/SKILL.md`
- `.openclaw/skills/ponytail-gain/SKILL.md`
- `.openclaw/skills/ponytail-help/SKILL.md`
- `.openclaw/skills/ponytail-review/SKILL.md`
- `.openclaw/skills/ponytail/SKILL.md`
- `.opencode/command/ponytail-audit.md`
- `.opencode/command/ponytail-debt.md`
- `.opencode/command/ponytail-gain.md`
- `.opencode/command/ponytail-help.md`
- `.opencode/command/ponytail-review.md`
- `.opencode/command/ponytail.md`
- `AGENTS.md`


## Code-detail inspection findings

### Pinned-release refresh (2026-08-28)

This dossier previously described `c4d1925ae9b7`, read from GitHub HEAD on 2026-06-26. That is not the code any lane runs. `BATCH_RELEASES` pins this tool to the **4.9.0** release at `0a4dd63ad454`, and the runner rewrites every lane path onto it, so the reading below is now taken from that pinned checkout instead. Inspecting the corpus checkout rather than a fresh network fetch keeps the reading reproducible after upstream HEAD moves again.

No release-by-release delta is available (release ships no changelog), so the gap between the audited commit and this pin is not enumerable from the release bytes alone.

The official install guide this tool is evaluated against is `source/README.md` at sha256 `743044a29ec74de5…` in the pinned release.

Evidence artifact: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.

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
