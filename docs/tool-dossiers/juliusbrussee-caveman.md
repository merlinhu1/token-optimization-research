# Tool dossier: JuliusBrussee/caveman

## Identity

- Repository: `JuliusBrussee/caveman`
- URL: https://github.com/JuliusBrussee/caveman
- Version/ref inspected: `2.2.0` release at commit `9aa63945a349bef17206540650db48c30fafbdf2`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: 9aa63945a349bef17206540650db48c30fafbdf2
- Commit URL: https://github.com/JuliusBrussee/caveman/commit/9aa63945a349bef17206540650db48c30fafbdf2
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 2.2.0 release checkout from the batch release corpus, the same bytes its lanes install; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection (2026-07-01, not refreshed offline): 77,013
- Forks at inspection (2026-07-01, not refreshed offline): 4,360
- License: MIT
- Updated at (2026-07-01, not refreshed offline): 2026-06-26T07:42:50Z

## Summary

Caveman is a cross-agent terse-output skill/plugin. It primarily reduces assistant prose and related instruction/tool-description overhead rather than reducing code retrieval or shell output by itself.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Used to identify installer, plugin, MCP, test, and benchmark paths beyond README. |
| README/docs | README path identified when present. | README claims require source and benchmark follow-up. |
| Installer/config/plugin files | Paths identified below. | Integration review started. |
| Runtime source | Representative implementation files inspected; see code-detail section. | Source-logic review is recorded for representative modules; uninspected modules remain benchmark-audit/reproduction follow-up. |
| Tests/benchmarks | Representative tests or metrics files inspected where available. | Full benchmark-method review remains open. |

## Initial source-structure finding

Tree inspection of the pinned `2.2.0` release checkout found 1412 files: 888 source, 189 documentation, 634 test/benchmark, and 373 matching installer, host-integration, hook, plugin, skill, MCP, or configuration patterns.

Integration code — what actually performs a host install, and therefore what an install protocol must be written against:

- `agents/compile.mjs`
- `agents/delegate/caveman-delegate-mcp.mjs`
- `agents/delegate/portable-process.mjs`
- `agents/drift-report.mjs`
- `agents/probe-installed.mjs`
- `bin/install.js`
- `bin/lib/opencode-agent.js`
- `bin/lib/owned-install.js`
- `browse/bin/binary-installer.generated.mjs`
- `browse/scripts/copy-binary-installer.mjs`
- `cli/install.js`
- `engine/compressors/config.go`
- `extension/playwright.config.mjs`
- `mcp/bin/binary-installer.generated.mjs`
- `mcp/bin/caveman-mcp.mjs`
- `mcp/bin/release.generated.mjs`
- `mcp/cmd/caveman-mcp/main.go`
- `mcp/engine_tools.go`
- `mcp/protocol.go`
- `mcp/server.go`
- `packages/agent/src/adapters.ts`
- `packages/agent/src/breakers.ts`
- `packages/agent/src/budget.ts`
- `packages/agent/src/build.ts`
- `packages/agent/src/catalog.ts`
- `packages/agent/src/claude-runtime.ts`
- `packages/agent/src/claude.ts`
- `packages/agent/src/cli.ts`

Host-integration documentation shipped in the release:

- `AGENTS.md`
- `CLAUDE.md`
- `INSTALL.md`
- `agents/cavecrew-builder.md`
- `agents/cavecrew-investigator.md`
- `agents/cavecrew-reviewer.md`
- `agents/docs/AGENTS.md`
- `agents/docs/CLAUDE.md`
- `browse/CLAUDE.md`
- `cacheengine/CLAUDE.md`
- `commands/caveman-init.md`
- `docs/install-windows.md`
- `docs/plans/cavemem-multi-agent.md`
- `docs/technical/agent-wrapping.md`


## Code-detail inspection findings

### Pinned-release refresh (2026-08-28)

This dossier previously described `25d22f864ad6`, read from GitHub HEAD on 2026-07-01. That is not the code any lane runs. `BATCH_RELEASES` pins this tool to the **2.2.0** release at `9aa63945a349`, and the runner rewrites every lane path onto it, so the reading below is now taken from that pinned checkout instead. Inspecting the corpus checkout rather than a fresh network fetch keeps the reading reproducible after upstream HEAD moves again.

No release-by-release delta is available (release ships no changelog), so the gap between the audited commit and this pin is not enumerable from the release bytes alone.

The official install guide this tool is evaluated against is `source/INSTALL.md` at sha256 `3eac1c3f79c09a84…` in the pinned release.

Evidence artifact: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.


- SessionStart activation is implemented in `src/hooks/caveman-activate.js`. It checks mode state, handles `off`, independent modes such as `commit`, `review`, and `compress`, and emits a full caveman ruleset as hidden session context rather than relying only on a short instruction.
- `src/hooks/caveman-mode-tracker.js` is a `UserPromptSubmit` hook that parses user prompts for activation/deactivation and brevity phrases, then updates local mode state under the Claude config directory.
- `src/mcp-servers/caveman-shrink/index.js` is a wrapper around an upstream MCP command. It compresses description-like fields in `tools/list`, `prompts/list`, and `resources/list`, but explicitly avoids compressing `tools/call` response content because that is higher risk for downstream parsing.
- `src/mcp-servers/caveman-shrink/compress.js` uses regex-based prose compression with protected patterns for code-like tokens, URLs, paths, identifiers, and structured content.
- `tests/test_mcp_shrink.js` checks that filler/pleasantry removal happens while protected segments survive, giving some implementation-level evidence for the stated preservation boundary.

### Implementation-level limits

- The main token-saving mechanism is behavior/instruction and MCP-description compression, not deterministic reduction of all tool outputs.
- It writes/reads local mode state; stack compatibility must account for hooks that alter assistant behavior.
- Provider-billed savings still need benchmark review because terse output can change turn count or model behavior.

## Installation and integration behavior

- Tool type: Agent skill/plugin
- Primary intervention surface: Behavioral output compression and instruction/MCP-description compression
- Integration status: documented integration paths and/or source locations were identified, but exact runtime behavior has not yet been fully reviewed.
- Disable/uninstall path: requires follow-up inspection of installer/plugin code and documentation.
- Failure behavior if dependency is missing: partially inspected in representative files; complete deployment failure-mode review remains open.

## Runtime behavior

- Intervention surface: Behavioral output compression and instruction/MCP-description compression
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Behavioral output compression and instruction/MCP-description compression
- Reduction method: identified from representative implementation files; full benchmark/reproduction review remains open.
- Quality-preservation mechanism: partially identified from representative source where present; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: depends on turn count, prompt caching, failure/retry behavior, and whether the tool changes agent workflow length.

## Benchmarks and claims

| Claim | Source | Measurement scope | Reviewed method | Caveats |
|---|---|---|---|---|
| Token-saving or context-reduction claims exist or are implied by repository description/metadata. | Repository metadata, existing catalog records, and pinned source-logic refresh. | Varies by tool. | Reviewed at source-logic level through representative implementation files; not benchmark-audited or reproduced. | Maintainer claims must not be treated as reproduced evidence. |

## Compatibility notes

Compatible with terminal-output compactors and code retrieval tools when only one behavior/output-style controller is active. Conflicts with other terse-output controllers such as scrooge-mode or concise, and may be too aggressive when paired with another behavior-steering ruleset without a benchmark.

Compatibility-safe stack selection means the tools should not fight over the same hook, context surface, retrieval authority, memory authority, proxy, or output channel.

## Failure modes and limits

- Reduced prose can obscure reasoning, trade-offs, or warnings.
- Output-token savings may not reduce provider-billed totals if reasoning/tool turns increase.
- Agent-specific plugin behavior must be verified per host.

## Open questions and next review tasks

- [ ] Inspect activation and rules files for exact behavior changes.
- [ ] Review benchmark harness and raw outputs for token accounting scope.
- [ ] Compare against Ponytail, scrooge-mode, concise, and no behavior layer on identical tasks.
