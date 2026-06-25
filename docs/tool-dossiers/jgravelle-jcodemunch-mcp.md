# Tool dossier: jgravelle/jcodemunch-mcp

## Identity

- Repository: `jgravelle/jcodemunch-mcp`
- URL: https://github.com/jgravelle/jcodemunch-mcp
- Version/ref inspected: local shallow clone `bdebb6399f07`, 2026-07-01
- Snapshot status: pinned-commit
- Commit inspected: bdebb6399f07431d4b072582ff80f7639d8752c5
- Commit URL: https://github.com/jgravelle/jcodemunch-mcp/commit/bdebb6399f07431d4b072582ff80f7639d8752c5
- Source artifact path: `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json`
- Date inspected: 2026-07-01
- Evidence stage: source-logic (fresh pinned shallow clone; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection: 1,942
- Forks at inspection: 300
- License: NOASSERTION
- Updated at: 2026-06-26T04:40:07Z

## Summary

jcodemunch MCP indexes code into symbol/context structures and exposes many MCP tools for token-budgeted code retrieval, graph/context bundles, and compact schema-driven responses.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` | Used to identify installer, plugin, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime source | `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json` | Representative implementation files fetched from GitHub HEAD with SHA-256 prefixes and behavior excerpts. |
| README/docs | README path identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 626 files and 574 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

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
- `src/jcodemunch_mcp/cli/receipt.py`
- `src/jcodemunch_mcp/cli/reflect.py`
- `src/jcodemunch_mcp/cli/skills.py`
- `src/jcodemunch_mcp/cli/upgrade.py`
- `src/jcodemunch_mcp/cli/whatsnew.py`
- `src/jcodemunch_mcp/config.py`
- `src/jcodemunch_mcp/counter.py`
- `src/jcodemunch_mcp/credentials.py`
- `src/jcodemunch_mcp/embeddings/__init__.py`
- `src/jcodemunch_mcp/embeddings/local_encoder.py`
- `src/jcodemunch_mcp/encoding/__init__.py`
- `src/jcodemunch_mcp/encoding/decoder.py`
- `src/jcodemunch_mcp/encoding/format.py`
- `src/jcodemunch_mcp/encoding/gate.py`
- `src/jcodemunch_mcp/encoding/generic.py`
- `src/jcodemunch_mcp/encoding/json_passthrough.py`
- `src/jcodemunch_mcp/encoding/schema_driven.py`
- `src/jcodemunch_mcp/encoding/schemas/__init__.py`
- `src/jcodemunch_mcp/encoding/schemas/find_importers.py`
- `src/jcodemunch_mcp/encoding/schemas/find_references.py`
- `src/jcodemunch_mcp/encoding/schemas/get_blast_radius.py`
- `src/jcodemunch_mcp/encoding/schemas/get_call_hierarchy.py`
- `src/jcodemunch_mcp/encoding/schemas/get_dependency_cycles.py`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`.

### Fresh pinned-source refresh

The 2026-07-01 refresh pins the inspected source to `bdebb6399f07431d4b072582ff80f7639d8752c5` and records a fresh tree plus selected implementation excerpts in `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` and `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`. Representative files captured for this refresh include `src/jcodemunch_mcp/__init__.py`, `src/jcodemunch_mcp/__main__.py`, `src/jcodemunch_mcp/agent_selector.py`, `src/jcodemunch_mcp/cli/__init__.py`, `src/jcodemunch_mcp/cli/delivery.py`, `src/jcodemunch_mcp/cli/digest.py`. Treat benchmark, savings, and deployment claims below as source-logic only unless a benchmark-audit or reproduction artifact is explicitly cited.


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

Large code retrieval/indexing authority. It overlaps with CodeGraph, Serena, claude-context, code-review-graph, CocoIndex Code, and LeanCTX graph/search tools.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Very broad tool surface can increase configuration and routing complexity.
- License metadata is `NOASSERTION`; legal/commercial use needs verification.
- Token-savings claims require review of benchmark harnesses and raw baselines.

## Open questions and next review tasks

- [ ] Review registered tool list, output budgets, and schema encoders per tool.
- [ ] Inspect storage/index freshness and redaction behavior.
- [ ] Review benchmark harnesses and replay artifacts before ranking.
