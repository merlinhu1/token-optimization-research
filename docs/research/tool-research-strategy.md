# Tool research strategy

This repository uses a source-code-first research process for token-saving tools. README inspection and integration-path discovery are lead generation only. A tool does not receive a decision-bearing dossier until representative source code logic, runtime behavior, and failure modes have been inspected and recorded.

## Evidence stages

| Stage | Required evidence | Permitted use |
|---|---|---|
| `lead` | Search result, catalog mention, README headline, repository metadata, or integration-path notes without source-logic interpretation. | Backlog and dossier planning only. Do not use in recommendations. |
| `source-logic` | Representative implementation files inspected; input/output transformations, state, caches, fallbacks, safety boundaries, and compatibility implications mapped. | Minimum stage for qualified recommendations and stack decisions. |
| `benchmark-audit` | Benchmark harness, tasks, scoring, token accounting, raw outputs, and maintainer/independent evidence boundaries inspected. | Evidence-weighted ranking. |
| `reproduction` | Local or independent persistent-workflow reproduction measures provider-reported tokens, structured task correctness, treatment/isolation validity, and independent quality. | Scoped treatment evidence; recommendation strength depends on compatible replicate count. |

## Required dossier sections

Each important tool gets a persistent dossier under `docs/tool-dossiers/`. The dossier records:

- repository identity and version inspected;
- exact evidence stage reached;
- installation and integration entry points;
- runtime behavior and intervention surfaces;
- state, caches, hooks, subprocesses, and network behavior;
- failure modes and quality risks;
- benchmark and evaluation evidence;
- compatibility with other surfaces;
- open questions and next inspection tasks.

Dossiers are cumulative. A later pass should update the existing dossier rather than replace it with a short summary.

## Source inspection requirements

A `source-logic` dossier must inspect representative source code logic beyond README and integration files. Depending on tool type, inspect:

| Tool type | Files to inspect |
|---|---|
| Agent plugin or skill | plugin manifests, hook configs, skill/rules files, activation scripts, uninstall path, tests. |
| MCP server | server entry point, tool schemas, transport setup, state/cache handling, error behavior, client config examples. |
| Shell-output compactor | hook scripts, command matcher/dispatcher, passthrough behavior, full-output recovery, tests. |
| Retrieval/index tool | indexer, watcher/sync behavior, staleness handling, query ranking, file-type support, tests. |
| Compression/proxy tool | compression pipeline, raw-content cache, retrieval path, provider transport, token accounting, quality checks. |
| Replacement agent | agent loop, tool budget policy, memory, repository map, model routing, benchmarks, rollback behavior. |

## Coverage and recommendation policy

- Reports must state the highest evidence stage reached for each recommended stack component.
- A repository that does not provide auditable versioning for the inspected source is not a valid candidate for recommendation, stack construction, benchmark-audit, or reproduction until a pinned source snapshot is available.
- Dossiers marked `unpinned-historical-inspection` may preserve historical notes, but they are candidate-ineligible until refreshed against an immutable commit.
- A stack may be recommended provisionally before reproduction, but the report must label the recommendation as evidence-weighted rather than deployment-proven.
- README-only and integration-only claims may describe leads but cannot be the basis for a qualified stack.
- Before a report claims a candidate set is complete, primary, recommended, or representative, run a coverage audit using `docs/methodology/discovery-protocol.md` and preserve the query artifact under `sources/discovery/`.
- Stack selection must not be based only on the subset of tools already inspected. If high-signal leads remain at `lead`, either inspect them to `source-logic` before ranking or state that the ranking is coverage-limited.
- In stack selection, use the term compatibility-safe directly: tools should not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, or state boundary. Do not use ambiguous stack labels; use compatibility-safe terminology directly.
- Local environment availability must not be used as evidence of external quality.
- Maintainer benchmarks must be separated from independent reproductions.
- If source-logic inspection cannot be completed in one session, keep the tool as a `lead` in the backlog rather than creating a decision-bearing dossier from shallow evidence.

## Minimum evidence for stack compatibility

A stack compatibility claim requires:

1. documented installation/integration path for each component;
2. intervention-surface map showing non-overlap or controlled overlap;
3. failure-mode analysis for each hook/proxy/MCP/plugin boundary;
4. uninstall/disable path for each component;
5. at least one test or benchmark artifact reviewed for every behavior-changing component;
6. explicit open questions if benchmark-audit or reproduction work is incomplete.
