# Methodology correction: discovery coverage after Graphify miss

Date: 2026-06-28

## Trigger

A high-signal repository, `safishamsi/graphify`, was absent from `data/repositories.json` even though it is directly relevant to the code-knowledge-graph and AI-coding-assistant retrieval surface.

This was not only a missing record. It exposed a methodology flaw.

## Root cause

The prior workflow optimized for evidence depth after a candidate entered the repository, but it did not enforce discovery breadth before stack-level claims.

Specific failure modes:

1. Seed-catalog and known-tool crawling created a closed candidate universe.
2. Source-logic availability biased stack construction toward tools already inspected.
3. The phrase "backlog has no lead-only entries" was interpreted as coverage completeness, but it only meant known leads had been processed.
4. Popularity was intentionally low weight for stack scoring, but the workflow also failed to use prominence as a discovery safety check.
5. Retrieval and memory tools using newer wording such as `knowledge graph`, `GraphRAG`, `queryable graph`, and broad agent-client lists were under-searched.

## Corrective audit

A GitHub coverage audit was run and saved at:

- `sources/discovery/2026-06-28-knowledge-graph-coverage-audit.json`

The audit used broad mechanism queries and follow-on phrase queries for knowledge-graph, GraphRAG, MCP, Claude Code, Codex, Gemini CLI, and Cursor terms.

It found multiple high-signal leads outside the prior source-logic set, including Graphify, Understand-Anything, swarmvault, total-agent-memory, cartog, codescope, Dragon-Brain, memex, and others.

## Repository changes

- Added missing high-signal leads to `data/repositories.json` as non-decision-bearing discovery records.
- Added matching `lead -> source_logic` backlog items in `data/tool-analysis-backlog.json`.
- Promoted the 13 corrective-audit leads to source-logic dossiers on 2026-06-29 and preserved inspection artifacts under `sources/discovery/2026-06-29-graph-leads-*-source-logic.json`.
- Updated `docs/methodology/discovery-protocol.md` with a coverage-audit requirement.
- Updated `docs/research/tool-research-strategy.md` so recommendations require coverage-audit context.
- Marked the Phase 1 stack report as coverage-limited and changed the top table from primary recommendations to source-inspected hypotheses.
- Updated repository truth for methodology/reporting workflow.

## New invariant

Before calling a stack set complete, primary, recommended, or representative, the repository must run a discovery coverage audit for the relevant mechanism group and preserve the query artifact under `sources/discovery/`.

If high-signal leads remain at `lead`, rankings must either wait for source-logic inspection or explicitly state they are coverage-limited.

## Remaining work

- Re-run retrieval-stack comparison after incorporating the 13 promoted graph/RAG and memory source-logic dossiers.
- Keep benchmark-audit and reproduction wording out of the Phase 1 upgrade until harnesses, raw outputs, token accounting, and quality gates are inspected.
