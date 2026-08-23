# Evaluation sources

This directory contains Lifecycle V2 fixture implementations, frozen execution contracts, retained provider-run evidence, derived comparisons, and audit receipts.

- `fixtures/` — Fastify and Beets Lifecycle V2 fixtures; their generated qualification evidence is active for the future rerun.
- `protocols/` — the two bare-Codex no-result contracts eligible for the future rerun.
- `workflow-sessions/` — active provider-backed compact workflow evidence. It is currently empty because the prior corpus was archived before rerun.
- `archive/` — superseded generations, retained only while they remain compatible controls.
- `audits/` — current qualification, invalidation, retirement, installation-parity, and general research receipts.

<!-- generated:corpus-summary -->
The active registry contains 16 accepted provider-backed sessions: 10 baselines, 4 replacement-runtime controls, 2 individual-tool treatments. By sequence: 8 `beets-lifecycle-sequence-v2`, 8 `fastify-lifecycle-sequence-v2`. By runtime: Claude Code 6, Codex CLI 6, OpenCode CLI 4.

Weighted token cost decomposes as agent steps times weighted cost per step. `94cb0f4a5c49` holds 2 replicates (71, 52 agent steps, spread 36.5%); weighted cost per step spread 12.9%; `c86863838e8b` holds 4 replicates (64, 64, 63, 123 agent steps, spread 95.2%); weighted cost per step spread 98.5%; `dc16afea3ad5` holds 4 replicates (69, 73, 76, 138 agent steps, spread 100.0%); weighted cost per step spread 35.2%; `e257557e288c` holds 2 replicates (66, 36 agent steps, spread 83.3%); weighted cost per step spread 41.1%.
<!-- /generated:corpus-summary -->

The active qualifications are `fixtures/medium/fastify-fastify/qualification-lifecycle-v2-20260818.json` and `fixtures/medium/beetbox-beets/qualification-lifecycle-v2-20260816.json`. No provider-backed result exists under those identities yet; a future rerun requires fresh provider execution and explicit authorization.

Historical audit receipts and papers retain their provenance and point to the archived result paths where applicable. They must not be read as current findings until a new corrected-contract corpus is executed and published.
