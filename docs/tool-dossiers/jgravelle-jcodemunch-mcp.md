# Tool dossier: jgravelle/jcodemunch-mcp

## Identity

- Repository: `jgravelle/jcodemunch-mcp`
- URL: https://github.com/jgravelle/jcodemunch-mcp
- Version/ref inspected: `1.108.290` release at commit `9e76d6320c017b774d54bb31d79dd4b8a5876aff`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: 9e76d6320c017b774d54bb31d79dd4b8a5876aff
- Commit URL: https://github.com/jgravelle/jcodemunch-mcp/commit/9e76d6320c017b774d54bb31d79dd4b8a5876aff
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 1.108.290 release checkout from the batch release corpus, the same bytes its lanes install; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection (2026-07-01, not refreshed offline): 1,942
- Forks at inspection (2026-07-01, not refreshed offline): 300
- License: NOASSERTION
- Updated at (2026-07-01, not refreshed offline): 2026-06-26T04:40:07Z

## Summary

jcodemunch MCP indexes code into symbol/context structures and exposes many MCP tools for token-budgeted code retrieval, graph/context bundles, and compact schema-driven responses.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Used to identify installer, plugin, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime source | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Representative implementation files read from the pinned release checkout with SHA-256 prefixes. |
| README/docs | README path identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Tree inspection of the pinned `1.108.290` release checkout found 964 files: 786 source, 56 documentation, 626 test/benchmark, and 316 matching installer, host-integration, hook, plugin, skill, MCP, or configuration patterns.

Integration code — what actually performs a host install, and therefore what an install protocol must be written against:

- `clients/ts/decoder.ts`
- `mcpb/build.py`
- `mcpb/server/main.py`
- `src/jcodemunch_mcp/__init__.py`
- `src/jcodemunch_mcp/__main__.py`
- `src/jcodemunch_mcp/agent_selector.py`
- `src/jcodemunch_mcp/cli/__init__.py`
- `src/jcodemunch_mcp/cli/delivery.py`
- `src/jcodemunch_mcp/cli/digest.py`
- `src/jcodemunch_mcp/cli/file_risk.py`
- `src/jcodemunch_mcp/cli/health.py`
- `src/jcodemunch_mcp/cli/hooks.py`
- `src/jcodemunch_mcp/cli/init.py`
- `src/jcodemunch_mcp/cli/install_pack.py`
- `src/jcodemunch_mcp/cli/observatory.py`
- `src/jcodemunch_mcp/cli/parity.py`
- `src/jcodemunch_mcp/cli/receipt.py`
- `src/jcodemunch_mcp/cli/reflect.py`
- `src/jcodemunch_mcp/cli/skills.py`
- `src/jcodemunch_mcp/cli/upgrade.py`
- `src/jcodemunch_mcp/cli/whatsnew.py`
- `src/jcodemunch_mcp/config.py`
- `src/jcodemunch_mcp/counter.py`
- `src/jcodemunch_mcp/credentials.py`
- `src/jcodemunch_mcp/embeddings/__init__.py`
- `src/jcodemunch_mcp/embeddings/advice.py`
- `src/jcodemunch_mcp/embeddings/local_encoder.py`
- `src/jcodemunch_mcp/encoding/__init__.py`

Host-integration documentation shipped in the release:

- `AGENTS.md`
- `AGENT_HINTS.md`
- `AGENT_HOOKS.md`
- `AGENT_INSTALL_UNIVERSAL.md`
- `CLAUDE.md`
- `CLIENTS.md`
- `CONFIGURATION.md`
- `INSTALL_FROM_SOURCE.md`
- `clients/ts/README.md`


## Code-detail inspection findings

### Pinned-release refresh (2026-08-28)

This dossier previously described `bdebb6399f07`, read from GitHub HEAD on 2026-07-01. That is not the code any lane runs. `BATCH_RELEASES` pins this tool to the **1.108.290** release at `9e76d6320c01`, and the runner rewrites every lane path onto it, so the reading below is now taken from that pinned checkout instead. Inspecting the corpus checkout rather than a fresh network fetch keeps the reading reproducible after upstream HEAD moves again.

Upstream shipped **199 releases** between 2026-07-01 and this pin (`CHANGELOG.md`). A protocol derived from the older reading is how the 2026-08-22 review found five drifts and one blocking defect, so any integration step below is worth re-checking against the pinned release rather than trusted.

14 of those releases name an install surface in their own title:

- [1.108.284] - 2026-08-17 - A documented setting the storage layer never read
- [1.108.283] - 2026-08-17 - A config in the wrong shape is a client that reports success and registers nothing
- [1.108.258] - 2026-08-07 - A config read that reads the config
- [1.108.255] - 2026-08-07 - Hook output on channels the model never sees
- [1.108.251] - 2026-08-06 - every server start silently deleted your installed starter packs
- [1.108.250] - 2026-08-06 - `config --check` reported a default while the indexer used your config
- [1.108.248] - 2026-08-06 - starter packs install again, and stop misreporting why they did not
- [1.108.242] - 2026-08-05 - documentation restructure: CAPABILITIES.md + CLIENTS.md, corrected tool counts and counters
- [1.108.221] - 2026-08-02 - what this install could establish, not just what it saw
- [1.108.197] - 2026-07-28 - the escape hatch read the wrong config file
- [1.108.150] - 2026-07-28 - stateless-MCP forward cover: principal session keying + SSE deprecation notice
- [1.108.121] - 2026-07-11 - License CLI reads the config-file `license_key`
- …and 2 more; see `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.

The official install guide this tool is evaluated against is `source/CLIENTS.md` at sha256 `19e87ba818c8efad…` in the pinned release.

Evidence artifact: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.


- `src/jcodemunch_mcp/server.py` implements the MCP server and lazily imports tool modules at dispatch time to reduce cold-start cost for sessions that do not need indexing-heavy tools.
- `src/jcodemunch_mcp/tools/get_ranked_context.py` assembles best-K-token context for a query using token costs, compact fields, savings recording, and context-bundle helpers.
- `src/jcodemunch_mcp/tools/_indexing_pipeline.py` shares indexing logic for file/folder/repo indexing, parsing files, language detection, context providers, and file summaries.
- `src/jcodemunch_mcp/parser/symbols.py` defines stable symbol IDs, line ranges, keyword fields, and content hashes for re-indexing stability.
- `src/jcodemunch_mcp/encoding/schema_driven.py` provides compact schema-driven encoding helpers for per-tool outputs.

## Installation and integration behavior

- Tool: jcodemunch MCP
- Primary intervention surface: MCP symbol/code retrieval, indexing, schema-driven compact encoding, and ranked context assembly
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative runtime files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: MCP symbol/code retrieval, indexing, schema-driven compact encoding, and ranked context assembly
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: MCP symbol/code retrieval, indexing, schema-driven compact encoding, and ranked context assembly
- Reduction method: implementation-level mechanism identified in representative source files.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Large code retrieval/indexing authority. It overlaps with CodeGraph, Serena, code-review-graph, CocoIndex Code, and LeanCTX graph/search tools.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Very broad tool surface can increase configuration and routing complexity.
- License metadata is `NOASSERTION`; legal/commercial use needs verification.
- Token-savings claims require review of benchmark harnesses and raw baselines.

## Open questions and next review tasks

- [ ] Review registered tool list, output budgets, and schema encoders per tool.
- [ ] Inspect storage/index freshness and redaction behavior.
- [ ] Review benchmark harnesses and replay artifacts before ranking.
