# Tool dossier: thedotmack/claude-mem

## Identity

- Repository: `thedotmack/claude-mem`
- URL: https://github.com/thedotmack/claude-mem
- Version/ref inspected: local shallow clone `cbdce2d676a9`, 2026-07-01
- Snapshot status: pinned-commit
- Commit inspected: cbdce2d676a9646b73dc236eebb53e4019870dcf
- Commit URL: https://github.com/thedotmack/claude-mem/commit/cbdce2d676a9646b73dc236eebb53e4019870dcf
- Source artifact path: `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json`
- Date inspected: 2026-07-01
- Evidence stage: source-logic (fresh pinned shallow clone; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection: 84,353
- Forks at inspection: 7,275
- License: Apache-2.0
- Updated at: 2026-06-26T07:42:49Z

## Summary

Claude Mem captures agent session observations, summarizes/compresses them, and injects relevant prior context into future agent sessions across multiple agent adapters.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` | Used to identify installer, plugin, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime source | `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json` | Representative implementation files fetched from GitHub HEAD with SHA-256 prefixes and behavior excerpts. |
| README/docs | README path identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 889 files and 597 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `src/services/context-generator.ts`
- `src/services/context/ContextBuilder.ts`
- `src/services/context/ContextConfigLoader.ts`
- `src/services/context/ObservationCompiler.ts`
- `src/services/context/TokenCalculator.ts`
- `src/services/context/formatters/AgentFormatter.ts`
- `src/services/context/formatters/HumanFormatter.ts`
- `src/services/context/sections/FooterRenderer.ts`
- `src/services/context/sections/HeaderRenderer.ts`
- `src/services/context/sections/SummaryRenderer.ts`
- `src/services/context/sections/TimelineRenderer.ts`
- `src/services/context/types.ts`
- `src/cli/handlers/context.ts`
- `src/cli/handlers/file-context.ts`
- `src/cli/handlers/file-edit.ts`
- `src/cli/handlers/index.ts`
- `src/cli/handlers/observation.ts`
- `src/cli/handlers/session-init.ts`
- `src/cli/handlers/summarize.ts`
- `src/cli/handlers/user-message.ts`
- `src/servers/mcp-server.ts`
- `plugin/scripts/context-generator.cjs`
- `plugin/scripts/mcp-server.cjs`
- `plugin/scripts/server-beta-service.cjs`
- `.claude/reports/test-audit-2026-01-05.md`
- `Dockerfile.test-installer`
- `cursor-hooks/.gitignore`
- `cursor-hooks/CONTEXT-INJECTION.md`
- `cursor-hooks/INTEGRATION.md`
- `cursor-hooks/PARITY.md`
- `cursor-hooks/QUICKSTART.md`
- `cursor-hooks/README.md`
- `cursor-hooks/REVIEW.md`
- `cursor-hooks/STANDALONE-SETUP.md`
- `cursor-hooks/cursorrules-template.md`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`.

### Fresh pinned-source refresh

The 2026-07-01 refresh pins the inspected source to `cbdce2d676a9646b73dc236eebb53e4019870dcf` and records a fresh tree plus selected implementation excerpts in `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` and `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`. Representative files captured for this refresh include `src/services/context-generator.ts`, `src/services/context/ContextBuilder.ts`, `src/services/context/ContextConfigLoader.ts`, `src/services/context/ObservationCompiler.ts`, `src/services/context/TokenCalculator.ts`, `src/services/context/formatters/AgentFormatter.ts`. Treat benchmark, savings, and deployment claims below as source-logic only unless a benchmark-audit or reproduction artifact is explicitly cited.


- `src/services/context/ContextBuilder.ts` builds injected context from observations/summaries and computes token economics before rendering context output.
- `src/services/context/ObservationCompiler.ts` queries observations and summaries from a session store, including multi-project observation retrieval and recorded discovery-token fields.
- `src/services/context/TokenCalculator.ts` estimates read tokens from observation size and compares them to stored `discovery_tokens`, making savings an explicit estimate rather than only a prose claim.
- `src/cli/handlers/observation.ts` handles PostToolUse observation capture, validates required `cwd`/tool information, skips excluded projects, and dispatches observations to a worker/runtime path.
- `src/servers/mcp-server.ts` implements MCP protocol handling and deliberately redirects console output to stderr to protect MCP JSON framing.

## Installation and integration behavior

- Tool: Claude Mem
- Primary intervention surface: Persistent context capture, summarization, memory retrieval, and context reinjection
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative runtime files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Persistent context capture, summarization, memory retrieval, and context reinjection
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Persistent context capture, summarization, memory retrieval, and context reinjection
- Reduction method: implementation-level mechanism identified in representative source files.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Memory/context owner. Do not combine casually with another automatic long-term-memory/context-injection system unless memory namespaces, injection precedence, and duplicate summaries are tested.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Savings depend on relevance of retrieved memories and summarization quality.
- Observation capture can introduce privacy/storage concerns.
- Token savings estimates use approximate token economics and require provider-billed reproduction.

## Open questions and next review tasks

- [ ] Review storage schema, retention, redaction, and multi-agent namespace isolation.
- [ ] Inspect summarization provider prompts and failure behavior.
- [ ] Benchmark future-session task success and billed-token effects.
