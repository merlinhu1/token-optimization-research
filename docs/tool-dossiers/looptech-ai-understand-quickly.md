# Tool dossier: looptech-ai/understand-quickly

## Identity

- Repository: `looptech-ai/understand-quickly`
- URL: https://github.com/looptech-ai/understand-quickly
- Local clone inspected: `/tmp/token-leads-20260629/looptech-ai__understand-quickly`
- Version/ref inspected: local shallow clone `6df261fcfa99`, 2026-06-29
- Snapshot status: pinned-commit
- Commit inspected: 6df261fcfa99
- Commit URL: https://github.com/looptech-ai/understand-quickly/commit/6df261fcfa99
- Source artifact path: `sources/discovery/2026-06-29-graph-leads-b-source-logic.json`
- Date inspected: 2026-06-29
- Evidence stage: source-logic (local shallow clone; representative registry scripts, MCP server, CLI add flow, schemas, validation, aggregation, and tests inspected)

## Summary

Understand Quickly is a public registry and thin MCP surface for discovering externally generated code-knowledge graph JSON files. Source inspection shows it does not parse a local codebase itself; it validates/fetches graph URLs, aggregates registry-wide stats, exposes registry lookup/search tools over MCP, and offers a CLI to submit a repository graph entry. The token-saving premise is discovery/reuse of precomputed graph artifacts rather than local indexing or prompt compression.

## Evidence inventory

| Evidence type | Files inspected | Notes |
|---|---|---|
| Manifests/entrypoints | `package.json`, `mcp/package.json`, `cli/package.json`, `python-sdk/pyproject.toml` (identified) | Root scripts validate/sync/aggregate/render; MCP package exposes `understand-quickly-mcp`; CLI package exposes `understand-quickly`. |
| MCP source | `mcp/src/index.ts`, `mcp/src/registry.ts`, `mcp/src/types.ts`, `mcp/src/tools/list-repos.ts`, `mcp/src/tools/get-graph.ts`, `mcp/src/tools/search-concepts.ts`, `mcp/src/tools/find-graph-for-repo.ts` | MCP is stdio and provides registry/list/get/search/find tools. |
| Registry/sync scripts | `scripts/validate.mjs`, `scripts/sync.mjs`, `scripts/aggregate.mjs`, `scripts/shard.mjs` (identified), `scripts/extract.mjs` (identified), `scripts/well-known.mjs` (identified) | Validation, remote fetch/sync, stats aggregation, and sharding paths inspected/identified. |
| CLI/source integration | `cli/bin/understand-quickly.mjs`, `cli/src/add.mjs`, `cli/src/detect.mjs` (identified), `cli/src/format.mjs` (identified), `cli/src/spawn.mjs` (identified) | CLI detects graph files/formats and emits issue/PR-ready registry entries. |
| Schemas/tests/site | `schemas/understand-anything@1.json`, `schemas/gitnexus@1.json` (identified), `schemas/code-review-graph@1.json` (identified), `mcp/tests/tools.test.ts`, `scripts/__tests__/validate.test.mjs`, `site/viewer.js` (identified) | Schema and test paths confirm validation and UI surfaces. |

## Installation and integration behavior

- Root `package.json` is a private registry/site package with scripts for validation, sync, aggregation, well-known endpoints, rendering, badges, and tests.
- `mcp/package.json` publishes `@looptech-ai/understand-quickly-mcp`, with `understand-quickly-mcp` mapped to `dist/index.js`; it depends on the MCP SDK and `zod`.
- `mcp/src/index.ts` creates a `McpServer` with stdio transport and registers `list_repos`, `get_graph`, `search_concepts`, and `find_graph_for_repo`.
- The CLI entrypoint requires Node 20+, dispatches `understand-quickly add`, and can print a JSON entry, open a prefilled issue, or attempt a PR flow via `gh`.
- Registry and graph source URLs can be overridden via `UNDERSTAND_QUICKLY_REGISTRY` and `UNDERSTAND_QUICKLY_STATS` for MCP fetches.

## Runtime behavior

- `loadRegistry` fetches `registry.json`, validates it has an `entries` array and schema version 1, and caches results in-memory for 60 seconds; stale cache is reused on 5xx registry responses.
- `fetchGraph` refuses non-HTTPS, localhost/internal, obvious private IPv4, and private IPv6 literal hosts before fetching a graph URL.
- `list_repos` filters registry entries by format, tag, and status, then returns compact summaries with id, format, description, status, tags, timestamp, and graph URL.
- `get_graph` resolves a registry id and returns the remote parsed graph JSON from that entry's `graph_url`.
- `search_concepts` defaults to precomputed `stats.json` concept matches; with `id` it searches one graph's node-like arrays; if stats fetch fails it scans up to five ok entries as a bounded fan-out fallback.
- `find_graph_for_repo` parses GitHub HTTPS/SSH URLs into `owner/repo`, looks up a registry entry, returns graph/drift metadata when found, or Levenshtein suggestions when not found.
- `validate.mjs` compiles JSON schemas with Ajv, validates registry uniqueness, fetches each graph with retry/size checks, parses JSON, and validates graph format schemas.
- `sync.mjs` updates entry status by fetching graph bodies, applying body limits and schema checks, deriving stats/source SHA, and marking missing/oversize/invalid/transient states.
- `aggregate.mjs` fetches ok graph entries with bounded concurrency and emits registry-wide `stats.json` totals, kinds, languages, and shared concept terms.

## Token-saving mechanism

- Main mechanism: expose precomputed graph registry metadata and graph URLs so agents can discover structured code maps without reading entire repositories or README pages.
- MCP search uses `stats.json` for cheap concept lookup by default, avoiding remote fan-out except on fallback or single-graph mode.
- Tool results are JSON summaries; `list_repos` is compact, and `search_concepts` caps concept matches and samples.
- Savings are indirect and depend on the quality/freshness of third-party graph artifacts. The repository does not implement local prompt compression or provider token accounting.

## Benchmarks and claims

| Claim area | Source inspected | Reviewed method | Caveats |
|---|---|---|---|
| Registry helps agents understand code quickly through graph artifacts. | MCP/registry/CLI source and schemas. | Source-logic only. | No benchmark artifacts or raw task outputs were inspected. |
| Graph validity/status. | `scripts/validate.mjs`, `scripts/sync.mjs`, schemas. | Logic review of validation pipeline only. | Validation is schema/availability evidence, not task effectiveness evidence. |

## Compatibility notes

- Treat this as a graph-discovery registry, not a local source indexer. It can complement local code graph tools by locating published graph artifacts, but it should not be counted as an active retrieval authority over a user's unregistered local checkout.
- If used alongside Cartog/CodeGraph/Serena/LeanCTX, make the boundary explicit: Understand Quickly finds or fetches precomputed external graph JSON; the local tool owns live repository querying.
- It performs network fetches to registry/stats/graph URLs during MCP calls, subject to SSRF guards but still relevant for privacy/offline deployments.

## Failure modes and limits

- Remote registry, stats, or graph URLs can be stale, missing, oversized, invalid, or unavailable; status fields are only as current as the last sync.
- `search_concepts` is substring/token based, not semantic embedding search; fan-out is capped to five entries.
- `get_graph` can return large graph JSON to the model if the selected graph is large.
- Registry data quality depends on external producers and schema conformance, not repository-local source parsing.
- MCP server has in-process cache only; each process refetches after TTL.

## Open questions

- How many registry entries are current and relevant to token-research workflows at the inspected commit?
- Are graph URL payloads small enough for practical MCP use, or should callers prefer stats/listing first?
- What provenance and licensing expectations apply to third-party graph JSON artifacts?

## Next review tasks

- [ ] Inspect `registry.json` entries and a sample graph payload for freshness/size/provenance.
- [ ] Run source-logic follow-up on `sync.mjs` drift checks and `extract.mjs` stats extraction.
- [ ] Do not advance to benchmark-audit unless task harnesses and raw outputs are present beyond registry validation.
