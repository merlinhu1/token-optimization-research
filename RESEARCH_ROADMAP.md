# Research Roadmap

## Phase 1 — Catalog foundation

- Import seed catalogs and candidate repositories.
- Normalize repository records into `data/repositories.json`.
- Add evidence labels and caveats for each record.
- Maintain `docs/methodology/discovery-protocol.md` as discovery expands.

## Phase 2 — Compatibility taxonomy

- Finalize technique categories by intervention surface.
- Map each repository to one or more technique IDs.
- Identify explicit conflicts and stackable combinations.
- Keep bundles as bundle records with component references.

## Phase 3 — Evaluation-method literature review

- Survey prompt compression, context selection, retrieval evaluation, agent benchmarks, cost accounting, and quality-retention methods.
- Populate `data/literature.json` and `docs/literature/literature-review.md`.
- Extract reusable metrics and experimental controls.

## Phase 4 — Technique-level evaluations

- Write one protocol per technique category.
- Run small deterministic pilots first.
- Add task-level and provider-billed accounting where available.
- Publish negative results and quality regressions.

## Phase 5 — Research outputs

- Produce paper drafts in `docs/paper/`.
- Standardize prompts, schemas, evidence labels, and benchmark templates.
- Version datasets and evaluation protocols with clear changelogs.
