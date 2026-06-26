# Tool dossier: mksglu/context-mode

## Identity

- Repository: `mksglu/context-mode`
- URL: https://github.com/mksglu/context-mode
- Version/ref inspected: GitHub `HEAD` tree via API, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 3-source-behavior (representative server, hooks, persistence, hook-config, and routing tests inspected)
- Stars at inspection: 18,195
- Forks at inspection: 1,277
- License: NOASSERTION
- Updated at: 2026-06-26T07:35:50Z

## Summary

Context-Mode moves large intermediate tool/MCP workflows outside the primary model context and returns selected results. It targets a different surface from code retrieval, but overlaps with output/offload compressors.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-06-26-five-more-tool-source-structures.json` | Used to identify installer, plugin, MCP, test, and benchmark paths beyond README. |
| README/docs | README path identified when present. | README claims require source and benchmark follow-up. |
| Installer/config/plugin files | Paths identified below. | Integration review started. |
| Runtime source | Representative implementation files inspected; see code-detail section. | Source-behavior review has started and should continue across remaining modules. |
| Tests/benchmarks | Representative tests or metrics files inspected where available. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 572 files and 501 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `.agents/plugins/marketplace.json`
- `.claude-plugin/marketplace.json`
- `.claude-plugin/plugin.json`
- `.claude/skills/context-mode-ops/SKILL.md`
- `.claude/skills/context-mode-ops/agent-teams.md`
- `.claude/skills/context-mode-ops/communication.md`
- `.claude/skills/context-mode-ops/marketing.md`
- `.claude/skills/context-mode-ops/release.md`
- `.claude/skills/context-mode-ops/review-pr.md`
- `.claude/skills/context-mode-ops/tdd.md`
- `.claude/skills/context-mode-ops/triage-issue.md`
- `.claude/skills/context-mode-ops/validation.md`
- `.codex-plugin/hooks.json`
- `.codex-plugin/mcp.json`
- `.codex-plugin/plugin.json`
- `.cursor-plugin/README.md`
- `.cursor-plugin/assets/logo.png`
- `.cursor-plugin/plugin.json`
- `.mcp.json.codex.example`
- `.mcp.json.example`
- `.openclaw-plugin/index.ts`
- `.openclaw-plugin/openclaw.plugin.json`
- `.openclaw-plugin/package.json`
- `.pi/extensions/context-mode/package.json`
- `.pi/extensions/context-mode/tsconfig.json`
- `BENCHMARK.md`
- `configs/antigravity-cli/hooks.json`
- `configs/antigravity-cli/hooks/hooks.json`
- `configs/antigravity-cli/mcp_config.json`
- `configs/antigravity-cli/plugin.json`
- `configs/antigravity-cli/rules/context-mode.md`
- `configs/antigravity-cli/skills/context-mode/SKILL.md`
- `configs/antigravity/GEMINI.md`
- `configs/antigravity/mcp_config.json`
- `configs/claude-code/CLAUDE.md`
- `configs/codex/AGENTS.md`
- `configs/codex/config.toml`
- `configs/codex/hooks.json`
- `configs/copilot-cli/.github/plugin/plugin.json`
- `configs/copilot-cli/.mcp.json`



## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-five-more-tool-code-inspection.json`. The artifact contains raw GitHub file paths, byte sizes, SHA-256 prefixes, and behavior-line excerpts from the inspected implementation files.

- `src/server.ts` is a large MCP server integrating file-system access, subprocess execution, `PolyglotExecutor`, fetch cache, search schemas, session statistics, hook configuration, and result tracking.
- `src/adapters/codex/hooks.ts` defines Codex hook event integration, including `PreToolUse`, `PostToolUse`, `PreCompact`, `SessionStart`, `SessionEnd`, and `Stop`, and routes external MCP tools through a matcher/body filter strategy.
- `src/session/persist-tool-calls.ts` persists per-tool call counts and returned byte counts into SessionDB on a best-effort basis so counters do not break parent tool calls.
- `src/util/hook-config.ts` parses hook command entries and extracts Node hook script paths, including Windows path edge cases.
- `tests/hooks/core-routing.test.ts` exercises `routePreToolUse`, external MCP routing, sentinel readiness, and hook guidance behavior.

### Implementation-level limits

- Context-Mode owns a broad offload/routing/hook surface and can conflict with other hook/output/offload owners unless tested.
- It uses subprocess execution and persistent session state, so correctness and trust boundaries need detailed review before deployment.
- Token savings come from offloading intermediate work and returning selected results; quality depends on routing and result-selection behavior.

## Installation and integration behavior

- Tool type: Offloaded execution and routing tool
- Primary intervention surface: Execution offload, MCP/tool sandboxing, result selection, and routing hooks
- Integration status: documented integration paths and/or source locations were identified, but exact runtime behavior has not yet been fully reviewed.
- Disable/uninstall path: requires follow-up inspection of installer/plugin code and documentation.
- Failure behavior if dependency is missing: requires source-behavior review.

## Runtime behavior

- Intervention surface: Execution offload, MCP/tool sandboxing, result selection, and routing hooks
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Execution offload, MCP/tool sandboxing, result selection, and routing hooks
- Reduction method: identified at mechanism level; implementation details require source-behavior review.
- Quality-preservation mechanism: requires source and benchmark review.
- Cases where savings may not translate to provider-billed reductions: depends on turn count, prompt caching, failure/retry behavior, and whether the tool changes agent workflow length.

## Benchmarks and claims

| Claim | Source | Measurement scope | Reviewed method | Caveats |
|---|---|---|---|---|
| Token-saving or context-reduction claims exist or are implied by repository description/metadata. | Repository metadata and existing catalog records. | Varies by tool. | Not yet reviewed beyond source-tree and metadata inspection in this dossier. | Maintainer claims must not be treated as reproduced evidence. |

## Compatibility notes

Can coexist with code retrieval and behavior layers when it owns the offload/result-selection surface. It may conflict with RTK, Headroom, pctx, or other output/offload layers unless the combination is documented and tested.

Compatibility-safe stack selection means the tools should not fight over the same hook, context surface, retrieval authority, memory authority, proxy, or output channel.

## Failure modes and limits

- Generated analysis code and sandbox routing can introduce correctness and trust-boundary issues.
- Hook enforcement varies across platforms.
- Elastic License 2.0 affects open-source/commercial reuse assumptions.

## Open questions and next review tasks

- [ ] Inspect hook routing and tool interception implementation.
- [ ] Inspect sandbox execution and result-selection source.
- [ ] Review benchmark examples and raw outputs.
- [ ] Test interaction with RTK/Headroom before stack recommendations.

