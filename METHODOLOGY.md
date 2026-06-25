# Methodology

This project uses a source-grounded, compatibility-first research workflow.

## Research workflow

1. **Discover** repositories and papers through GitHub search, web search, awesome-lists, benchmark repos, paper indexes, and citation chaining.
2. **Classify** each artifact as `technique implementation`, `bundle`, `benchmark`, `measurement`, `research`, `primitive`, or `adjacent`.
3. **Extract** mechanism, intervention surface, supported agents, claimed savings, evidence type, caveats, and raw source URLs.
4. **Normalize** implementations into technique IDs in `data/techniques.json`.
5. **Assess compatibility** by asking which buffer/control point each technique rewrites or owns.
6. **Evaluate** individual techniques with narrowly scoped experiments before comparing bundles.
7. **Synthesize** results into research papers, standards, and repeatable prompts.

## Evidence hierarchy

1. `peer-reviewed-research` — paper with methodology and review venue.
2. `external-reproducible-benchmark` — independent benchmark with scripts/data.
3. `external-pilot-benchmark` — independent but small-N or limited replication.
4. `reproducible-maintainer-benchmark` — maintainer benchmark with runnable scripts/data.
5. `maintainer-measurement` — maintainer numbers without full replication package.
6. `maintainer-claim` — stated claim without sufficient method.
7. `documented-mechanism` — mechanism documented, no quantitative result reviewed.
8. `monitoring-tool` — measures usage/cost without direct token reduction.

## Rules

- Preserve provenance: source URL, review date, exact claim, and caveat.
- Separate operation-level token reduction from provider-billed task totals.
- Treat bundles as references; decompose them into techniques before analysis.
- Do not rank across projects unless scope, workload, model, pricing, and quality gates are comparable.
- Record negative and null results; they are first-class research findings.
