# Tool dossier: Context-Engine-AI/Context-Engine

## Identity

- Repository: `Context-Engine-AI/Context-Engine`
- URL: https://github.com/Context-Engine-AI/Context-Engine
- Version/ref inspected: GitHub `HEAD` API or local shallow clone plus representative implementation files, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 2-integration/content review (repository appears to contain skills/tool-selection docs and site code, not inspected runtime MCP implementation)
- Stars at inspection: 395
- Forks at inspection: 53
- License: NOASSERTION
- Updated at: 2026-06-26T05:01:34Z

## Summary

Context Engine, as represented in this repository, provides skills and tool-selection guidance for hybrid semantic/lexical code search, symbol graph usage, and cross-repo/context-answer workflows. The inspected repository did not expose the claimed MCP runtime implementation.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-06-26-ten-more-tool-source-structures.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-06-26-ten-more-tool-code-inspection.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 55 files and 22 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `.codex/skills/context-engine/SKILL.md`
- `.codex/skills/context-engine/references/patterns.md`
- `.codex/skills/context-engine/references/tool-reference.md`
- `.skills/mcp-tool-selection/SKILL.md`
- `skills/context-engine/SKILL.md`
- `src/routes/$types.ts`
- `src/routes/+layout.svelte`
- `src/routes/+page.svelte`
- `src/routes/+page.ts`
- `src/routes/contact/+page.svelte`
- `package-lock.json`
- `package.json`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-ten-more-tool-code-inspection.json`.

- `skills/context-engine/SKILL.md` defines the primary workflow: start with `search`, use `symbol_graph` for direct relationships, and use `graph_query` only when available.
- `.codex/skills/context-engine/SKILL.md` duplicates the shared skill for Codex-specific installation/use.
- `.codex/skills/context-engine/references/tool-reference.md` is a quick reference for search, repo_search/code_search, batch_search, context_answer, symbol_graph, and graph_query.
- `src/routes/+page.ts` and `src/routes/+page.svelte` are Svelte site/page files rather than runtime MCP code.
- No representative server/indexer/compressor implementation was found in the inspected tree, so this dossier should not be treated as source-behavior validation of the underlying MCP service.

## Installation and integration behavior

- Tool: Context Engine
- Primary intervention surface: MCP retrieval tool-selection guidance and context-search skill layer
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: MCP retrieval tool-selection guidance and context-search skill layer
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: MCP retrieval tool-selection guidance and context-search skill layer
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation is present.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes/state, failed retrieval/compression, or increased correction turns.

## Compatibility notes

If deployed as skills only, it is behavior/tool-selection guidance that can coexist with one retrieval authority. If paired with a live Context Engine MCP server, it would become a retrieval authority overlapping with CodeGraph/Serena/Claude Context/etc.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- No runtime MCP source was found in this repository.
- Tool capabilities are described by skill docs and require live-schema verification.
- Cannot substantiate compression/search behavior until actual server implementation is inspected.

## Open questions and next review tasks

- [ ] Locate the runtime MCP/server repository or package if separate.
- [ ] Verify live tool schemas against the skill reference.
- [ ] Only promote to Level 3 after reading actual retrieval/ranking/server code.
