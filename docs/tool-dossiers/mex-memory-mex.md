# Tool dossier: mex-memory/mex

## Identity

- Repository: `mex-memory/mex`
- URL: https://github.com/mex-memory/mex
- Version/ref inspected: GitHub `HEAD` API or local shallow clone plus representative implementation files, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 3-source-behavior (representative CLI, drift, event, and heartbeat files inspected)
- Stars at inspection: 1,140
- Forks at inspection: 65
- License: MIT
- Updated at: 2026-06-26T04:27:36Z

## Summary

MEX is a project-memory scaffold and drift-checking CLI for AI coding agents. It stores structured context files and verifies that memory/config surfaces stay synchronized across tools.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-06-26-ten-more-tool-source-structures.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-06-26-ten-more-tool-code-inspection.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 137 files and 98 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `src/cli-tools.ts`
- `src/cli.ts`
- `src/config.ts`
- `src/doctor.ts`
- `src/drift/checkers/broken-link.ts`
- `src/drift/checkers/command.ts`
- `src/drift/checkers/cross-file.ts`
- `src/drift/checkers/dependency.ts`
- `src/drift/checkers/edges.ts`
- `src/drift/checkers/index-sync.ts`
- `src/drift/checkers/path.ts`
- `src/drift/checkers/script-coverage.ts`
- `src/drift/checkers/staleness.ts`
- `src/drift/checkers/todo-fixme.ts`
- `src/drift/checkers/tool-config-sync.ts`
- `src/drift/claims.ts`
- `src/drift/frontmatter.ts`
- `src/drift/index.ts`
- `src/drift/scoring.ts`
- `src/events.ts`
- `src/feedback/index.ts`
- `src/git.ts`
- `src/global-config.ts`
- `src/heartbeat.ts`
- `src/index.ts`
- `src/markdown.ts`
- `src/paths.ts`
- `src/pattern/index.ts`
- `src/reporter.ts`
- `src/scanner/entry-points.ts`
- `src/scanner/folder-tree.ts`
- `src/scanner/index.ts`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-ten-more-tool-code-inspection.json`.

- `src/cli.ts` implements command parsing and loads/backfills scaffold identity while keeping config lookup mostly read-oriented for embedders.
- `src/drift/index.ts` finds scaffold files, parses frontmatter claims, and runs multiple drift checkers over context files.
- `src/drift/checkers/tool-config-sync.ts` compares installed tool config files for identical content, intentionally excluding format-different configs.
- `src/events.ts` appends structured decision/note/risk/todo events with optional trace/source/status fields.
- `src/heartbeat.ts` checks stale memory and cleanup cadence using configured scaffold patterns and default retention thresholds.

## Installation and integration behavior

- Tool: MEX
- Primary intervention surface: Persistent project memory scaffold, drift detection, and multi-tool config synchronization
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Persistent project memory scaffold, drift detection, and multi-tool config synchronization
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Persistent project memory scaffold, drift detection, and multi-tool config synchronization
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation is present.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes/state, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Memory/scaffold governance surface. It can coexist with retrieval tools but overlaps with automatic memory reinjection tools if both inject or maintain project memory independently.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Primarily a scaffold/governance tool rather than automatic token compression.
- Savings depend on agents using compact context files instead of rediscovering project facts.
- Drift checks do not prove memory relevance or provider-billed savings.

## Open questions and next review tasks

- [ ] Inspect setup/install paths and generated tool configs.
- [ ] Review telemetry/privacy defaults.
- [ ] Measure task-restart token savings with and without scaffold context.
