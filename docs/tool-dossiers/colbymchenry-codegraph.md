# Tool dossier: colbymchenry/codegraph

## Identity

- Repository: `colbymchenry/codegraph`
- URL: https://github.com/colbymchenry/codegraph
- Version/ref inspected: `1.5.0` release at commit `ea72e1b190921232aa7bd02e96bef5bbe4fe0ab6`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: ea72e1b190921232aa7bd02e96bef5bbe4fe0ab6
- Commit URL: https://github.com/colbymchenry/codegraph/commit/ea72e1b190921232aa7bd02e96bef5bbe4fe0ab6
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 1.5.0 release checkout from the batch release corpus, the same bytes its lanes install; representative CLI, context builder/formatter, search parser, DB queries, API, output-budget, and staleness tests inspected)

## Summary

CodeGraph builds a local code knowledge graph and provides task-oriented context construction, symbol/file search, graph traversal, and installer/daemon workflows. Source inspection confirms explicit context formatting, query parsing, output budgets, and staleness-signal tests.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository source tree | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Local shallow clone tree used to identify source, hook, MCP, test, benchmark, and runtime paths. |
| Runtime/source content | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Representative implementation files read from local clone with byte counts, SHA-256 prefixes, and behavior excerpts. |
| README/docs | README/docs and skill files where present. | README claims remain discovery evidence; source findings below control this evidence stage. |
| Tests/benchmarks | Test and benchmark paths identified; representative tests inspected where listed. | Benchmark-method review remains benchmark-audit work. |

## Initial source-structure finding

Tree inspection of the pinned `1.5.0` release checkout found 648 files: 400 source, 61 documentation, 211 test/benchmark, and 126 matching installer, host-integration, hook, plugin, skill, MCP, or configuration patterns.

Integration code — what actually performs a host install, and therefore what an install protocol must be written against:

- `scripts/agent-eval/offload-eval-cost.mjs`
- `scripts/agent-eval/offload-eval-effort.mjs`
- `scripts/agent-eval/offload-eval-hook.mjs`
- `scripts/agent-eval/offload-eval-judge.mjs`
- `scripts/agent-eval/offload-eval-metrics.mjs`
- `scripts/agent-eval/offload-eval-summarize.mjs`
- `scripts/agent-eval/parse-arms.mjs`
- `scripts/agent-eval/parse-run.mjs`
- `scripts/agent-eval/parse-session.mjs`
- `scripts/agent-eval/probe-context.mjs`
- `scripts/agent-eval/probe-explore.mjs`
- `scripts/agent-eval/probe-node.mjs`
- `scripts/agent-eval/probe-sweep.mjs`
- `scripts/agent-eval/probe-trace.mjs`
- `scripts/agent-eval/repro-concurrent-explore.mjs`
- `scripts/agent-eval/repro-daemon-clients.mjs`
- `scripts/agent-eval/seq-matrix.mjs`
- `site/astro.config.mjs`
- `site/src/content.config.ts`
- `src/bin/uninstall.ts`
- `src/installer/beta-signup.ts`
- `src/installer/clack.d.ts`
- `src/installer/config-writer.ts`
- `src/installer/index.ts`
- `src/installer/instructions-template.ts`
- `src/installer/targets/antigravity.ts`
- `src/installer/targets/claude.ts`
- `src/installer/targets/codex.ts`

Host-integration documentation shipped in the release:

- `.claude/skills/add-lang/SKILL.md`
- `.claude/skills/agent-eval/SKILL.md`
- `CLAUDE.md`
- `docs/design/agent-codegraph-adoption.md`
- `scripts/agent-eval/offload-eval.md`
- `site/src/content/docs/getting-started/configuration.md`
- `site/src/content/docs/getting-started/installation.md`
- `site/src/content/docs/reference/mcp-server.md`


## Code-detail inspection findings

### Pinned-release refresh (2026-08-28)

This dossier previously described `4077ed19b7d8`, read from GitHub HEAD on 2026-06-26. That is not the code any lane runs. `BATCH_RELEASES` pins this tool to the **1.5.0** release at `ea72e1b19092`, and the runner rewrites every lane path onto it, so the reading below is now taken from that pinned checkout instead. Inspecting the corpus checkout rather than a fresh network fetch keeps the reading reproducible after upstream HEAD moves again.

Upstream shipped **11 releases** between 2026-06-26 and this pin (`CHANGELOG.md`). A protocol derived from the older reading is how the 2026-08-22 review found five drifts and one blocking defect, so any integration step below is worth re-checking against the pinned release rather than trusted.

This project's changelog headings carry no descriptive titles, so which of those releases touched an install surface cannot be read off the headings. The most recent are:

- [1.5.0] - 2026-07-21
- [1.4.1] - 2026-07-10
- [1.4.0] - 2026-07-10
- [1.3.1] - 2026-07-09
- [1.3.0] - 2026-07-07
- [1.2.0] - 2026-07-02
- [1.1.6] - 2026-06-30
- [1.1.5] - 2026-06-30
- …and 3 further releases; see `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.

The official install guide this tool is evaluated against is `source/README.md` at sha256 `ef12f20aa127d8a5…` in the pinned release.

Evidence artifact: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.

- `src/bin/codegraph.ts` exposes install, init, index, sync, status, query, files, context, callers, callees, and impact commands.
- `src/context/index.ts` builds task context by combining full-text search, graph traversal, query-derived symbols, path scoring, and relevance signals.
- `src/context/formatter.ts` formats task context as compact Markdown or JSON, prioritizing entry points and limiting code blocks to key symbols.
- `src/search/query-parser.ts` parses field-qualified queries such as kind/name/path/language filters and composes filters with free text.
- `src/db/queries.ts` implements prepared graph/search queries with path/value heuristics and result scoring.
- `src/index.ts` wires indexing, graph traversal, context builder, file watcher/sync, and project directory state into the public API.
- `__tests__/explore-output-budget.test.ts` pins adaptive output budgets so explore results remain under inline tool-result ceilings for small/medium/large projects.
- `__tests__/mcp-staleness-banner.test.ts` verifies MCP responses warn when referenced files or project files are pending index sync.

## Installation and integration behavior

- Tool: CodeGraph
- Primary intervention surface: Code retrieval and graph-indexing authority exposed through CLI/MCP-oriented workflows
- Integration status: source and integration paths identified; source logic inspected for representative runtime files.
- Disable/uninstall path: partially inspected where representative files expose it; full host-by-host review remains open.
- Failure behavior if dependency is missing: the official Codex installer writes a bare `codegraph` command into Codex configuration; evaluations built from a pinned source checkout must expose that command on the actual model-runtime PATH, not merely call an absolute binary from controller probes. The deleted generation violated this requirement; the corrected canonical v1 generation gates on a container command-resolution probe and fresh protocol hashes.

## Runtime behavior

- Intervention surface: Code retrieval and graph-indexing authority exposed through CLI/MCP-oriented workflows
- Input captured: implementation-specific inputs are described in code-detail findings.
- Output emitted: implementation-specific outputs are described in code-detail findings.
- State/cache/files written: representative state and recovery behavior identified where present.
- Network/subprocess behavior: not exhaustively reviewed; benchmark/reproduction review remains required.
- Raw-output recovery path: recorded where present; otherwise open for benchmark-audit/reproduction review.
- Security/privacy considerations: host hooks, local state, indexes, memory, or runtime boundaries should be reviewed before sensitive deployment.

## Token-saving mechanism

- Addressable token surface: Code retrieval and graph-indexing authority exposed through CLI/MCP-oriented workflows
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation exists.
- Quality-preservation mechanism: partially identified via guards, budgets, tests, profile controls, or explicit caveats where present.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, extra tool calls, stale indexes, skipped rewrites, duplicate context authorities, correction turns, or increased latency.

## Compatibility notes

Code retrieval/indexing authority. It overlaps with Serena, SigMap, jcodemunch MCP, CocoIndex Code, Code Review Graph, LeanCTX retrieval, and Token Savior retrieval. Use one primary retrieval authority per stack.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Retrieval quality depends on index freshness, supported languages/framework extractors, and generated-file filtering.
- Daemon/watch state introduces stale-index and multi-repo boundary concerns.
- Output-budget tests constrain response size but do not prove task success or billed-token savings.
- benchmark-audit review of agent-eval scripts remains open.

## Open questions and next review tasks

- [ ] Review MCP tool schemas and daemon lifecycle more deeply.
- [ ] Run same-task retrieval comparisons against Serena, SigMap, jcodemunch, and LeanCTX.
- [ ] Inspect agent-eval benchmark raw outputs and scoring before ranking.
