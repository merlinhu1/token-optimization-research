# Evaluation sources

This directory contains Lifecycle V2 fixture implementations, frozen execution contracts, retained provider-run evidence, derived comparisons, and audit receipts.

- `fixtures/` — Fastify and Beets Lifecycle V2 fixtures; their generated qualification evidence is active for the future rerun.
- `protocols/` — the two bare-Codex no-result contracts eligible for the future rerun.
- `workflow-sessions/` — active provider-backed compact workflow evidence. It is currently empty because the prior corpus was archived before rerun.
- `archive/` — superseded generations, retained only while they remain compatible controls.
- `audits/` — current qualification, invalidation, retirement, installation-parity, and general research receipts.

<!-- generated:corpus-summary -->
The active registry contains 5 accepted provider-backed sessions: 5 baselines. By sequence: 3 `beets-lifecycle-sequence-v2`, 2 `fastify-lifecycle-sequence-v2`. By runtime: Codex CLI 5.

Weighted token cost decomposes as agent steps times weighted cost per step. `c86863838e8b` holds 3 replicates (64, 64, 63 agent steps, spread 1.6%); weighted cost per step spread 8.8%; `dc16afea3ad5` holds 2 replicates (69, 73 agent steps, spread 5.8%); weighted cost per step spread 10.0%.
<!-- /generated:corpus-summary -->

The active qualifications are `fixtures/medium/fastify-fastify/qualification-lifecycle-v2-20260818.json` and `fixtures/medium/beetbox-beets/qualification-lifecycle-v2-20260816.json`. No provider-backed result exists under those identities yet; a future rerun requires fresh provider execution and explicit authorization.

Historical audit receipts and papers retain their provenance and point to the archived result paths where applicable. They must not be read as current findings until a new corrected-contract corpus is executed and published.
