# Tool dossier: edouard-claude/snip

## Identity

- Repository: `edouard-claude/snip`
- URL: https://github.com/edouard-claude/snip
- Version/ref inspected: `0.24.1` release at commit `18a57bc9dc4499f1a00b9c8ff799e982ba25ceba`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: 18a57bc9dc4499f1a00b9c8ff799e982ba25ceba
- Commit URL: https://github.com/edouard-claude/snip/commit/18a57bc9dc4499f1a00b9c8ff799e982ba25ceba
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 0.24.1 release checkout from the batch release corpus, the same bytes its lanes install; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection (2026-07-01, not refreshed offline): 347
- Forks at inspection (2026-07-01, not refreshed offline): None
- License: UNKNOWN-local-clone
- Updated at (2026-07-01, not refreshed offline): local shallow clone 2026-06-26

## Summary

Snip rewrites agent shell commands so supported producers run through command-specific filters, with transparent-prefix handling and audit logging.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Tree inspection of the pinned `0.24.1` release checkout found 258 files: 98 source, 16 documentation, 67 test/benchmark, and 46 matching installer, host-integration, hook, plugin, skill, MCP, or configuration patterns.

Integration code — what actually performs a host install, and therefore what an install protocol must be written against:

- `internal/config/config.go`
- `internal/hook/blockscope.go`
- `internal/hook/codex.go`
- `internal/hook/copilot.go`
- `internal/hook/grok.go`
- `internal/hook/hook.go`
- `internal/hook/parse.go`
- `internal/hook/pi.go`
- `internal/hook/rewrite.go`
- `internal/hook/suggest.go`
- `internal/hook/transparent.go`
- `internal/hookaudit/hookaudit.go`
- `internal/initcmd/codex.go`
- `internal/initcmd/copilot.go`
- `internal/initcmd/grok.go`
- `internal/initcmd/init.go`
- `internal/initcmd/pi.go`

Host-integration documentation shipped in the release:

- `CLAUDE.md`
- `SKILL.md`


## Code-detail inspection findings

### Pinned-release refresh (2026-08-28)

This dossier previously described `82b741b3ba50`, read from GitHub HEAD on 2026-07-01. That is not the code any lane runs. `BATCH_RELEASES` pins this tool to the **0.24.1** release at `18a57bc9dc44`, and the runner rewrites every lane path onto it, so the reading below is now taken from that pinned checkout instead. Inspecting the corpus checkout rather than a fresh network fetch keeps the reading reproducible after upstream HEAD moves again.

No release-by-release delta is available (release ships no changelog), so the gap between the audited commit and this pin is not enumerable from the release bytes alone.

The official install guide this tool is evaluated against is `source/README.md` at sha256 `710e49a20580910a…` in the pinned release.

Evidence artifact: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.


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
