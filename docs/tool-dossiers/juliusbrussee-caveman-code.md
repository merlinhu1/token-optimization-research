# Tool dossier: JuliusBrussee/caveman-code

## Identity

- Repository: `JuliusBrussee/caveman-code`
- URL: https://github.com/JuliusBrussee/caveman-code
- Version/ref inspected: local shallow clone `74d599aa7a61`, 2026-06-26
- Date inspected: 2026-06-26
- Evidence stage: source-logic (local shallow clone; agent loop, model routing, proxy stream, cost caps, compression fallback, memory provider, repomap builder, token verification, microbench runner, and session/settings paths inspected)
- Stars at inspection: not recorded in source-logic artifact
- Forks at inspection: not recorded in source-logic artifact
- License: Apache-2.0
- Updated at: local shallow clone 2026-06-26

## Summary

Caveman Code is a replacement AI coding agent/runtime implemented as a TypeScript monorepo. Source inspection found a real agent loop, model router, proxy streaming layer, cost-cap tracker, compression exports and fallback events, cavemem-backed memory integration, repository-map construction, token verification utilities, and microbenchmark runners. It should be evaluated as a replacement runtime rather than as an add-on token-saving plugin.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Source tree | `sources/discovery/2026-06-26-final-lead-uplift-source-structures.json` | Local shallow clone tree used to identify agent runtime, TUI, SDK, coding-agent, memory, compression, repomap, benchmark, and research/eval paths. |
| Runtime/source content | `sources/discovery/2026-06-26-final-lead-uplift-code-inspection.json` | Representative TypeScript implementation files read with byte counts, SHA-256 prefixes, and behavior excerpts. |
| README/docs | Repository README/docs paths identified in source tree. | README claims are not used as behavior evidence. |
| Tests/benchmarks | `packages/agent/src/bench/*`, `research/evals/*`, `research/results/*`, and agent tests identified. | Benchmark harnesses are present, but full benchmark-audit remains open. |

## Initial source-structure finding

Repository tree inspection found 1,423 tracked files. Relevant paths include:

- `packages/agent/src/agent.ts`
- `packages/agent/src/agent-loop.ts`
- `packages/agent/src/router.ts`
- `packages/agent/src/proxy.ts`
- `packages/agent/src/cost/caps.ts`
- `packages/agent/src/cost/trace-writer.ts`
- `packages/agent/src/compression/index.ts`
- `packages/agent/src/compression/fallback.ts`
- `packages/agent/src/compression/llmlingua.ts`
- `packages/agent/src/memory/index.ts`
- `packages/agent/src/memory/cavemem.ts`
- `packages/agent/src/repomap/builder.ts`
- `packages/agent/src/repomap/pagerank.ts`
- `packages/agent/src/bench/token-verifier.ts`
- `packages/agent/src/bench/microbench-dataset.ts`
- `research/evals/run-microbench.ts`
- `packages/coding-agent/src/core/sdk.ts`
- `packages/coding-agent/src/core/session-manager.ts`
- `packages/coding-agent/src/core/settings-manager.ts`
- `packages/agent/src/__tests__/bench.test.ts`

## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-final-lead-uplift-code-inspection.json`.

- `packages/agent/src/agent.ts` implements a stateful `Agent` wrapper around the low-level loop. It owns messages/tools, queues steering and follow-up messages, supports context transforms, tool filters, model routing, stream functions, transport choice, tool execution mode, and max-turn caps.
- `packages/agent/src/agent-loop.ts` applies context transforms before LLM calls, converts internal messages at the LLM boundary, resolves system prompts/tools per turn, streams assistant events, and executes tool calls sequentially or in parallel with argument validation and before/after tool hooks.
- `packages/agent/src/router.ts` defines role-based routing with cache-retention hints and deterministic cost-aware downgrade at 90% of a configured session cap for non-plan roles.
- `packages/agent/src/proxy.ts` streams through a proxy endpoint, strips/reconstructs partial event state, sends model/context/options to `/api/stream`, and preserves token/cost usage fields in reconstructed messages.
- `packages/agent/src/cost/caps.ts` tracks per-turn and per-session spend, emits cap events, and can cancel calls when caps are crossed; turn caps require acknowledgement before continuation.
- `packages/agent/src/compression/fallback.ts` wraps compression calls so inference failures emit `compression_fallback` trace events and fall back to passthrough rather than failing the agent loop.
- `packages/agent/src/memory/cavemem.ts` wraps `cavemem` as both hook subprocess and stdio MCP server. Writes are hook-driven, reads use MCP namespaced calls, and high-frequency writes are best-effort/non-blocking.
- `packages/agent/src/repomap/builder.ts` parses files, builds a symbol graph, applies personalized PageRank using added/mentioned files, selects symbols within a token budget, and renders a compact repository map.
- `packages/agent/src/bench/token-verifier.ts` implements independent token verification via tokenizer recount or provider Usage APIs with mode-specific tolerances.
- `research/evals/run-microbench.ts` runs Cave sessions on small coding tasks, enables Cave mode with ultra intensity/tool compression/ML compression, records cost/tool calls/tokens, and verifies tasks through `verify.sh`.

## Installation and integration behavior

- Tool: Caveman Code / Cave
- Primary intervention surface: replacement AI coding agent/runtime with its own loop, tool execution, memory, routing, compression, cost accounting, repository-map, and benchmark subsystems.
- Integration status: source logic inspected for runtime loop, routing, proxy, memory, cost, compression fallback, repomap, benchmark/token verification, and session/settings paths.
- Disable/uninstall path: not fully reviewed; replacement runtime can be avoided by not using the Cave CLI/session, but installed package cleanup and state removal need follow-up.
- Failure behavior if dependency is missing: source shows fallback behavior for compression failures and best-effort memory hook writes; full dependency-failure map remains open.

## Runtime behavior

- Intervention surface: replacement runtime rather than a hook-layer add-on. It controls context transformation, model calls, tool execution, message state, memory integration, repository-map generation, and cost/cap handling.
- Input captured: user/assistant/tool messages, system prompt, tool schemas/results, memory hook payloads, source files for repomap, benchmark prompts, and provider usage windows.
- Output emitted: streamed assistant messages, tool results, trace/cost events, memory hook subprocess writes, MCP memory reads, repomap text, benchmark result files, and verification results.
- State/cache/files written: session state, settings, cost traces, memory backend data via cavemem, benchmark outputs, and possible checkpoint/worktree state through related packages.
- Network/subprocess behavior: provider/proxy LLM streams, cavemem subprocess and MCP transport, dynamic tokenizer/provider usage API imports, benchmark subprocess verification scripts, and tool executions.
- Raw-output recovery path: not a shell-output compactor. It preserves tool results in the agent loop and benchmark outputs, but raw recovery for compressed content depends on the specific compression and session subsystems.
- Security/privacy considerations: replacement runtime has broad visibility into prompts, files, tools, memory, and provider/proxy calls. This makes it a large trust boundary relative to add-on reducers.

## Token-saving mechanism

- Addressable token surface: assistant verbosity, context selection, repository map budget, memory retrieval, tool-result compression, model routing, cache retention, and cost caps inside a replacement agent.
- Reduction method: runtime-level control through compact repository maps, role/model routing, compression middleware, cavemem-backed memory, tool-result handling, and benchmarked Cave mode settings.
- Quality-preservation mechanism: tool validation hooks, before/after hooks, max-turn caps, compression passthrough fallback, token verification utilities, task verification scripts, and benchmark aggregation paths.
- Cases where savings may not translate to provider-billed reductions: replacement runtime may add orchestration turns, proxy overhead, memory/tool calls, benchmark-specific settings, or correction loops; source-logic evidence is not yet independent benchmark reproduction.

## Compatibility notes

Caveman Code should be evaluated as an alternative coding-agent runtime, not combined with hook-layer token-saving stacks such as RTK/Lowfat/Snip/TokenJuice/Headroom by default. Combining it with external memory, retrieval, or compression tools risks double ownership because the runtime already includes memory, repomap/context selection, compression, routing, and cost/accounting surfaces.

It may be compared against ClawCodex and existing Claude/Codex workflows in a replacement-agent evaluation lane using identical tasks, model/provider settings, billed-token accounting, pass rates, latency, and implementation-quality scoring.

## Failure modes and limits

- Large replacement-agent surface creates more compatibility and trust-boundary risk than narrow add-on tools.
- Benchmark harnesses and result files exist, but source-logic inspection did not reproduce provider-billed savings or pass-rate preservation.
- Memory depends on `cavemem` availability and best-effort hook dispatch; failures may silently degrade memory capture.
- Compression fallback preserves operation by passing through content, which protects quality but can erase expected token savings.
- Cost-aware routing depends on configured caps and may alter model quality near session limits.
- Repository-map quality depends on parser coverage, token-budget selection, and the accuracy of added/mentioned-file personalization.

## Open questions and next review tasks

- [ ] Run benchmark-audit on `research/evals/run-microbench.ts`, `packages/agent/src/bench/*`, and stored `research/results/*` to validate methodology, raw outputs, and scoring.
- [ ] Reproduce a replacement-agent comparison against ClawCodex and baseline Claude/Codex with provider-billed token accounting.
- [ ] Inspect CLI install/state cleanup and checkpoint/worktree behavior before operational rollout.
- [ ] Map all default Cave mode settings to exact runtime transforms and compression middleware.
