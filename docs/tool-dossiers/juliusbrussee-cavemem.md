# Tool dossier: JuliusBrussee/cavemem

## Identity

- Repository: `JuliusBrussee/cavemem`
- URL: https://github.com/JuliusBrussee/cavemem
- Version/ref inspected: local shallow clone `1fe41e9c9f28`, 2026-07-01
- Snapshot status: pinned-commit
- Commit inspected: 1fe41e9c9f28380d3da9640f02812f8e5565839a
- Commit URL: https://github.com/JuliusBrussee/cavemem/commit/1fe41e9c9f28380d3da9640f02812f8e5565839a
- Source artifact path: `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json`
- Date inspected: 2026-07-01
- Evidence stage: source-logic (fresh pinned shallow clone; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection: 565
- Forks at inspection: 49
- License: MIT
- Updated at: 2026-06-26T03:57:44Z

## Summary

Cavemem stores compressed observations for coding agents, backfills embeddings, exposes MCP/CLI search, and can inject additional context via hooks.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 161 files and 131 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `apps/cli/package.json`
- `apps/cli/scripts/pack-release.mjs`
- `apps/cli/scripts/prepack.mjs`
- `apps/cli/src/commands/compress.ts`
- `apps/cli/src/commands/config.ts`
- `apps/cli/src/commands/doctor.ts`
- `apps/cli/src/commands/export.ts`
- `apps/cli/src/commands/hook.ts`
- `apps/cli/src/commands/install.ts`
- `apps/cli/src/commands/lifecycle.ts`
- `apps/cli/src/commands/mcp.ts`
- `apps/cli/src/commands/reindex.ts`
- `apps/cli/src/commands/search.ts`
- `apps/cli/src/commands/status.ts`
- `apps/cli/src/commands/uninstall.ts`
- `apps/cli/src/commands/worker.ts`
- `apps/cli/src/env.d.ts`
- `apps/cli/src/index.ts`
- `apps/cli/src/util/resolve.ts`
- `apps/cli/test/program.test.ts`
- `apps/cli/tsup.config.ts`
- `apps/cli/vitest.config.ts`
- `apps/mcp-server/CHANGELOG.md`
- `apps/mcp-server/package.json`
- `apps/mcp-server/src/server.ts`
- `apps/mcp-server/test/exports.test.ts`
- `apps/mcp-server/test/server.test.ts`
- `apps/mcp-server/tsconfig.json`
- `apps/worker/package.json`
- `apps/worker/src/embed-loop.ts`
- `apps/worker/src/server.ts`
- `apps/worker/src/viewer.ts`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`.

### Fresh pinned-source refresh

The 2026-07-01 refresh pins the inspected source to `1fe41e9c9f28380d3da9640f02812f8e5565839a` and records a fresh tree plus selected implementation excerpts in `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` and `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`. Representative files captured for this refresh include `apps/cli/package.json`, `apps/cli/scripts/pack-release.mjs`, `apps/cli/scripts/prepack.mjs`, `apps/cli/src/commands/compress.ts`, `apps/cli/src/commands/config.ts`, `apps/cli/src/commands/doctor.ts`. Treat benchmark, savings, and deployment claims below as source-logic only unless a benchmark-audit or reproduction artifact is explicitly cited.


- `apps/mcp-server/src/server.ts` exposes MCP stdio progressive-disclosure tools and lazily loads the embedder on first semantic search to keep handshake fast.
- `apps/worker/src/embed-loop.ts` expands compressed text before embedding so semantic search matches human intent rather than compressed grammar.
- `apps/cli/src/commands/search.ts` supports BM25-only or semantic rerank, with embedding fallback handling and latency notice.
- `apps/cli/src/commands/compress.ts` compresses files in place with backups and can expand compressed text.
- `apps/cli/src/commands/hook.ts` registers non-blocking hook entrypoints and maps hook names to Claude Code event names for additional context output.

## Installation and integration behavior

- Tool: Cavemem
- Primary intervention surface: Compressed cross-agent persistent memory with MCP/CLI hooks and semantic search
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Compressed cross-agent persistent memory with MCP/CLI hooks and semantic search
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Compressed cross-agent persistent memory with MCP/CLI hooks and semantic search
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation is present.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes/state, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Memory/reinjection authority. Avoid combining untested with Claude Mem, MEX reinjection, Omni/Engram, or other automatic memory surfaces without namespace and injection-order controls.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Compression/expansion can alter wording before embedding or recall.
- Embedding worker state and model/dimension changes affect search freshness.
- Hook context injection can duplicate other memory tools.

## Open questions and next review tasks

- [ ] Inspect core MemoryStore schema, compression format, and redaction behavior.
- [ ] Review eval corpus and compression benchmarks.
- [ ] Test multi-agent namespace separation and provider-billed savings.
