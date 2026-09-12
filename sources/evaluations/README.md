# Evaluation sources

This directory contains Lifecycle V2 fixture implementations, frozen execution contracts, retained provider-run evidence, derived comparisons, and audit receipts.

- `fixtures/` — Fastify and Beets Lifecycle V2 fixtures and their generated qualification evidence.
- `protocols/` — frozen execution contracts, content-addressed and derived at run time ([ADR 0010](../../docs/architecture/decision-records/0010-protocols-are-derived-at-run-time.md)); one file per apparatus that has actually run.
- `workflow-sessions/` — active provider-backed compact workflow evidence and the derived comparison artifacts beside it.
- `archive/` — superseded generations, retained only while they remain compatible controls.
- `audits/` — current qualification, invalidation, retirement, installation-parity, and general research receipts.

<!-- generated:corpus-summary -->
The active registry contains 90 accepted provider-backed sessions: 17 baselines, 4 replacement-runtime controls, 69 individual-tool treatments. By sequence: 45 `beets-lifecycle-sequence-v2`, 45 `fastify-lifecycle-sequence-v2`. By runtime: Claude Code 50, Codex CLI 36, OpenCode CLI 4.

Weighted token cost decomposes as agent steps times weighted cost per step. `94cb0f4a5c49` holds 24 replicates (71, 52, 52, 74, 72, 89, 58, 110, 65, 67, 76, 64, 56, 68, 74, 69, 72, 75, 62, 68, 69, 65, 62, 56 agent steps, spread 111.5%); weighted cost per step spread 57.4%; `c86863838e8b` holds 19 replicates (64, 64, 63, 123, 77, 60, 67, 73, 75, 78, 100, 69, 90, 78, 78, 61, 67, 67, 67 agent steps, spread 105.0%); weighted cost per step spread 169.5%; `dc16afea3ad5` holds 19 replicates (69, 73, 76, 138, 72, 68, 64, 68, 86, 71, 106, 78, 80, 72, 84, 85, 82, 68, 74 agent steps, spread 115.6%); weighted cost per step spread 76.2%; `e257557e288c` holds 24 replicates (66, 36, 35, 50, 45, 51, 52, 54, 51, 39, 64, 42, 44, 54, 55, 51, 39, 53, 47, 54, 49, 44, 47, 79 agent steps, spread 125.7%); weighted cost per step spread 162.6%.
<!-- /generated:corpus-summary -->

The active qualifications are `fixtures/medium/fastify-fastify/qualification-lifecycle-v2-20260821.json` and `fixtures/medium/beetbox-beets/qualification-lifecycle-v2-20260822.json`. Both lanes carry provider-backed results under those identities; a qualification proves preparation only and is never an effectiveness result.

Historical audit receipts and papers retain their provenance and point to the archived result paths where applicable. They are not current findings and must not be reused as controls for the Lifecycle V2 corpus.
