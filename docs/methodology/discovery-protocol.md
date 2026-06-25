# Discovery Protocol

## Source classes

- GitHub repository metadata and README search.
- GitHub code search for exact phrases from seed catalogs.
- Awesome-lists for Claude Code, Codex, MCP, coding agents, and AI devtools.
- Benchmark repositories and live result dashboards.
- Academic search: arXiv, Semantic Scholar, ACL Anthology, ACM/IEEE where relevant.
- Product docs and blog posts for mechanism details.

## Search pattern

1. Start from known seed repositories and crawl their links.
2. Search exact phrases from claims and methodology sections.
3. Search by mechanism terms: `token saving`, `context compression`, `repo map`, `MCP trim`, `Claude Code token`, `Codex token`, `agentic token benchmark`.
4. Inspect README, docs, examples, benchmark scripts, and issue/discussion caveats.
5. Add record to `data/repositories.json` only after at least one source URL is reviewed.

## Minimum repository record

- `id`
- `name`
- `url`
- `kind`
- `summary`
- `mechanism`
- `technique_ids`
- `evidence_label`
- `reported_result`
- `main_caveat`
- `sources`
- `reviewed_at`

## Review-depth levels

- `surface`: README and repository metadata only.
- `moderate`: README plus docs/examples/benchmark files.
- `deep`: source code, benchmark scripts, reproduction attempt, or transcript review.
