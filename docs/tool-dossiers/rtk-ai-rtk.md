# Tool dossier: rtk-ai/rtk

## Identity

- Repository: `rtk-ai/rtk`
- URL: https://github.com/rtk-ai/rtk
- Version/ref inspected: `0.45.0` release at commit `b34be37caf3796b69a50952a28e60e32b5daad43`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: b34be37caf3796b69a50952a28e60e32b5daad43
- Commit URL: https://github.com/rtk-ai/rtk/commit/b34be37caf3796b69a50952a28e60e32b5daad43
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 0.45.0 release checkout from the batch release corpus, the same bytes its lanes install; representative runner, filter, tee, hook rewrite/init, discovery, formatter, and guard tests inspected)

## Summary

RTK is a shell and tool-output compaction layer for AI coding agents. Source inspection shows a Rust runtime that rewrites eligible commands through agent hooks, applies command/category filters, guards output so filtered text does not exceed raw output, and stores raw failure output for recovery.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository source tree | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Local shallow clone tree used to identify source, hook, MCP, test, benchmark, and runtime paths. |
| Runtime/source content | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Representative implementation files read from local clone with byte counts, SHA-256 prefixes, and behavior excerpts. |
| README/docs | README/docs and skill files where present. | README claims remain discovery evidence; source findings below control this evidence stage. |
| Tests/benchmarks | Test and benchmark paths identified; representative tests inspected where listed. | Benchmark-method review remains benchmark-audit work. |

## Initial source-structure finding

Tree inspection of the pinned `0.45.0` release checkout found 412 files: 143 source, 146 documentation, 88 test/benchmark, and 98 matching installer, host-integration, hook, plugin, skill, MCP, or configuration patterns.

Integration code — what actually performs a host install, and therefore what an install protocol must be written against:

- `hooks/hermes/rtk-rewrite/__init__.py`
- `hooks/opencode/rtk.ts`
- `hooks/pi/rtk.ts`
- `src/core/config.rs`
- `src/hooks/constants.rs`
- `src/hooks/hook_audit_cmd.rs`
- `src/hooks/hook_check.rs`
- `src/hooks/hook_cmd.rs`
- `src/hooks/init.rs`
- `src/hooks/integrity.rs`
- `src/hooks/mod.rs`
- `src/hooks/permissions.rs`
- `src/hooks/rewrite_cmd.rs`
- `src/hooks/trust.rs`
- `src/hooks/verify_cmd.rs`

Host-integration documentation shipped in the release:

- `.claude/agents/code-reviewer.md`
- `.claude/agents/debugger.md`
- `.claude/agents/rust-rtk.md`
- `.claude/agents/system-architect.md`
- `.claude/agents/technical-writer.md`
- `.claude/commands/clean-worktree.md`
- `.claude/commands/clean-worktrees.md`
- `.claude/commands/diagnose.md`
- `.claude/commands/tech/audit-codebase.md`
- `.claude/commands/tech/clean-worktree.md`
- `.claude/commands/tech/clean-worktrees.md`
- `.claude/commands/tech/codereview.md`
- `.claude/commands/tech/remove-worktree.md`
- `.claude/commands/tech/worktree-status.md`


## Code-detail inspection findings

### Pinned-release refresh (2026-08-28)

This dossier previously described `23aae98c5b29`, read from GitHub HEAD on 2026-06-26. That is not the code any lane runs. `BATCH_RELEASES` pins this tool to the **0.45.0** release at `b34be37caf37`, and the runner rewrites every lane path onto it, so the reading below is now taken from that pinned checkout instead. Inspecting the corpus checkout rather than a fresh network fetch keeps the reading reproducible after upstream HEAD moves again.

Upstream shipped **5 releases** between 2026-06-26 and this pin (`CHANGELOG.md`). A protocol derived from the older reading is how the 2026-08-22 review found five drifts and one blocking defect, so any integration step below is worth re-checking against the pinned release rather than trusted.

This project's changelog headings carry no descriptive titles, so which of those releases touched an install surface cannot be read off the headings. The most recent are:

- [0.45.0](https://github.com/rtk-ai/rtk/compare/v0.44.2...v0.45.0) (2026-08-07)
- [0.44.2](https://github.com/rtk-ai/rtk/compare/v0.44.1...v0.44.2) (2026-08-01)
- [0.44.1](https://github.com/rtk-ai/rtk/compare/v0.44.0...v0.44.1) (2026-07-28)
- [0.44.0](https://github.com/rtk-ai/rtk/compare/v0.43.0...v0.44.0) (2026-07-26)
- [0.43.0](https://github.com/rtk-ai/rtk/compare/v0.42.4...v0.43.0) (2026-06-28)

The official install guide this tool is evaluated against is `source/README.md` at sha256 `413b3c684d00c36d…` in the pinned release.

Evidence artifact: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.

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
