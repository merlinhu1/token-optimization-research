# Tool dossier: portofcontext/pctx

## Identity

- Repository: `portofcontext/pctx`
- URL: https://github.com/portofcontext/pctx
- Version/ref inspected: GitHub `HEAD` API or local shallow clone plus representative implementation files, 2026-06-26
- Date inspected: 2026-06-26
- Evidence stage: source-logic (local shallow clone; representative MCP server, service, code mode, executor, and session routes inspected)
- Stars at inspection: 264
- Forks at inspection: None
- License: UNKNOWN-local-clone
- Updated at: local shallow clone 2026-06-26

## Summary

pctx provides an MCP/code-mode execution layer with session-scoped registries, generated TypeScript/bash execution tools, and an execution runtime for offloading tool work.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-06-26-ten-more-tool-source-structures.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-06-26-ten-more-tool-code-inspection.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 272 files and 206 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `crates/pctx_mcp_server/Cargo.toml`
- `crates/pctx_mcp_server/src/service.rs`
- `crates/pctx_mcp_server/src/server.rs`
- `crates/pctx_mcp_server/src/mod.rs`
- `crates/pctx_mcp_server/src/lib.rs`
- `crates/pctx_mcp_server/src/extractors.rs`
- `crates/pctx_mcp_server/src/utils/styles.rs`
- `crates/pctx_mcp_server/src/utils/mod.rs`
- `crates/pctx_code_mode/Cargo.toml`
- `crates/pctx_code_mode/src/code_mode.rs`
- `crates/pctx_code_mode/src/model.rs`
- `crates/pctx_code_mode/src/lib.rs`
- `crates/pctx_code_mode/src/descriptions.rs`
- `crates/pctx_code_mode/descriptions/tools/search_functions/v1.txt`
- `crates/pctx_code_mode/descriptions/tools/list_functions/v1.txt`
- `crates/pctx_code_mode/descriptions/tools/execute_typescript_filesystem/v1.txt`
- `crates/pctx_code_mode/descriptions/tools/execute_typescript_catalog/v1.txt`
- `crates/pctx_code_mode/descriptions/tools/execute_bash/v1.txt`
- `crates/pctx_code_mode/descriptions/tools/execute_typescript_sidecar/v1.txt`
- `crates/pctx_code_mode/descriptions/tools/get_function_details/v1.txt`
- `crates/pctx_executor/Cargo.toml`
- `crates/pctx_executor/src/events.rs`
- `crates/pctx_executor/src/lib.rs`
- `crates/pctx_executor/src/tests/mcp_client_usage.rs`
- `crates/pctx_executor/src/tests/mod.rs`
- `crates/pctx_executor/src/tests/output_capture.rs`
- `crates/pctx_executor/src/tests/concurrent_v8_stress.rs`
- `crates/pctx_executor/src/tests/just_bash.rs`
- `crates/pctx_executor/src/tests/runtime_execution.rs`
- `crates/pctx_executor/src/tests/diagnostic_filtering.rs`
- `crates/pctx_executor/src/tests/type_checking.rs`
- `crates/pctx_executor/src/tests/default_export_capture.rs`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-ten-more-tool-code-inspection.json`.

- `crates/pctx_mcp_server/src/server.rs` wraps a local session manager and cancels cached MCP connection pools when sessions close.
- `crates/pctx_mcp_server/src/service.rs` defines a `PctxMcpService` with tool routing, per-session MCP connection pools, and registry/disclosure configuration.
- `crates/pctx_code_mode/src/code_mode.rs` assembles server/tool registries, callbacks, and virtual filesystem support for code-mode workflows.
- `crates/pctx_executor/src/lib.rs` executes code with a registry and a global V8 runtime mutex to avoid unsafe concurrent JsRuntime access.
- `crates/pctx_session_server/src/routes.rs` creates/closes sessions and registers tools/MCP servers through HTTP routes backed by code-mode session state.

## Installation and integration behavior

- Tool: pctx
- Primary intervention surface: Execution offload/code mode that converts MCP/tool calls into sandboxed code workflows
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Execution offload/code mode that converts MCP/tool calls into sandboxed code workflows
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Execution offload/code mode that converts MCP/tool calls into sandboxed code workflows
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation is present.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes/state, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Execution-offload owner. It overlaps with Context-Mode and other sandbox/offload systems; can coexist with retrieval tools if result-selection boundaries are explicit.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Sandbox/runtime correctness and trust boundaries are central; failures can affect tool semantics, not just token count.
- Session/registry state introduces freshness and cleanup concerns.
- Type-check/runtime layers add latency and operational dependencies.

## Open questions and next review tasks

- [ ] Inspect runtime JS wrappers and Deno/type-check behavior.
- [ ] Review integration tests for output capture and diagnostic filtering.
- [ ] Benchmark token savings against Context-Mode on the same MCP-heavy tasks.
