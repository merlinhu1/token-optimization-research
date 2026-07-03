# Tool dossier: HoangP8/tokless

## Identity

- Repository: `HoangP8/tokless`
- URL: https://github.com/HoangP8/tokless
- Version/ref inspected: local shallow clone `769cd6dc8413`, 2026-06-26
- Snapshot status: pinned-commit
- Commit inspected: 769cd6dc8413
- Commit URL: https://github.com/HoangP8/tokless/commit/769cd6dc8413
- Source artifact path: `sources/discovery/2026-06-26-final-lead-uplift-source-structures.json`
- Date inspected: 2026-06-26
- Evidence stage: source-logic (local shallow clone; registry, init/wire loop, agent config writers, bundled-tool installers, MCP/hook wiring, indexing, and integration tests inspected)
- Stars at inspection: not recorded in source-logic artifact
- Forks at inspection: not recorded in source-logic artifact
- License: MIT
- Updated at: local shallow clone 2026-06-26

## Summary

Tokless is a Go installer and compatibility orchestrator for token-saving tools across Claude Code, Codex, OpenCode, and Antigravity/Gemini-style agents. Source inspection shows that it does not itself compress context or rewrite model prompts as a primary runtime. Its main behavior is dependency installation, agent detection, MCP server configuration, hook/plugin registration, project indexing, and cleanup for bundled tools such as RTK, CodeGraph, Context-Mode, and Caveman.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Source tree | `sources/discovery/2026-06-26-final-lead-uplift-source-structures.json` | Local shallow clone tree used to identify CLI, registry, tool, agent, hook, MCP, install, test, and utility paths. |
| Runtime/source content | `sources/discovery/2026-06-26-final-lead-uplift-code-inspection.json` | Representative Go implementation files read with byte counts, SHA-256 prefixes, and behavior excerpts. |
| README/docs | Repository README and installer assets identified in source tree. | README claims are discovery inputs only. |
| Tests/benchmarks | Go tests for registry, init integration, installation fallbacks, Caveman relocation, CodeGraph freshness, and utility behavior identified. `sources/discovery/2026-06-26-tokless-go-test.json` records a passing `go test ./...` run for the inspected clone. | Full benchmark-method review remains open; inspected tests mainly cover wiring and install behavior, not token-savings outcomes. |

## Initial source-structure finding

Repository tree inspection found 109 tracked files. Relevant paths include:

- `cmd/tokless/main.go`
- `internal/core/core.go`
- `internal/commands/init.go`
- `internal/commands/disable.go`
- `internal/commands/index.go`
- `internal/commands/runmcp.go`
- `internal/tools/rtk.go`
- `internal/tools/contextmode.go`
- `internal/tools/codegraph.go`
- `internal/tools/caveman.go`
- `internal/agents/claude.go`
- `internal/agents/codex.go`
- `internal/agents/opencode.go`
- `internal/util/npminstall.go`
- `internal/util/mcpspawn.go`
- `internal/commands/init_integration_test.go`
- `internal/core/registry_test.go`

## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-final-lead-uplift-code-inspection.json`.

- `internal/core/core.go` defines the central `ToolManifest` and `AgentManifest` registries. Tools expose install functions, per-agent wire/unwire maps, verify functions, project indexing hooks, and dependency metadata such as channel, Git requirement, and minimum Node version.
- `internal/commands/init.go` selects tools, ensures Node/Git prerequisites, installs each tool, detects installed agents, and wires each selected tool to each selected agent. Wiring failures are tracked per agent and return a non-zero exit when any selected agent cannot be fully equipped.
- `internal/tools/rtk.go` downloads RTK prebuilt release assets or falls back to the upstream install script/cargo. It rewrites or wraps Claude/Codex/OpenCode/Antigravity hooks so shell/tool output flows through RTK-owned compaction behavior.
- `internal/tools/contextmode.go` installs `context-mode` via npm, enforces Node 22+ checks, configures Claude MCP, OpenCode plugins, Codex hooks across multiple events, and cleans stale OpenCode cache directories before plugin reuse.
- `internal/tools/codegraph.go` installs `@colbymchenry/codegraph`, runs `codegraph install`, configures MCP entries for supported agents, verifies config presence, and runs project indexing with `codegraph sync` or `codegraph init`.
- `internal/tools/caveman.go` adds/removes Caveman skills or plugins, writes fenced instruction blocks into agent instruction files, removes MCP entries for older Caveman wiring, and preserves uninstall cleanup logic.
- `internal/agents/claude.go` shows that Claude integration writes `~/.claude.json` MCP server entries and permissions allow-list entries such as `mcp__<tool>__.*`, so Tokless changes agent-level configuration and permission state.
- `internal/commands/disable.go`, `internal/commands/index.go`, and `internal/commands/runmcp.go` provide operational cleanup, indexing, and MCP-spawn paths rather than token-saving algorithms.

## Installation and integration behavior

- Tool: Tokless
- Primary intervention surface: installer/orchestrator for multiple external token-saving tools and supported agents.
- Integration status: source logic inspected for registry, install, agent wiring, MCP configuration, hook/plugin registration, indexing, and cleanup paths.
- Disable/uninstall path: represented by unwire functions and command paths that remove MCP entries, plugins, hooks, or fenced instruction blocks for known tools.
- Failure behavior if dependency is missing: dependency checks gate npm/Git/Node-dependent installs; per-tool install and per-agent wire failures are recorded and surfaced.

## Runtime behavior

- Intervention surface: configuration-time and hook/MCP setup layer. Runtime token-saving is delegated to installed tools such as RTK, CodeGraph, Context-Mode, and Caveman.
- Input captured: agent/tool configuration paths, selected tools/agents, project directory for indexing, and environment/dependency probes.
- Output emitted: modified agent config files, MCP entries, hooks/plugins, instruction blocks, index directories, and progress/failure logs.
- State/cache/files written: agent settings, global config files, OpenCode plugin/cache entries, local binaries, `.codegraph` indexes, and fenced Caveman instruction blocks.
- Network/subprocess behavior: downloads release assets, runs shell install scripts, cargo/npm installs, `codegraph` commands, and tool-specific MCP spawns.
- Raw-output recovery path: not a compactor itself; recovery depends on the installed tools. Tokless preserves failure logs for install/wire phases.
- Security/privacy considerations: writes broad MCP permissions for some agents and installs/runs third-party tools. This is operationally useful but makes Tokless a high-trust setup tool rather than a narrow reducer.

## Token-saving mechanism

- Addressable token surface: orchestration of terminal compaction, retrieval/indexing, memory/style layers, and execution offload tools through supported agents.
- Reduction method: no independent reduction method identified in Tokless source logic; token reduction comes from bundled tools it installs and wires.
- Quality-preservation mechanism: compatibility-aware setup, verification, install fallback, and cleanup logic reduce integration failure risk but do not prove token-saving quality.
- Cases where savings may not translate to provider-billed reductions: overlapping installed tools can double-own hooks/MCP/memory surfaces; installer success does not imply benchmarked savings; broad permissions and auto-wiring can introduce extra calls or stale indexes.

## Compatibility notes

Tokless is best treated as an installation and compatibility orchestrator, not as a stack component that directly reduces tokens. It can be useful for reproducible setup when the chosen underlying tools are already selected, but it should not be counted as an additional reduction layer in a compatibility-safe stack.

Because Tokless can wire several tools at once, the selected profile must still obey one-owner-per-surface rules: one terminal/tool-output compactor, one retrieval authority, one memory/reinjection authority, one broad proxy/compression owner, and one behavior/artifact controller unless overlap is explicitly disabled and tested.

## Failure modes and limits

- High trust boundary: writes agent configs, hooks, plugins, permissions, local binaries, and indexes.
- Bundle risk: the default tool set may combine surfaces that should be selected intentionally rather than installed as a blanket stack.
- External dependency risk: npm, cargo, GitHub release downloads, install scripts, and tool-specific postinstall behavior can fail or change independently.
- Verification mainly confirms install/config presence; it is not evidence of provider-billed token savings or pass-rate preservation.
- Benchmark-audit or reproduction evidence for Tokless as an orchestrated full-stack installer was not found in the inspected representative files.

## Open questions and next review tasks

- [ ] Define explicit Tokless profiles that install only non-overlapping surfaces for target workloads.
- [ ] Benchmark Tokless-installed profiles against manually installed equivalents to separate installer reliability from reduction quality.
- [ ] Review all unwire paths for idempotence and stale-permission cleanup across supported agents.
- [ ] Run install/disable tests in clean Claude, Codex, OpenCode, and Antigravity sandboxes before recommending operational rollout.
