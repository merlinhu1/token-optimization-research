# Evaluation sources

This directory contains Lifecycle V2 fixture implementations, frozen execution contracts, retained provider-run evidence, derived comparisons, and audit receipts.

- `fixtures/` — Fastify and Beets Lifecycle V2 fixtures and their generated qualification evidence.
- `protocols/` — frozen execution contracts, content-addressed and derived at run time ([ADR 0010](../../docs/architecture/decision-records/0010-protocols-are-derived-at-run-time.md)); one file per apparatus that has actually run.
- `workflow-sessions/` — active provider-backed compact workflow evidence and the derived comparison artifacts beside it.
- `archive/` — superseded generations, retained only while they remain compatible controls.
- `audits/` — current qualification, invalidation, retirement, installation-parity, and general research receipts.

<!-- generated:corpus-summary -->
The active registry contains 111 accepted provider-backed sessions: 17 baselines, 8 replacement-runtime controls, 86 individual-tool treatments. By sequence: 56 `beets-lifecycle-sequence-v2`, 55 `fastify-lifecycle-sequence-v2`. By runtime: Claude Code 65, Codex CLI 38, OpenCode CLI 8.

Weighted token cost decomposes as agent steps times weighted cost per step. `05d5af94b07a` holds 2 replicates (128, 118 agent steps, spread 8.5%); weighted cost per step spread 6.2%; `4c934a33cbd1` holds 2 replicates (136, 129 agent steps, spread 5.4%); weighted cost per step spread 10.6%; `94cb0f4a5c49` holds 31 replicates (71, 52, 52, 74, 72, 89, 58, 110, 65, 67, 76, 64, 56, 68, 74, 69, 72, 75, 62, 68, 69, 65, 62, 56, 73, 71, 96, 55, 51, 61, 58 agent steps, spread 115.7%); weighted cost per step spread 76.1%; `c86863838e8b` holds 20 replicates (64, 64, 63, 123, 77, 60, 67, 73, 75, 78, 100, 69, 90, 78, 78, 61, 67, 67, 67, 78 agent steps, spread 105.0%); weighted cost per step spread 169.5%; `dc16afea3ad5` holds 20 replicates (69, 73, 76, 138, 72, 68, 64, 68, 86, 71, 106, 78, 80, 72, 84, 85, 82, 68, 74, 81 agent steps, spread 115.6%); weighted cost per step spread 76.2%; `e257557e288c` holds 32 replicates (66, 36, 35, 50, 45, 51, 52, 54, 51, 39, 64, 42, 44, 54, 55, 51, 39, 53, 47, 54, 49, 44, 47, 79, 51, 49, 54, 51, 39, 37, 38, 45 agent steps, spread 125.7%); weighted cost per step spread 163.0%.
<!-- /generated:corpus-summary -->

The active qualifications are `fixtures/medium/fastify-fastify/qualification-lifecycle-v2-20260821.json` and `fixtures/medium/beetbox-beets/qualification-lifecycle-v2-20260822.json`. Both lanes carry provider-backed results under those identities; a qualification proves preparation only and is never an effectiveness result.

Historical audit receipts and papers retain their provenance and point to the archived result paths where applicable. They are not current findings and must not be reused as controls for the Lifecycle V2 corpus.
