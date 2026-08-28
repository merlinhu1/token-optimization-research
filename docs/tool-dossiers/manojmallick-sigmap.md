# Tool dossier: manojmallick/sigmap

## Identity

- Repository: `manojmallick/sigmap`
- URL: https://github.com/manojmallick/sigmap
- Version/ref inspected: `8.28.0` release at commit `3313c3a4e88722e134e5747663c02d5db5ad3032`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: 3313c3a4e88722e134e5747663c02d5db5ad3032
- Commit URL: https://github.com/manojmallick/sigmap/commit/3313c3a4e88722e134e5747663c02d5db5ad3032
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 8.28.0 release checkout from the batch release corpus, the same bytes its lanes install; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection (2026-07-01, not refreshed offline): 530
- Forks at inspection (2026-07-01, not refreshed offline): 37
- License: MIT
- Updated at (2026-07-01, not refreshed offline): 2026-06-26T03:25:38Z

## Summary

SigMap extracts code signatures and exposes an MCP server with tools for context reads, signature search, maps, impact, routing, and session memory.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Tree inspection of the pinned `8.28.0` release checkout found 573 files: 339 source, 106 documentation, 260 test/benchmark, and 42 matching installer, host-integration, hook, plugin, skill, MCP, or configuration patterns.

Integration code — what actually performs a host install, and therefore what an install protocol must be written against:

- `packages/adapters/claude.js`
- `packages/adapters/codex.js`
- `packages/adapters/cursor.js`
- `src/config/defaults.js`
- `src/config/loader.js`
- `src/config/tune.js`
- `src/init/creation-workflow.js`
- `src/map/config-manifest.js`
- `src/mcp/handlers.js`
- `src/mcp/install.js`
- `src/mcp/server.js`
- `src/mcp/tools.js`
- `src/skills/skills.js`

Host-integration documentation shipped in the release:

- `AGENTS.md`
- `docs-vp/guide/agents.md`
- `docs-vp/guide/config.md`
- `docs-vp/guide/mcp.md`
- `docs/JETBRAINS_SETUP.md`
- `docs/readmes/ENTERPRISE_SETUP.md`
- `docs/readmes/JETBRAINS_SETUP.md`
- `docs/readmes/MCP_SETUP.md`
- `docs/readmes/jetbrains-plugin.md`


## Code-detail inspection findings

### Pinned-release refresh (2026-08-28)

This dossier previously described `569320994751`, read from GitHub HEAD on 2026-07-01. That is not the code any lane runs. `BATCH_RELEASES` pins this tool to the **8.28.0** release at `3313c3a4e887`, and the runner rewrites every lane path onto it, so the reading below is now taken from that pinned checkout instead. Inspecting the corpus checkout rather than a fresh network fetch keeps the reading reproducible after upstream HEAD moves again.

Upstream shipped **36 releases** between 2026-07-01 and this pin (`CHANGELOG.md`). A protocol derived from the older reading is how the 2026-08-22 review found five drifts and one blocking defect, so any integration step below is worth re-checking against the pinned release rather than trusted.

This project's changelog headings carry no descriptive titles, so which of those releases touched an install surface cannot be read off the headings. The most recent are:

- [8.28.0] — 2026-08-18
- [8.27.0] — 2026-08-18
- [8.26.2] — 2026-08-18
- [8.26.1] — 2026-08-18
- [8.26.0] — 2026-08-18
- [8.25.0] — 2026-08-18
- [8.24.0] — 2026-07-28
- [8.23.0] — 2026-07-28
- …and 28 further releases; see `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.

The official install guide this tool is evaluated against is `source/README.md` at sha256 `5c6d0392b5dcbadd…` in the pinned release.

Evidence artifact: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.


- `src/mcp/server.js` is a zero-dependency JSON-RPC line server that lists tools and dispatches calls over stdin/stdout.
- `src/mcp/tools.js` defines 17 MCP tools including context reads, signature search, impact, memory, diff context, and architecture overview.
- `src/retrieval/ranker.js` ranks files by keyword overlap, symbol matches, prefix/path matches, graph boosts, and learned weights.
- `src/graph/builder.js` builds forward/reverse dependency graphs for many language families from import/require patterns.
- `src/session/memory.js` stores short-lived coding-session context with a TTL for merge/read/clear workflows.

## Installation and integration behavior

- Tool: SigMap
- Primary intervention surface: Signature-map code retrieval, dependency graph, session memory, and MCP tools
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Signature-map code retrieval, dependency graph, session memory, and MCP tools
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Signature-map code retrieval, dependency graph, session memory, and MCP tools
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation is present.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes/state, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Code retrieval/signature authority plus light memory. It overlaps with CodeGraph, Serena, jcodemunch, CocoIndex Code, code-review-graph, and LeanCTX retrieval.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Signature extraction/ranking can miss dynamic behavior or unsupported language patterns.
- Session memory TTL and format may conflict with longer-lived memory systems.
- Benchmark claims require raw task/harness review before ranking.

## Open questions and next review tasks

- [ ] Inspect extraction dispatch and per-language parsers.
- [ ] Review benchmark reports/tasks and failure semantics.
- [ ] Compare retrieval output budgets against CodeGraph/Serena/jcodemunch.
