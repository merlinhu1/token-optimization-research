# Research Architecture

This repository is designed as a **research production system**, not as a document dump.

The central design decision is to separate four layers that are often mixed together in token-saving discussions:

1. **Observed artifact** — a repository, paper, benchmark, blog post, or user-provided catalog.
2. **Claim** — a scoped statement from an artifact, such as “90% command-output reduction.”
3. **Technique** — an atomic intervention surface, such as terminal-output compaction or AST-level code retrieval.
4. **Evaluation** — an experiment that tests a technique under a defined workload, model, and accounting method.

The repository exists to move evidence through those layers until it can support papers and standards.

## Architecture modules

| Module | Responsibility | Canonical files |
|---|---|---|
| Ingestion | Discover artifacts and preserve source provenance. | `sources/`, `data/repositories.json` |
| Normalization | Decompose products into techniques and claims. | `data/techniques.json`, `docs/architecture/domain-model.md` |
| Compatibility analysis | Model conflict and stackability by intervention surface. | `data/compatibility-edges.json`, `docs/architecture/compatibility-graph.md` |
| Evaluation design | Define reproducible experiments and measurement contracts. | `docs/evaluations/`, `data/evaluations.json` |
| Synthesis | Turn validated records into papers, references, and prompts. | `docs/papers/`, `docs/reference/`, `prompts/` |

## Research kernel

The stable kernel is:

```text
Artifact → Claim → Technique → Compatibility Edge → Evaluation → Finding → Paper Section
```

Everything else is support structure. If a file does not help one of those transitions, it does not belong in the core research path.

## Non-goals

- This is not an awesome-list.
- This is not a benchmark leaderboard.
- This is not an installer for token-saving stacks.
- This is not a place to repeat marketing claims without scope and caveats.

## Architectural invariants

1. **Bundles are references, not techniques.** A bundle can map to many techniques but must not define a technique merely because it packages tools together.
2. **Compatibility is surface-based.** Techniques conflict when they compete for the same buffer, decision point, or authority.
3. **Claims preserve scope.** Command-level, request-level, workflow-level, provider-reported, output-only, and quality-accepted claims are different evidence types.
4. **Evaluations are technique-level first.** Bundle comparisons are secondary and only useful after component techniques are understood.
5. **Paper text cites internal records.** The paper should cite repository IDs, claim IDs, technique IDs, evaluation IDs, and source URLs.

## Layout contract

The current directory ownership and archive policy are documented in [`repository-layout.md`](repository-layout.md).
