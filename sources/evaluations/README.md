# Evaluation sources

This directory contains Lifecycle V2 fixture implementations, frozen execution contracts, retained provider-run evidence, derived comparisons, and audit receipts.

- `fixtures/` — Fastify and Beets Lifecycle V2 fixtures and their generated qualification evidence.
- `protocols/` — frozen execution contracts, content-addressed and derived at run time ([ADR 0010](../../docs/architecture/decision-records/0010-protocols-are-derived-at-run-time.md)); one file per apparatus that has actually run.
- `workflow-sessions/` — active provider-backed compact workflow evidence and the derived comparison artifacts beside it.
- `archive/` — superseded generations, retained only while they remain compatible controls.
- `audits/` — current qualification, invalidation, retirement, installation-parity, and general research receipts.

<!-- generated:corpus-summary -->
The active registry contains 32 accepted provider-backed sessions: 10 baselines, 4 replacement-runtime controls, 18 individual-tool treatments. By sequence: 16 `beets-lifecycle-sequence-v2`, 16 `fastify-lifecycle-sequence-v2`. By runtime: Claude Code 14, Codex CLI 14, OpenCode CLI 4.

Weighted token cost decomposes as agent steps times weighted cost per step. `94cb0f4a5c49` holds 6 replicates (71, 52, 52, 74, 72, 89 agent steps, spread 71.2%); weighted cost per step spread 43.4%; `c86863838e8b` holds 8 replicates (64, 64, 63, 123, 77, 60, 67, 73 agent steps, spread 105.0%); weighted cost per step spread 118.7%; `dc16afea3ad5` holds 8 replicates (69, 73, 76, 138, 72, 68, 64, 68 agent steps, spread 115.6%); weighted cost per step spread 42.1%; `e257557e288c` holds 6 replicates (66, 36, 35, 50, 45, 51 agent steps, spread 88.6%); weighted cost per step spread 61.7%.
<!-- /generated:corpus-summary -->

The active qualifications are `fixtures/medium/fastify-fastify/qualification-lifecycle-v2-20260821.json` and `fixtures/medium/beetbox-beets/qualification-lifecycle-v2-20260822.json`. Both lanes carry provider-backed results under those identities; a qualification proves preparation only and is never an effectiveness result.

Historical audit receipts and papers retain their provenance and point to the archived result paths where applicable. They are not current findings and must not be reused as controls for the Lifecycle V2 corpus.
