# Tool dossier: JuliusBrussee/caveman

## Identity

- Repository: `JuliusBrussee/caveman`
- URL: https://github.com/JuliusBrussee/caveman
- Version/ref inspected: GitHub `HEAD` tree via API, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 3-source-behavior (representative hook, MCP proxy, compressor, and tests inspected)
- Stars at inspection: 77,013
- Forks at inspection: 4,360
- License: MIT
- Updated at: 2026-06-26T07:42:50Z

## Summary

Caveman is a cross-agent terse-output skill/plugin. It primarily reduces assistant prose and related instruction/tool-description overhead rather than reducing code retrieval or shell output by itself.

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

Repository tree inspection found 148 files and 116 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `.claude-plugin/marketplace.json`
- `.claude-plugin/plugin.json`
- `plugins/caveman/.codex-plugin/plugin.json`
- `plugins/caveman/agents/cavecrew-builder.md`
- `plugins/caveman/agents/cavecrew-investigator.md`
- `plugins/caveman/agents/cavecrew-reviewer.md`
- `plugins/caveman/assets/caveman-small.svg`
- `plugins/caveman/assets/caveman.svg`
- `plugins/caveman/skills/cavecrew/SKILL.md`
- `plugins/caveman/skills/caveman-compress/SKILL.md`
- `plugins/caveman/skills/caveman-compress/scripts/__init__.py`
- `plugins/caveman/skills/caveman-compress/scripts/__main__.py`
- `plugins/caveman/skills/caveman-compress/scripts/benchmark.py`
- `plugins/caveman/skills/caveman-compress/scripts/cli.py`
- `plugins/caveman/skills/caveman-compress/scripts/compress.py`
- `plugins/caveman/skills/caveman-compress/scripts/detect.py`
- `plugins/caveman/skills/caveman-compress/scripts/validate.py`
- `plugins/caveman/skills/caveman-stats/SKILL.md`
- `plugins/caveman/skills/caveman/SKILL.md`
- `plugins/caveman/skills/caveman/agents/openai.yaml`
- `plugins/caveman/skills/caveman/assets/caveman-small.svg`
- `plugins/caveman/skills/caveman/assets/caveman.svg`
- `src/plugins/opencode/README.md`
- `src/plugins/opencode/commands/caveman-commit.md`
- `src/plugins/opencode/commands/caveman-compress.md`
- `src/plugins/opencode/commands/caveman-help.md`
- `src/plugins/opencode/commands/caveman-review.md`
- `src/plugins/opencode/commands/caveman-stats.md`
- `src/plugins/opencode/commands/caveman.md`
- `src/plugins/opencode/package.json`
- `src/plugins/opencode/plugin.js`
- `.codex/hooks.json`
- `src/hooks/README.md`
- `src/hooks/caveman-activate.js`
- `src/hooks/caveman-config.js`
- `src/hooks/caveman-mode-tracker.js`
- `src/hooks/caveman-stats.js`
- `src/hooks/caveman-statusline.ps1`
- `src/hooks/caveman-statusline.sh`
- `src/hooks/checksums.sha256`



## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-five-more-tool-code-inspection.json`. The artifact contains raw GitHub file paths, byte sizes, SHA-256 prefixes, and behavior-line excerpts from the inspected implementation files.

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
- Failure behavior if dependency is missing: requires source-behavior review.

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
- Reduction method: identified at mechanism level; implementation details require source-behavior review.
- Quality-preservation mechanism: requires source and benchmark review.
- Cases where savings may not translate to provider-billed reductions: depends on turn count, prompt caching, failure/retry behavior, and whether the tool changes agent workflow length.

## Benchmarks and claims

| Claim | Source | Measurement scope | Reviewed method | Caveats |
|---|---|---|---|---|
| Token-saving or context-reduction claims exist or are implied by repository description/metadata. | Repository metadata and existing catalog records. | Varies by tool. | Not yet reviewed beyond source-tree and metadata inspection in this dossier. | Maintainer claims must not be treated as reproduced evidence. |

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
