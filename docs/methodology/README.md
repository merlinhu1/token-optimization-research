# Methodology

This project uses a source-grounded, compatibility-first research workflow. Tool decisions require inspecting source code logic; README summaries, repository metadata, and integration-path discovery are lead-generation inputs, not decision evidence.

## Research workflow

1. **Discover** repositories and papers through GitHub search, web search, benchmark repositories, paper indexes, issue threads, community reports, and citation chaining.
2. **Classify** each artifact as `technique implementation`, `bundle`, `benchmark`, `measurement`, `research`, `primitive`, or `adjacent`.
3. **Create or update a dossier** for important tools under `docs/tool-dossiers/`. The dossier is the persistent record for source-level findings and open questions.
4. **Inspect source code logic** before using a tool in a qualified stack. Depending on tool type, inspect installer files, plugin manifests, hook scripts, MCP server code, runtime source, tests, benchmark harnesses, and raw benchmark outputs.
5. **Extract** mechanism, intervention surface, supported agents, state/caches, raw-output recovery, failure behavior, claimed savings, evidence type, caveats, and source URLs.
6. **Normalize** implementations into technique IDs in `data/techniques.json` and update `data/repositories.json` only when source-grounded evidence is sufficient.
7. **Assess compatibility** by mapping which buffer/control point each technique rewrites or owns.
8. **Evaluate** individual techniques with narrowly scoped experiments before comparing bundles.
9. **Synthesize** results into reports only after stating the evidence stage reached for each major tool.

## Evidence stages

| Stage | Required evidence | Permitted use |
|---|---|---|
| `lead` | Search result, catalog mention, README headline, or repository metadata only. | Backlog and discovery planning only; not a dossier and not decision evidence. |
| `source-logic` | Representative implementation files inspected; runtime transformations, state, fallbacks, compatibility boundaries, and failure modes interpreted. | Minimum stage for qualified stack recommendations and tool decisions. |
| `benchmark-audit` | Benchmark harness, tasks, scoring, token accounting, raw outputs, and exclusion/failure semantics inspected. | Evidence-weighted ranking. |
| `reproduction` | Independent or local persistent-workflow reproduction with complete provider-reported token use, execution integrity, structured verifier outcomes, treatment/isolation evidence, compact recoverable artifacts, and optional source review. | Scoped treatment evidence; recommendation strength depends on compatible replicate count and separately reported diagnostics. |

The full dossier process is defined in `docs/research/tool-research-strategy.md`. Open research tasks are tracked in `data/tool-analysis-backlog.json`.

## Evidence hierarchy

1. `peer-reviewed-research` — paper with methodology and review venue.
2. `external-reproducible-benchmark` — independent benchmark with scripts/data.
3. `external-pilot-benchmark` — independent but small-N or limited replication.
4. `reproducible-maintainer-benchmark` — maintainer benchmark with runnable scripts/data.
5. `maintainer-measurement` — maintainer numbers without full replication package.
6. `maintainer-claim` — stated claim without sufficient method.
7. `documented-mechanism` — mechanism documented, no quantitative result reviewed.
8. `monitoring-tool` — measures token usage without direct token reduction.

README text can identify a claim or installation path, but it is not sufficient evidence for behavior, limits, stack placement, or deployment quality. A tool remains a `lead` until source code logic has been inspected.

## Rules

- Preserve provenance: source URL, file path, review date, exact claim, and caveat.
- Separate extracted facts from interpretation.
- Separate operation-level token reduction from provider-reported workflow totals.
- Treat bundles as references; decompose them into techniques before analysis.
- Do not aggregate across projects unless scope, workflow, model condition, token boundary, and acceptance contract are compatible; report verifier and review diagnostics separately.
- Record negative and null results; they are first-class research findings.
- Persist partial findings in dossiers and backlog rather than compressing them into short report summaries.
- Do not promote README-only or integration-only findings into qualified stack recommendations; inspect source code logic first.
