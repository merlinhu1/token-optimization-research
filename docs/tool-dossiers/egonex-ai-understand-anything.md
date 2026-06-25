# Tool dossier: Egonex-AI/Understand-Anything

## Identity

- Repository: `Egonex-AI/Understand-Anything`
- URL: https://github.com/Egonex-AI/Understand-Anything
- Version/ref inspected: local shallow clone `54754a6f9705`, 2026-06-29
- Snapshot status: pinned-commit
- Commit inspected: 54754a6f9705
- Commit URL: https://github.com/Egonex-AI/Understand-Anything/commit/54754a6f9705
- Source artifact path: `sources/discovery/2026-06-29-graph-leads-a-source-logic.json`
- Date inspected: 2026-06-29
- Evidence stage: source-logic (local source inspection of installer, plugin exports, project scanner, structural extractor, core search/schema/parser logic, and representative tests)
- License: MIT (`package.json`)

## Summary

Understand-Anything is a skills/plugin workspace for generating and querying codebase knowledge graphs and dashboards. Source inspection confirms deterministic helper scripts for file enumeration and structural extraction, a core graph schema/sanitizer, Fuse-based search, prompt-context builders, and installer symlink behavior across agent hosts. Evidence is source-logic only; no benchmark-audit was performed.

## Evidence inventory

| Evidence type | Files inspected | Notes |
|---|---|---|
| Manifest/entrypoints | `package.json`, `understand-anything-plugin/package.json`, `understand-anything-plugin/src/index.ts` | Root workspace and plugin package; exports prompt/context builders. |
| Installer/integration | `install.sh` | Clones/updates repo, symlinks skills per host, links universal plugin root, includes uninstall/update paths. |
| Deterministic scan/extract | `skills/understand/scan-project.mjs`, `skills/understand/extract-structure.mjs` | Replaces some LLM-side file enumeration/regex extraction with Node scripts and core analyzers. |
| Core graph/search/schema | `packages/core/src/search.ts`, `packages/core/src/plugins/tree-sitter-plugin.ts`, `packages/core/src/schema.ts` | Fuse search, tree-sitter WASM loading, graph sanitization/autofix aliases. |
| Context/test coverage | `src/context-builder.ts`, `src/__tests__/context-builder.test.ts` | Query-relevant node search, 1-hop expansion, markdown prompt formatting, tests for bounded matches and relationships. |

## Installation and integration behavior

- Root `package.json` is a pnpm workspace; plugin package `@understand-anything/skill` exports built JS from `dist/index.js`.
- `install.sh` clones or updates into `$HOME/.understand-anything/repo`, then symlinks all skill directories into a host-specific target.
- Platform mappings include Gemini/Codex/OpenCode/Pi/Vibe/VS Code/Trae/Kiro per-skill style and OpenClaw/Antigravity/Hermes/Cline/Kimi folder style.
- The installer creates `$HOME/.understand-anything-plugin` as a universal plugin-root symlink unless already present.
- For Kiro, install dynamically writes `$HOME/.kiro/agents/understand.json` with prompt/resources derived from repository agent markdown files.

## Runtime behavior

- `scan-project.mjs` enumerates files via `git ls-files` when possible or sorted filesystem walk fallback, applies `.understandignore` through core ignore filters, detects languages/categories, counts lines, estimates complexity, and writes JSON.
- `extract-structure.mjs` loads `@understand-anything/core`, initializes `TreeSitterPlugin` plus non-code parsers, reads batch files, emits functions/classes/exports/sections/definitions/call graph data, and degrades per file when analysis fails.
- `TreeSitterPlugin` loads web-tree-sitter WASM grammars from language configs, registers builtin language extractors, and skips unavailable grammars rather than hard failing.
- `SearchEngine` uses Fuse over node name/tags/summary/languageNotes, turns whitespace-separated query terms into extended-search OR clauses, optionally filters node types, and applies a result limit.
- `buildChatContext` searches graph nodes, expands one hop through edges, collects layers containing the resulting nodes, and formats project/layer/node/edge context as markdown.

## Token-saving mechanism

- Addressable token surface: project onboarding/explanation/chat prompts over codebase knowledge graphs.
- Reduction method: deterministic scanners/extractors create structured graph inputs; chat/explain/onboard builders select relevant nodes/edges/layers instead of including broad source files.
- Quality-preservation mechanisms seen in source: schema sanitization/autofix aliases, parser graceful degradation, result limits, 1-hop relationship expansion, and tests asserting relevant nodes/edges/layers appear.
- Savings may not translate to provider-billed reductions if graph generation requires substantial LLM work, if extracted context is too coarse, or if agents need extra turns to correct missing source detail.

## Benchmarks and claims

No benchmark-audit was performed. Dashboard benchmark scripts and tests exist in the tree, but benchmark harness/scoring/raw output were not inspected. Do not treat README or package descriptions as measured token-saving evidence.

## Compatibility notes

Understand-Anything overlaps with graph/code retrieval, project onboarding, and dashboard authorities. In a compatibility-safe stack, use it as one primary graph/onboarding context source rather than combining blindly with Graphify, SwarmVault, MaestroGraph, CodeGraph, Serena, or other retrieval MCP servers.

## Failure modes and limits

- Tree-sitter structural analysis depends on available WASM grammar packages and language extractor coverage.
- Non-code/language gaps are handled by skip/degraded output, which can lower graph completeness.
- Installer uses symlinks and a repo clone under the user home; host skill discovery and symlink behavior may vary by platform.
- Query context is selected by Fuse text matching plus 1-hop expansion, not semantic embeddings in the inspected path.
- Source inspection did not verify end-to-end generated graph quality or dashboard behavior.

## Open questions

- How much of the final graph is deterministic extraction versus LLM-authored analysis in a real project run?
- Which agent hosts consume the skills without extra manual configuration beyond symlinks?
- How are stale graph artifacts detected and refreshed during normal use?

## Next review tasks

- [ ] Run the scanner/extractor on a fixed fixture and inspect generated graph JSON.
- [ ] Inspect dashboard aggregation/layout scripts only if dashboard performance claims become relevant.
- [ ] Compare chat prompt context against full-source and other graph retrieval baselines with provider-billed accounting.
