# Discovery Protocol

## Purpose

Discovery must minimize blind spots before the repository makes stack-selection claims. The `safishamsi/graphify` miss showed that seed-catalog search plus source-inspection depth can bias the repository toward already-known tools. A tool can remain non-decision-bearing, but high-signal leads must still be visible in `data/repositories.json` and `data/tool-analysis-backlog.json`.

## Source classes

- GitHub repository metadata, README search, and topic/description search.
- GitHub code search for exact phrases from seed catalogs and high-signal discovered repositories.
- Awesome-lists, registries, and curated catalogs for Claude Code, Codex, MCP, coding agents, AI devtools, GraphRAG, code intelligence, and agent memory.
- Benchmark repositories and live result dashboards.
- Academic search: arXiv, Semantic Scholar, ACL Anthology, ACM/IEEE where relevant.
- Product docs, blog posts, release notes, and issue/discussion caveats.
- Fork networks and copycat clusters, used only to find upstreams or divergent implementations.

## Search pattern

1. Start from known seed repositories and crawl their links.
2. Search exact phrases from claims and methodology sections.
3. Search by mechanism terms and synonyms:
   - token saving, context compression, prompt compression, context pruning;
   - repo map, code graph, code knowledge graph, repository graph, GraphRAG for code;
   - MCP trim, MCP code graph, MCP memory, agent memory, persistent memory;
   - Claude Code token, Codex token, Gemini CLI code graph, Cursor knowledge graph;
   - agentic token benchmark, provider-billed tokens, tool-call reduction.
4. For each mechanism group, run at least one broad query that is not anchored to known repository names.
5. For each top discovery result, run one follow-on query using its distinctive phrase.
6. Inspect README, docs, examples, benchmark scripts, issue/discussion caveats, and package metadata before creating a lead record.
7. Add a record to `data/repositories.json` after at least one source URL is reviewed, even if the current stage remains `lead`.
8. Add a matching backlog item for high-signal leads that need source-logic inspection.

## Coverage audit requirement

Run a coverage audit before any report claims that a candidate set is complete, primary, recommended, or representative.

A coverage audit must:

- record exact search queries, source, date, and returned candidates under `sources/discovery/`;
- include broad mechanism queries and follow-on phrase queries;
- sort or review at least one query family by stars or equivalent prominence and one by recent activity where the source supports it;
- deduplicate forks, mirrors, and copycat descriptions, while recording likely upstreams;
- add high-signal missing leads to `data/repositories.json` and `data/tool-analysis-backlog.json`;
- label shallow additions as `lead` or `discovery-lead`, not as source-logic evidence;
- state remaining coverage debt in the report or plan.

High-signal lead indicators include any of:

- strong match to an owned intervention surface;
- explicit support for Claude Code, Codex, Gemini CLI, Cursor, Hermes, MCP, or comparable coding-agent clients;
- explicit token, cost, tool-call, context, or retrieval-efficiency claim;
- large repository prominence relative to the mechanism group;
- recent active development;
- benchmark, evaluation, or raw-result artifacts mentioned in metadata or README.

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

- `lead`: search result, metadata, README, package metadata, or catalog entry only.
- `source-logic`: representative source code logic, runtime behavior, and failure behavior inspected.
- `benchmark-audit`: benchmark harness, tasks, scoring, token accounting, raw outputs, and failure semantics inspected.
- `reproduction`: independent target-workload reproduction with provider-billed accounting and quality gates.

Do not use retired `surface/moderate/deep` wording for decision confidence. Those terms describe reading effort, not evidence stage.

## Anti-bias rule

Stack selection must not be based only on the subset of tools already inspected. If a mechanism group has high-signal leads that are still `lead`, the report must either inspect them to `source-logic` before ranking or explicitly label the ranking as provisional and coverage-limited.
