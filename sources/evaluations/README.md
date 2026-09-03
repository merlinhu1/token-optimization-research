# Evaluation sources

This directory contains Lifecycle V2 fixture implementations, frozen execution contracts, retained provider-run evidence, derived comparisons, and audit receipts.

- `fixtures/` — Fastify and Beets Lifecycle V2 fixtures and their generated qualification evidence.
- `protocols/` — frozen execution contracts, content-addressed and derived at run time ([ADR 0010](../../docs/architecture/decision-records/0010-protocols-are-derived-at-run-time.md)); one file per apparatus that has actually run.
- `workflow-sessions/` — active provider-backed compact workflow evidence and the derived comparison artifacts beside it.
- `archive/` — superseded generations, retained only while they remain compatible controls.
- `audits/` — current qualification, invalidation, retirement, installation-parity, and general research receipts.

<!-- generated:corpus-summary -->
The active registry contains 56 accepted provider-backed sessions: 12 baselines, 4 replacement-runtime controls, 40 individual-tool treatments. By sequence: 28 `beets-lifecycle-sequence-v2`, 28 `fastify-lifecycle-sequence-v2`. By runtime: Claude Code 26, Codex CLI 26, OpenCode CLI 4.

Weighted token cost decomposes as agent steps times weighted cost per step. `94cb0f4a5c49` holds 12 replicates (71, 52, 52, 74, 72, 89, 58, 110, 65, 67, 76, 64 agent steps, spread 111.5%); weighted cost per step spread 57.4%; `c86863838e8b` holds 14 replicates (64, 64, 63, 123, 77, 60, 67, 73, 75, 78, 100, 69, 90, 78 agent steps, spread 105.0%); weighted cost per step spread 169.5%; `dc16afea3ad5` holds 14 replicates (69, 73, 76, 138, 72, 68, 64, 68, 86, 71, 106, 78, 80, 72 agent steps, spread 115.6%); weighted cost per step spread 67.9%; `e257557e288c` holds 12 replicates (66, 36, 35, 50, 45, 51, 52, 54, 51, 39, 64, 42 agent steps, spread 88.6%); weighted cost per step spread 91.0%.
<!-- /generated:corpus-summary -->

The active qualifications are `fixtures/medium/fastify-fastify/qualification-lifecycle-v2-20260821.json` and `fixtures/medium/beetbox-beets/qualification-lifecycle-v2-20260822.json`. Both lanes carry provider-backed results under those identities; a qualification proves preparation only and is never an effectiveness result.

Historical audit receipts and papers retain their provenance and point to the archived result paths where applicable. They are not current findings and must not be reused as controls for the Lifecycle V2 corpus.
