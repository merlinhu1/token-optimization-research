# Tool dossier: edouard-claude/snip

## Identity

- Repository: `edouard-claude/snip`
- URL: https://github.com/edouard-claude/snip
- Version/ref inspected: GitHub `HEAD` API or local shallow clone plus representative implementation files, 2026-06-26
- Date inspected: 2026-06-26
- Evidence stage: source-logic (local shallow clone; representative hook rewrite, transparent prefix, parser, and audit files inspected)
- Stars at inspection: 347
- Forks at inspection: None
- License: UNKNOWN-local-clone
- Updated at: local shallow clone 2026-06-26

## Summary

Snip rewrites agent shell commands so supported producers run through command-specific filters, with transparent-prefix handling and audit logging.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-06-26-ten-more-tool-source-structures.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-06-26-ten-more-tool-code-inspection.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 242 files and 100 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `internal/utils/utils.go`
- `internal/utils/regex_test.go`
- `internal/utils/regex.go`
- `internal/utils/utils_test.go`
- `internal/tee/tee_test.go`
- `internal/tee/tee.go`
- `internal/hook/codex_test.go`
- `internal/hook/hook_test.go`
- `internal/hook/transparent.go`
- `internal/hook/rewrite_test.go`
- `internal/hook/codex.go`
- `internal/hook/rewrite.go`
- `internal/hook/pi_test.go`
- `internal/hook/hook.go`
- `internal/hook/pi.go`
- `internal/hook/parse.go`
- `internal/hook/parse_test.go`
- `internal/hook/transparent_test.go`
- `internal/display/display_test.go`
- `internal/display/gain.go`
- `internal/display/display.go`
- `internal/display/gain_test.go`
- `internal/learn/learn.go`
- `internal/learn/learn_test.go`
- `internal/initcmd/codex_test.go`
- `internal/initcmd/init_test.go`
- `internal/initcmd/init.go`
- `internal/initcmd/codex.go`
- `internal/initcmd/pi_test.go`
- `internal/initcmd/pi.go`
- `internal/verify/verify.go`
- `internal/verify/verify_test.go`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-ten-more-tool-code-inspection.json`.

- `internal/hook/rewrite.go` splits compound commands on shell boundaries and rewrites only eligible producer stages so filters apply before downstream pipes.
- `internal/hook/transparent.go` models transparent runners such as `uv run`, `poetry run`, and `docker exec`, preserving prefixes while filtering the inner command.
- `internal/hook/parse.go` extracts first command segments and detects unverifiable constructs such as command substitution/backticks that should not be silently rewritten.
- `internal/hookaudit/hookaudit.go` writes best-effort JSONL hook audit events under a local Snip data directory with bounded tail behavior.
- `cmd/snip/main.go` is a small Cobra-style CLI entrypoint delegating to internal command logic.

## Installation and integration behavior

- Tool: Snip
- Primary intervention surface: CLI proxy/hook-based command-output filtering with declarative filters
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: CLI proxy/hook-based command-output filtering with declarative filters
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: CLI proxy/hook-based command-output filtering with declarative filters
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation is present.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes/state, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Terminal-output compaction owner. It overlaps with RTK, Lowfat, TokenJuice, xcsift on specific command domains, and LeanCTX shell compression.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Hook rewriting must be cautious around shell syntax; missed or unverifiable constructs reduce coverage.
- Filters can affect downstream pipe consumers if command boundaries are misidentified.
- Audit logs are best-effort and not a full recovery path.

## Open questions and next review tasks

- [ ] Inspect filter YAML schema and representative filters.
- [ ] Review hook install/uninstall for Claude/Codex/Pi.
- [ ] Benchmark fidelity on test/build/log commands against RTK/Lowfat/TokenJuice.
