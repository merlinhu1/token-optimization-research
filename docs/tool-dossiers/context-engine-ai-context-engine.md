# Tool dossier: Context-Engine-AI/Context-Engine

## Identity

- Repository: `Context-Engine-AI/Context-Engine`
- URL: https://github.com/Context-Engine-AI/Context-Engine
- Version/ref inspected: local shallow clone `b1dc3ef3ff4a`, 2026-06-26
- Snapshot status: pinned-commit
- Commit inspected: b1dc3ef3ff4a
- Commit URL: https://github.com/Context-Engine-AI/Context-Engine/commit/b1dc3ef3ff4a
- Source artifact path: `sources/discovery/2026-06-26-source-logic-uplift-source-structures.json`
- Date inspected: 2026-06-26
- Evidence stage: source-logic of inspected repository (local shallow clone; package/site/skill files inspected; no runtime MCP implementation found in this repository)

## Summary

Context Engine, as represented by this repository, ships skill and tool-selection guidance for code search workflows plus a Svelte static site. Source inspection found no server/indexer/ranker/runtime MCP implementation in the inspected tree, so it should not be recommended as a runtime token-saving component from this repository alone.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository source tree | `sources/discovery/2026-06-26-source-logic-uplift-source-structures.json` | Local shallow clone tree used to identify source, hook, MCP, test, benchmark, and runtime paths. |
| Runtime/source content | `sources/discovery/2026-06-26-source-logic-uplift-code-inspection.json` | Representative implementation files read from local clone with byte counts, SHA-256 prefixes, and behavior excerpts. |
| README/docs | README/docs and skill files where present. | README claims remain discovery evidence; source findings below control this evidence stage. |
| Tests/benchmarks | Test and benchmark paths identified; representative tests inspected where listed. | Benchmark-method review remains benchmark-audit work. |

## Initial source-structure finding

Local tree inspection found 55 files and 23 files matching integration, source, test, benchmark, hook, MCP, or documentation patterns. Relevant paths include:

- `.skills/mcp-tool-selection/SKILL.md`
- `skills/context-engine/SKILL.md`
- `.codex/skills/context-engine/SKILL.md`
- `.codex/skills/context-engine/references/tool-reference.md`
- `.codex/skills/context-engine/references/patterns.md`
- `src/routes/+layout.svelte`
- `src/routes/+page.svelte`
- `src/routes/+page.ts`
- `src/routes/$types.ts`
- `src/routes/contact/+page.svelte`
- `package.json`
- `vite.config.ts`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-source-logic-uplift-code-inspection.json`.

- `package.json` identifies a Svelte/Vite application with web dependencies rather than a runtime MCP server package.
- `skills/context-engine/SKILL.md` provides workflow guidance: start with `search`, use `symbol_graph` for direct relationships, use `graph_query` only when available, and treat public V1 `include_memories=true` as compatibility-only.
- `.codex/skills/context-engine/references/tool-reference.md` is explicitly a quick reference rather than canonical live tool schema, listing expected search/context/symbol tools.
- `src/routes/+page.svelte` implements form/video/landing-page UI behavior rather than retrieval runtime behavior.
- `src/routes/+page.ts` sets static prerendering for the route.
- `vite.config.ts` configures SvelteKit/Vite only.

## Installation and integration behavior

- Tool: Context Engine
- Primary intervention surface: Skill/tool-selection guidance and static marketing/documentation site, not a validated runtime retrieval implementation in this repo
- Integration status: source and integration paths identified; source logic inspected for representative runtime files.
- Disable/uninstall path: partially inspected where representative files expose it; full host-by-host review remains open.
- Failure behavior if dependency is missing: partially inspected in representative code/tests; complete deployment failure-mode review remains open.

## Runtime behavior

- Intervention surface: Skill/tool-selection guidance and static marketing/documentation site, not a validated runtime retrieval implementation in this repo
- Input captured: implementation-specific inputs are described in code-detail findings.
- Output emitted: implementation-specific outputs are described in code-detail findings.
- State/cache/files written: representative state and recovery behavior identified where present.
- Network/subprocess behavior: not exhaustively reviewed; benchmark/reproduction review remains required.
- Raw-output recovery path: recorded where present; otherwise open for benchmark-audit/reproduction review.
- Security/privacy considerations: host hooks, local state, indexes, memory, or runtime boundaries should be reviewed before sensitive deployment.

## Token-saving mechanism

- Addressable token surface: Skill/tool-selection guidance and static marketing/documentation site, not a validated runtime retrieval implementation in this repo
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation exists.
- Quality-preservation mechanism: partially identified via guards, budgets, tests, profile controls, or explicit caveats where present.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, extra tool calls, stale indexes, skipped rewrites, duplicate context authorities, correction turns, or increased latency.

## Compatibility notes

As inspected, this repository is not a runtime retrieval authority. Its skill guidance can coexist with one actual retrieval engine only if it points to live tools already installed elsewhere. Do not include it as a stack component until a runtime package/repository is located and inspected.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- No runtime MCP server, indexer, search implementation, or ranking logic was found in this repository.
- Claims in skill docs require live schema and implementation verification elsewhere.
- It remains useful as evidence about desired workflow semantics, not runtime token-saving behavior.

## Open questions and next review tasks

- [ ] Locate any separate Context Engine runtime package/repository if it exists.
- [ ] Verify live MCP tool schemas and implementation code before including in stack candidates.
- [ ] Keep excluded from recommended runtime stacks until runtime code is inspected.
