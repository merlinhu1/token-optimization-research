# Methodology

This project uses a source-grounded, compatibility-first research workflow. Tool research must progress beyond README summaries into persistent source, integration, behavior, benchmark, and reproduction records.

## Research workflow

1. **Discover** repositories and papers through GitHub search, web search, benchmark repositories, paper indexes, issue threads, community reports, and citation chaining.
2. **Classify** each artifact as `technique implementation`, `bundle`, `benchmark`, `measurement`, `research`, `primitive`, or `adjacent`.
3. **Create or update a dossier** for important tools under `docs/tool-dossiers/`. The dossier is the persistent record for source-level findings and open questions.
4. **Inspect beyond the README** before using a tool in a qualified stack. Depending on tool type, inspect installer files, plugin manifests, hook scripts, MCP server code, runtime source, tests, benchmark harnesses, and raw benchmark outputs.
5. **Extract** mechanism, intervention surface, supported agents, state/caches, raw-output recovery, failure behavior, claimed savings, evidence type, caveats, and source URLs.
6. **Normalize** implementations into technique IDs in `data/techniques.json` and update `data/repositories.json` only when source-grounded evidence is sufficient.
7. **Assess compatibility** by mapping which buffer/control point each technique rewrites or owns.
8. **Evaluate** individual techniques with narrowly scoped experiments before comparing bundles.
9. **Synthesize** results into reports only after stating the review level reached for each major tool.

## Review levels

| Level | Name | Required evidence | Permitted use |
|---:|---|---|---|
| 0 | Discovery lead | Search result, catalog mention, or README headline. | Backlog only. |
| 1 | Surface review | README plus repository metadata, license, supported agents, and claimed mechanism. | Candidate lists with explicit caveats. |
| 2 | Integration review | Installer/config/plugin/hook files inspected; supported-agent paths mapped. | Provisional compatibility analysis. |
| 3 | Source behavior review | Core implementation paths inspected; transformations, state, fallbacks, and boundaries mapped. | Qualified recommendation with implementation caveats. |
| 4 | Benchmark review | Benchmark harness, tasks, scoring, token accounting, and raw outputs inspected. | Evidence-weighted ranking. |
| 5 | Reproduction review | Independent or local reproduction on target workloads with provider-billed accounting. | Deployment-grade recommendation. |

The full dossier process is defined in `docs/research/tool-research-strategy.md`. Open research tasks are tracked in `data/tool-analysis-backlog.json`.

## Evidence hierarchy

1. `peer-reviewed-research` — paper with methodology and review venue.
2. `external-reproducible-benchmark` — independent benchmark with scripts/data.
3. `external-pilot-benchmark` — independent but small-N or limited replication.
4. `reproducible-maintainer-benchmark` — maintainer benchmark with runnable scripts/data.
5. `maintainer-measurement` — maintainer numbers without full replication package.
6. `maintainer-claim` — stated claim without sufficient method.
7. `documented-mechanism` — mechanism documented, no quantitative result reviewed.
8. `monitoring-tool` — measures usage/cost without direct token reduction.

README text can identify a claim or installation path, but it is not sufficient evidence for behavior, limits, or deployment quality.

## Rules

- Preserve provenance: source URL, file path, review date, exact claim, and caveat.
- Separate extracted facts from interpretation.
- Separate operation-level token reduction from provider-billed task totals.
- Treat bundles as references; decompose them into techniques before analysis.
- Do not rank across projects unless scope, workload, model, pricing, and quality gates are comparable.
- Record negative and null results; they are first-class research findings.
- Persist partial findings in dossiers and backlog rather than compressing them into short report summaries.
- Do not promote README-only findings into qualified stack recommendations.
