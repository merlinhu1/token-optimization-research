# Evaluation sources

This directory contains Lifecycle V2 fixture implementations, frozen execution contracts, retained provider-run evidence, derived comparisons, and audit receipts.

- `fixtures/` — Fastify and Beets Lifecycle V2 fixtures; their generated qualification evidence is active for the future rerun.
- `protocols/` — the two bare-Codex no-result contracts eligible for the future rerun.
- `workflow-sessions/` — active provider-backed compact workflow evidence. It is currently empty because the prior corpus was archived before rerun.
- `archive/lifecycle-v1-pre-corrected-prompts-20260813/` — immutable pre-correction sessions, comparisons, protocols, campaign audits, and archive-only registry metadata.
- `archive/lifecycle-v1-raw-metric-protocols-20260815/` — two unexecuted protocols superseded when weighted token cost became the sole metric.
- `audits/` — current qualification, invalidation, archive, installation-parity, and general research receipts.

<!-- generated:corpus-summary -->
The active registry contains 1 accepted provider-backed session: 1 baselines. By sequence: 1 `fastify-lifecycle-sequence-v2`. By runtime: Codex CLI 1.

Weighted token cost decomposes as agent steps times weighted cost per step. `sample-bd72ef33cf25` holds 1 replicate (71 agent steps).

Archived generations: `lifecycle-v1-pre-capped-suite-20260815` (2 sessions); `lifecycle-v1-pre-corrected-prompts-20260813` (103 sessions); `lifecycle-v1-pre-targeted-tests-20260816` (4 sessions).
<!-- /generated:corpus-summary -->

The active qualifications are `fixtures/medium/fastify-fastify/qualification-lifecycle-v2-20260818.json` and `fixtures/medium/beetbox-beets/qualification-lifecycle-v2-20260816.json`. No provider-backed result exists under those identities yet; a future rerun requires fresh provider execution and explicit authorization.

Historical audit receipts and papers retain their provenance and point to the archived result paths where applicable. They must not be read as current findings until a new corrected-contract corpus is executed and published.
