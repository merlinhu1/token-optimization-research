# Tool dossier: vincentkoc/tokenjuice

## Identity

- Repository: `vincentkoc/tokenjuice`
- URL: https://github.com/vincentkoc/tokenjuice
- Version/ref inspected: local shallow clone `49bdcf175583`, 2026-07-01
- Snapshot status: pinned-commit
- Commit inspected: 49bdcf1755833ff1e02e44e6e7fe91c0fb44c16e
- Commit URL: https://github.com/vincentkoc/tokenjuice/commit/49bdcf1755833ff1e02e44e6e7fe91c0fb44c16e
- Source artifact path: `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json`
- Date inspected: 2026-07-01
- Evidence stage: source-logic (fresh pinned shallow clone; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection: 469
- Forks at inspection: 48
- License: MIT
- Updated at: 2026-06-26T03:48:05Z

## Summary

TokenJuice compacts command outputs using rule-driven reducers and installs host integrations across many agent frameworks.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 793 files and 603 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `src/core/analysis.ts`
- `src/core/artifacts.ts`
- `src/core/builtin-rules.generated.ts`
- `src/core/classify.ts`
- `src/core/cli-client.ts`
- `src/core/command-identity.ts`
- `src/core/command-match.ts`
- `src/core/command-shell.ts`
- `src/core/command.ts`
- `src/core/compaction-metadata.ts`
- `src/core/env.ts`
- `src/core/execution-input.ts`
- `src/core/fixtures.ts`
- `src/core/github-actions-summary.ts`
- `src/core/integrations/compact-bash-result.ts`
- `src/core/integrations/rewrite-policy.ts`
- `src/core/inventory-safety.ts`
- `src/core/json-protocol.ts`
- `src/core/reduce-formatters.ts`
- `src/core/reduce-inspection-summary.ts`
- `src/core/reduce-utils.ts`
- `src/core/reduce.ts`
- `src/core/rules.ts`
- `src/core/source.ts`
- `src/core/text.ts`
- `src/core/time.ts`
- `src/core/validate-rules.ts`
- `src/core/wrap.ts`
- `src/hosts/claude-code/index.ts`
- `.agents/skills/autoreview/scripts/autoreview`
- `.agents/skills/autoreview/scripts/test-review-harness`
- `scripts/bench.mjs`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`.

### Fresh pinned-source refresh

The 2026-07-01 refresh pins the inspected source to `49bdcf1755833ff1e02e44e6e7fe91c0fb44c16e` and records a fresh tree plus selected implementation excerpts in `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` and `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`. Representative files captured for this refresh include `src/core/analysis.ts`, `src/core/artifacts.ts`, `src/core/builtin-rules.generated.ts`, `src/core/classify.ts`, `src/core/cli-client.ts`, `src/core/command-identity.ts`. Treat benchmark, savings, and deployment claims below as source-logic only unless a benchmark-audit or reproduction artifact is explicitly cited.


- `src/core/reduce.ts` implements core reduction logic for command output and compaction metadata.
- `src/core/command-match.ts` identifies commands and command variants for rule matching.
- `src/core/integrations/compact-bash-result.ts` integrates compaction into Bash/tool-result workflows.
- `src/core/rules.ts` handles rule definitions/validation for command-specific reduction behavior.
- `src/hosts/claude-code/index.ts` reads/writes Claude Code hook settings and detects already-wrapped hook commands.

## Installation and integration behavior

- Tool: TokenJuice
- Primary intervention surface: Terminal-heavy command-output compaction and host hook/wrap integration
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Terminal-heavy command-output compaction and host hook/wrap integration
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Terminal-heavy command-output compaction and host hook/wrap integration
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation is present.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes/state, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Terminal-output compaction owner. It overlaps with RTK, Lowfat, Snip, xcsift for Xcode output, and LeanCTX shell compression.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Large host-integration surface raises install/uninstall and hook-order risks.
- Rule-driven reduction requires fidelity tests for each command family.
- Compaction can affect downstream shell-pipeline expectations if used at the wrong boundary.

## Open questions and next review tasks

- [ ] Inspect built-in generated rule catalog and safety/fallback behavior.
- [ ] Review bench script and fixture coverage.
- [ ] Test hook ordering against RTK/Snip/Claude Code native hooks.
