# Tool research strategy

This repository uses a staged research process for token-saving tools. README inspection is only the entry point. A tool is not considered deeply reviewed until its integration code, runtime behavior, benchmark method, and failure modes have been inspected and recorded in a persistent dossier.

## Review levels

| Level | Name | Required evidence | Permitted use |
|---:|---|---|---|
| 0 | Discovery lead | Search result, catalog mention, or README headline. | Backlog only. Do not use in recommendations. |
| 1 | Surface review | README plus repository metadata, license, supported agents, and claimed mechanism. | Candidate lists with explicit caveats. |
| 2 | Integration review | Installer/config/plugin/hook files inspected; supported-agent paths mapped; uninstall/failure behavior checked. | Compatibility analysis and provisional stack placement. |
| 3 | Source behavior review | Core implementation paths inspected; input/output transformations, state, caches, fallbacks, and safety boundaries mapped. | Qualified recommendation with implementation caveats. |
| 4 | Benchmark review | Benchmark harness, tasks, scoring, token accounting, and raw outputs inspected; maintainer claims separated from independent evidence. | Evidence-weighted ranking. |
| 5 | Reproduction review | A local or independent reproduction measures provider-billed tokens, turns, pass rate, latency, and quality on target workloads. | Deployment-grade recommendation. |

## Required dossier sections

Each important tool gets a persistent dossier under `docs/tool-dossiers/`. The dossier records:

- repository identity and version inspected;
- exact review level reached;
- installation and integration entry points;
- runtime behavior and intervention surfaces;
- state, caches, hooks, subprocesses, and network behavior;
- failure modes and quality risks;
- benchmark and evaluation evidence;
- compatibility with other surfaces;
- open questions and next inspection tasks.

Dossiers are cumulative. A later pass should update the existing dossier rather than replace it with a short summary.

## Source inspection requirements

A Level 2 or higher review must inspect files beyond the README. Depending on tool type, inspect:

| Tool type | Files to inspect |
|---|---|
| Agent plugin or skill | plugin manifests, hook configs, skill/rules files, activation scripts, uninstall path, tests. |
| MCP server | server entry point, tool schemas, transport setup, state/cache handling, error behavior, client config examples. |
| Shell-output compactor | hook scripts, command matcher/dispatcher, passthrough behavior, full-output recovery, tests. |
| Retrieval/index tool | indexer, watcher/sync behavior, staleness handling, query ranking, file-type support, tests. |
| Compression/proxy tool | compression pipeline, raw-content cache, retrieval path, provider transport, token accounting, quality checks. |
| Replacement agent | agent loop, tool budget policy, memory, repository map, model routing, benchmarks, rollback behavior. |

## Recommendation policy

- Reports must state the highest review level reached for each recommended stack component.
- A stack may be recommended provisionally before Level 5, but the report must label the recommendation as evidence-weighted rather than deployment-proven.
- README-only claims may describe candidates but cannot be the main basis for a qualified stack.
- In stack selection, use the term compatibility-safe directly: tools should not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, or state boundary. Do not label the report or stack category as conservative.
- Local environment availability must not be used as evidence of external quality.
- Maintainer benchmarks must be separated from independent reproductions.
- If deep review cannot be completed in one session, add or update the dossier and backlog rather than collapsing the finding into a shallow summary.

## Minimum evidence for stack compatibility

A stack compatibility claim requires:

1. documented installation/integration path for each component;
2. intervention-surface map showing non-overlap or controlled overlap;
3. failure-mode analysis for each hook/proxy/MCP/plugin boundary;
4. uninstall/disable path for each component;
5. at least one test or benchmark artifact reviewed for every behavior-changing component;
6. explicit open questions if source or benchmark inspection is incomplete.
