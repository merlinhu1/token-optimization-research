# Tool dossier: rtk-ai/rtk

## Identity

- Repository: `rtk-ai/rtk`
- URL: https://github.com/rtk-ai/rtk
- Version/ref inspected: local shallow clone `23aae98c5b29`, 2026-06-26
- Date inspected: 2026-06-26
- Evidence stage: source-logic (local shallow clone; representative runner, filter, tee, hook rewrite/init, discovery, formatter, and guard tests inspected)

## Summary

RTK is a shell and tool-output compaction layer for AI coding agents. Source inspection shows a Rust runtime that rewrites eligible commands through agent hooks, applies command/category filters, guards output so filtered text does not exceed raw output, and stores raw failure output for recovery.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository source tree | `sources/discovery/2026-06-26-source-logic-uplift-source-structures.json` | Local shallow clone tree used to identify source, hook, MCP, test, benchmark, and runtime paths. |
| Runtime/source content | `sources/discovery/2026-06-26-source-logic-uplift-code-inspection.json` | Representative implementation files read from local clone with byte counts, SHA-256 prefixes, and behavior excerpts. |
| README/docs | README/docs and skill files where present. | README claims remain discovery evidence; source findings below control this evidence stage. |
| Tests/benchmarks | Test and benchmark paths identified; representative tests inspected where listed. | Benchmark-method review remains benchmark-audit work. |

## Initial source-structure finding

Local tree inspection found 380 files and 293 files matching integration, source, test, benchmark, hook, MCP, or documentation patterns. Relevant paths include:

- `src/core/utils.rs`
- `src/core/runner.rs`
- `src/core/toml_filter.rs`
- `src/core/stream.rs`
- `src/core/args_utils.rs`
- `src/core/README.md`
- `src/core/mod.rs`
- `src/core/telemetry_cmd.rs`
- `src/core/telemetry.rs`
- `src/core/constants.rs`
- `src/core/guard.rs`
- `src/core/tracking.rs`
- `src/core/tee.rs`
- `src/core/filter.rs`
- `src/core/config.rs`
- `src/core/display_helpers.rs`
- `src/core/truncate.rs`
- `src/hooks/trust.rs`
- `src/hooks/integrity.rs`
- `src/hooks/hook_audit_cmd.rs`
- `src/hooks/README.md`
- `src/hooks/mod.rs`
- `src/hooks/constants.rs`
- `src/hooks/permissions.rs`
- `src/hooks/hook_cmd.rs`
- `src/hooks/init.rs`
- `src/hooks/rewrite_cmd.rs`
- `src/hooks/hook_check.rs`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-source-logic-uplift-code-inspection.json`.

- `src/core/runner.rs` composes filtered output with optional recovery hints, applies a `never_worse` guard against raw output, and emits tee hints when applicable.
- `src/core/filter.rs` defines filter levels and source/comment-stripping behavior used for compaction modes.
- `src/core/tee.rs` saves unfiltered command output on failures with minimum-size, maximum-file, and maximum-file-size limits plus configurable tee directory overrides.
- `src/hooks/rewrite_cmd.rs` evaluates shell commands and exits with distinct allow/pass-through/deny/ask outcomes for agent hooks.
- `src/hooks/init.rs` embeds and installs agent-specific hook/plugin/instruction assets for Claude, Codex, Hermes, OpenCode, Pi, Cursor, Copilot, and other hosts.
- `src/discover/registry.rs` classifies command invocations through lexer/tokenization and category/subcommand rewrite rules.
- `src/parser/formatter.rs` defines compact, verbose, and ultra formatting modes for token-efficient canonical output.
- `tests/guard_integration_test.rs` pins the guard behavior that raw minified input should be emitted when filtering would bloat the output.

## Installation and integration behavior

- Tool: RTK
- Primary intervention surface: Terminal and tool-output compaction through command rewriting, filters, guarded output, and raw-output recovery
- Integration status: source and integration paths identified; source logic inspected for representative runtime files.
- Disable/uninstall path: partially inspected where representative files expose it; full host-by-host review remains open.
- Failure behavior if dependency is missing: partially inspected in representative code/tests; complete deployment failure-mode review remains open.

## Runtime behavior

- Intervention surface: Terminal and tool-output compaction through command rewriting, filters, guarded output, and raw-output recovery
- Input captured: implementation-specific inputs are described in code-detail findings.
- Output emitted: implementation-specific outputs are described in code-detail findings.
- State/cache/files written: representative state and recovery behavior identified where present.
- Network/subprocess behavior: not exhaustively reviewed; benchmark/reproduction review remains required.
- Raw-output recovery path: recorded where present; otherwise open for benchmark-audit/reproduction review.
- Security/privacy considerations: host hooks, local state, indexes, memory, or runtime boundaries should be reviewed before sensitive deployment.

## Token-saving mechanism

- Addressable token surface: Terminal and tool-output compaction through command rewriting, filters, guarded output, and raw-output recovery
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation exists.
- Quality-preservation mechanism: partially identified via guards, budgets, tests, profile controls, or explicit caveats where present.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, extra tool calls, stale indexes, skipped rewrites, duplicate context authorities, correction turns, or increased latency.

## Compatibility notes

Terminal-output compaction owner. It overlaps with Lowfat, TokenJuice, Snip, xcsift for overlapping command families, Headroom broad compression, and LeanCTX shell compression. Use as the single general shell/tool-output owner unless a benchmarked combination disables overlap.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Hook rewrite behavior depends on command classification coverage and shell parsing safety.
- Raw-output recovery is failure-oriented and bounded; success-path raw recovery still needs target-workflow checks.
- Filter rules can hide diagnostic detail if the wrong command family is matched.
- Benchmarks and counter-evidence still require benchmark-audit review.

## Open questions and next review tasks

- [ ] Review all embedded filter TOML categories and passthrough coverage.
- [ ] Benchmark RTK against Lowfat, Snip, TokenJuice, and Headroom on identical terminal-heavy tasks.
- [ ] Verify raw-output recovery workflow in Claude/Codex/Hermes integrations.
