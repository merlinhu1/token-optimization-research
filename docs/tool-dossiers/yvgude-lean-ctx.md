# Tool dossier: yvgude/lean-ctx

## Identity

- Repository: `yvgude/lean-ctx`
- URL: https://github.com/yvgude/lean-ctx
- Version/ref inspected: `3.9.19` release at commit `8a3d23b317c98b39704543c9acb8b7cc8992c63d`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: 8a3d23b317c98b39704543c9acb8b7cc8992c63d
- Commit URL: https://github.com/yvgude/lean-ctx/commit/8a3d23b317c98b39704543c9acb8b7cc8992c63d
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 3.9.19 release checkout from the batch release corpus, the same bytes its lanes install; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection (2026-07-01, not refreshed offline): 2,941
- Forks at inspection (2026-07-01, not refreshed offline): 285
- License: Apache-2.0
- Updated at (2026-07-01, not refreshed offline): 2026-06-26T07:45:20Z

## Summary

LeanCTX is a broad local context layer that controls what agents read, compresses outputs, exposes many MCP tools, and records token-saving telemetry.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Used to identify installer, plugin, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime source | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Representative implementation files read from the pinned release checkout with SHA-256 prefixes. |
| README/docs | README path identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Tree inspection of the pinned `3.9.19` release checkout found 3416 files: 2427 source, 350 documentation, 826 test/benchmark, and 470 matching installer, host-integration, hook, plugin, skill, MCP, or configuration patterns.

Integration code — what actually performs a host install, and therefore what an install protocol must be written against:

- `clients/python/leanctx/__init__.py`
- `clients/python/leanctx/adapters/__init__.py`
- `clients/python/leanctx/adapters/_common.py`
- `clients/python/leanctx/adapters/crewai.py`
- `clients/python/leanctx/adapters/langchain.py`
- `clients/python/leanctx/adapters/llamaindex.py`
- `clients/python/leanctx/adapters/openai.py`
- `clients/python/leanctx/client.py`
- `clients/python/leanctx/conformance.py`
- `clients/python/leanctx/errors.py`
- `clients/python/leanctx/ocla.py`
- `clients/python/leanctx/ocla_verify.py`
- `clients/python/leanctx/tool_text.py`
- `clients/rust/lean-ctx-client/src/bin/lean-ctx-ocla-verify.rs`
- `clients/rust/lean-ctx-client/src/client.rs`
- `clients/rust/lean-ctx-client/src/conformance.rs`
- `clients/rust/lean-ctx-client/src/error.rs`
- `clients/rust/lean-ctx-client/src/events.rs`
- `clients/rust/lean-ctx-client/src/lib.rs`
- `clients/rust/lean-ctx-client/src/ocla.rs`
- `clients/rust/lean-ctx-client/src/tool_text.rs`
- `clients/rust/lean-ctx-client/src/types.rs`
- `cookbook/examples/knowledge-graph-explorer/src/lib/client.ts`
- `cookbook/examples/knowledge-graph-explorer/vite.config.ts`
- `cookbook/sdk/src/client.ts`
- `go-sdk/client.go`
- `integrations/hermes-lean-ctx/__init__.py`
- `integrations/hermes-lean-ctx/config.py`

Host-integration documentation shipped in the release:

- `.codex/vision-input/01-MARKET-PAIN.md`
- `.codex/vision-input/02-VISION.md`
- `.codex/vision-input/03-CONTEXT-KITS.md`
- `.codex/vision-input/04-ARCHITECTURE.md`
- `.codex/vision-input/07-PARTNER-STRATEGY.md`
- `.codex/vision-input/09-MONETIZATION.md`
- `.codex/vision-input/15-BRANDING.md`
- `.codex/vision-input/17-GO-TO-MARKET.md`
- `.codex/vision-output/00-EXECUTIVE-SUMMARY.md`
- `AGENTS.md`
- `clients/python/README.md`
- `clients/rust/lean-ctx-client/README.md`
- `discord-faq/01-installation-setup.md`
- `discord-faq/03-shell-hook-issues.md`


## Code-detail inspection findings

### Path drift at this pin

Between the commit this dossier used to describe and the pinned 3.9.19 release, the Rust tool modules were reorganised. Every path below was cited by the readings in this dossier and no longer resolves as written:

- `rust/src/tools/registered/ctx_search.rs` → `rust/src/tools/registered/ctx_search.rs` (tools moved behind a `registered/` layer)

The paths are corrected here; the **behavioural claims attached to them were not re-verified** against the pinned release. A file that moved during a restructure can also have changed what it does, so treat those specific readings as carried over from the older commit rather than as current source-logic evidence.

### Pinned-release refresh (2026-08-28)

This dossier previously described `adc4e8b2e401`, read from GitHub HEAD on 2026-07-01. That is not the code any lane runs. `BATCH_RELEASES` pins this tool to the **3.9.19** release at `8a3d23b317c9`, and the runner rewrites every lane path onto it, so the reading below is now taken from that pinned checkout instead. Inspecting the corpus checkout rather than a fresh network fetch keeps the reading reproducible after upstream HEAD moves again.

Upstream shipped **20 releases** between 2026-07-01 and this pin (`CHANGELOG.md`). A protocol derived from the older reading is how the 2026-08-22 review found five drifts and one blocking defect, so any integration step below is worth re-checking against the pinned release rather than trusted.

This project's changelog headings carry no descriptive titles, so which of those releases touched an install surface cannot be read off the headings. The most recent are:

- [3.9.19] — 2026-08-18
- [3.9.18] — 2026-08-08
- [3.9.17] — 2026-08-04
- [3.9.16] — 2026-08-04
- [3.9.15] — 2026-08-04
- [3.9.14] — 2026-08-03
- [3.9.13] — 2026-07-29
- [3.9.12] — 2026-07-17
- …and 12 further releases; see `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.

The official install guide this tool is evaluated against is `source/README.md` at sha256 `0e53184df357ed64…` in the pinned release.

Evidence artifact: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.


- `rust/src/mcp_stdio.rs` implements MCP stdio serving, so LeanCTX can be an MCP tool provider rather than only a CLI.
- `rust/src/tools/ctx_read/mod.rs` implements compressed/cacheable read modes, computes output tokens, and stores compressed bodies with a full-source-on-request hint.
- `rust/src/tools/registered/ctx_search.rs` renders compressed search output and tracks observed tokens plus modeled native-grep baselines.
- `rust/crates/lean-ctx-sdk/src/compress.rs` exposes shell/tool-output compression and explicitly returns original output when no compressor improves it.
- `integrations/hermes-lean-ctx/tools.py` advertises LeanCTX tool schemas and proxies calls to the daemon over `/v1` for Hermes integration.

## Installation and integration behavior

- Tool: LeanCTX
- Primary intervention surface: Broad context intelligence layer: compressed reads, search, shell compression, memory, code graph, and MCP tools
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative runtime files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Broad context intelligence layer: compressed reads, search, shell compression, memory, code graph, and MCP tools
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Broad context intelligence layer: compressed reads, search, shell compression, memory, code graph, and MCP tools
- Reduction method: implementation-level mechanism identified in representative source files.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Broad context owner. It can cover retrieval, read compression, shell compression, memory, and graph surfaces, so it should be combined with narrow tools only after surface ownership is explicit.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Broad surface creates overlap risk with RTK, CodeGraph, Serena, Token Savior, Headroom, and memory tools.
- Daemon and cache state affect reproducibility and freshness.
- Telemetry baselines need provider-billed validation.

## Open questions and next review tasks

- [ ] Map which LeanCTX tools are enabled in each agent integration.
- [ ] Inspect daemon state/cache boundaries and raw-output recovery paths.
- [ ] Run focused comparisons against narrower tools by surface.
