# Tool dossier: yvgude/lean-ctx

## Identity

- Repository: `yvgude/lean-ctx`
- URL: https://github.com/yvgude/lean-ctx
- Version/ref inspected: GitHub `HEAD` tree and representative raw implementation files via API, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 3-source-behavior (representative implementation files inspected; benchmark/reproduction review remains open)
- Stars at inspection: 2,941
- Forks at inspection: 285
- License: Apache-2.0
- Updated at: 2026-06-26T07:45:20Z

## Summary

LeanCTX is a broad local context layer that controls what agents read, compresses outputs, exposes many MCP tools, and records token-saving telemetry.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-06-26-eight-more-tool-source-structures.json` | Used to identify installer, plugin, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime source | `sources/discovery/2026-06-26-eight-more-tool-code-inspection.json` | Representative implementation files fetched from GitHub HEAD with SHA-256 prefixes and behavior excerpts. |
| README/docs | README path identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 2,060 files and 1,762 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `integrations/hermes-lean-ctx/benchmarks/README.md`
- `integrations/hermes-lean-ctx/benchmarks/__init__.py`
- `integrations/hermes-lean-ctx/benchmarks/corpus.py`
- `integrations/hermes-lean-ctx/benchmarks/engines.py`
- `integrations/hermes-lean-ctx/benchmarks/metrics.py`
- `integrations/hermes-lean-ctx/benchmarks/run.py`
- `integrations/hermes-lean-ctx/tests/__init__.py`
- `integrations/hermes-lean-ctx/tests/_helpers.py`
- `integrations/hermes-lean-ctx/tests/conftest.py`
- `integrations/hermes-lean-ctx/tests/test_benchmark.py`
- `integrations/hermes-lean-ctx/tests/test_compaction.py`
- `integrations/hermes-lean-ctx/tests/test_config.py`
- `integrations/hermes-lean-ctx/tests/test_engine_abc.py`
- `integrations/hermes-lean-ctx/tests/test_engine_adapter.py`
- `integrations/hermes-lean-ctx/tests/test_lifecycle.py`
- `integrations/hermes-lean-ctx/tests/test_live_daemon.py`
- `integrations/hermes-lean-ctx/tests/test_registration.py`
- `integrations/hermes-lean-ctx/tests/test_tools.py`
- `integrations/hermes-lean-ctx/tokens.py`
- `integrations/hermes-lean-ctx/tools.py`
- `BENCHMARKS.md`
- `assets/leanctx-benchmark.gif`
- `bench/agent-task/.gitignore`
- `bench/agent-task/PROMPT.md`
- `bench/agent-task/PROTOCOL.md`
- `bench/agent-task/README.md`
- `bench/agent-task/config.json`
- `bench/agent-task/r2/README.md`
- `bench/agent-task/r2/faithful-arm.env`
- `bench/agent-task/r2/lean-ctx.toml`
- `bench/agent-task/r2/pi-config.json`
- `bench/agent-task/r2/preflight.mjs`
- `bench/agent-task/requirements.txt`
- `bench/agent-task/swebench_harness/__init__.py`
- `bench/agent-task/swebench_harness/collect.py`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-eight-more-tool-code-inspection.json`.

- `rust/src/mcp_stdio.rs` implements MCP stdio serving, so LeanCTX can be an MCP tool provider rather than only a CLI.
- `rust/src/tools/ctx_read/mod.rs` implements compressed/cacheable read modes, computes output tokens, and stores compressed bodies with a full-source-on-request hint.
- `rust/src/tools/ctx_search.rs` renders compressed search output and tracks observed tokens plus modeled native-grep baselines.
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
