# Tool dossier: open-compress/claw-compactor

## Identity

- Repository: `open-compress/claw-compactor`
- URL: https://github.com/open-compress/claw-compactor
- Version/ref inspected: local shallow clone `c1b936d40b11`, 2026-07-01
- Snapshot status: pinned-commit
- Commit inspected: c1b936d40b1145c7a257bd6e34a17994f467495f
- Commit URL: https://github.com/open-compress/claw-compactor/commit/c1b936d40b1145c7a257bd6e34a17994f467495f
- Source artifact path: `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json`
- Date inspected: 2026-07-01
- Evidence stage: source-logic (fresh pinned shallow clone; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection: 2,191
- Forks at inspection: 209
- License: MIT
- Updated at: 2026-06-25T14:32:22Z

## Summary

Claw Compactor applies staged, content-aware compression to messages/tool results and includes proxy middleware with rewind retrieval for compressed sections.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` | Used to identify installer, plugin, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime source | `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json` | Representative implementation files fetched from GitHub HEAD with SHA-256 prefixes and behavior excerpts. |
| README/docs | README path identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 209 files and 151 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `scripts/lib/fusion/__init__.py`
- `scripts/lib/fusion/base.py`
- `scripts/lib/fusion/cache_prefix.py`
- `scripts/lib/fusion/compact_hooks.py`
- `scripts/lib/fusion/content_detector.py`
- `scripts/lib/fusion/content_stripper.py`
- `scripts/lib/fusion/conversation_summarizer.py`
- `scripts/lib/fusion/cortex.py`
- `scripts/lib/fusion/diff_crunch.py`
- `scripts/lib/fusion/engine.py`
- `scripts/lib/fusion/ionizer.py`
- `scripts/lib/fusion/llm_summarizer.py`
- `scripts/lib/fusion/log_crunch.py`
- `scripts/lib/fusion/neurosyntax.py`
- `scripts/lib/fusion/nexus.py`
- `scripts/lib/fusion/nexus_model.py`
- `scripts/lib/fusion/photon.py`
- `scripts/lib/fusion/pipeline.py`
- `scripts/lib/fusion/plan_reinjection.py`
- `scripts/lib/fusion/quantum_lock.py`
- `scripts/lib/fusion/search_crunch.py`
- `scripts/lib/fusion/semantic_dedup.py`
- `scripts/lib/fusion/skill_reinjection.py`
- `scripts/lib/fusion/structural_collapse.py`
- `scripts/lib/fusion/tiered_compaction.py`
- `scripts/lib/fusion/tool_result_budget.py`
- `proxy/compression-middleware.mjs`
- `proxy/package-lock.json`
- `proxy/package.json`
- `proxy/server.mjs`
- `proxy/test/event-log.test.mjs`
- `proxy/test/helpers.mjs`
- `proxy/test/integration.test.mjs`
- `proxy/test/metrics-store.test.mjs`
- `proxy/test/process-registry.test.mjs`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`.

### Fresh pinned-source refresh

The 2026-07-01 refresh pins the inspected source to `c1b936d40b1145c7a257bd6e34a17994f467495f` and records a fresh tree plus selected implementation excerpts in `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` and `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`. Representative files captured for this refresh include `scripts/lib/fusion/__init__.py`, `scripts/lib/fusion/base.py`, `scripts/lib/fusion/cache_prefix.py`, `scripts/lib/fusion/compact_hooks.py`, `scripts/lib/fusion/content_detector.py`, `scripts/lib/fusion/content_stripper.py`. Treat benchmark, savings, and deployment claims below as source-logic only unless a benchmark-audit or reproduction artifact is explicitly cited.


- `scripts/lib/fusion/pipeline.py` runs ordered compression stages sequentially, feeding each stage output into the next stage context.
- `scripts/lib/fusion/engine.py` is the unified entry point for string/message compression and wires stages such as content detection, log/search/diff compression, structural collapse, and token optimization.
- `scripts/lib/fusion/content_detector.py` classifies content as text/code/json/log/diff/search using rule-based detectors before stage routing.
- `scripts/lib/fusion/tool_result_budget.py` truncates older tool-role messages while keeping recent and exempt tool results intact.
- `proxy/compression-middleware.mjs` scans compressed messages for Rewind markers and injects a `rewind_retrieve` tool definition for retrieving original uncompressed content.

## Installation and integration behavior

- Tool: Claw Compactor
- Primary intervention surface: Multi-stage text/tool-result compression pipeline and proxy middleware
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative runtime files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Multi-stage text/tool-result compression pipeline and proxy middleware
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Multi-stage text/tool-result compression pipeline and proxy middleware
- Reduction method: implementation-level mechanism identified in representative source files.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Broad compression/proxy owner. It overlaps with Headroom, RTK, TokenTamer, Kompact, and LeanCTX compression unless used in a clearly separate message/proxy layer.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Multi-stage compression can obscure content if recovery paths fail.
- Rewind retrieval adds tool definitions and state/retrieval dependency.
- Quality preservation must be benchmarked on task success, not only compression ratio.

## Open questions and next review tasks

- [ ] Inspect Rewind store/retriever and hash collision/failure behavior.
- [ ] Review benchmark datasets and raw results.
- [ ] Test with coding-agent tool outputs that require exact line/error fidelity.
