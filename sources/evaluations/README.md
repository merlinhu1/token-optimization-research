# Evaluation sources

This directory contains Lifecycle V1 fixture implementations, frozen execution contracts, retained provider-run evidence, derived comparisons, and audit receipts.

- `fixtures/` — corrected Fastify and Beets Lifecycle V1 fixtures; their 2026-08-13 qualification inputs remain active for the future rerun.
- `protocols/` — the two corrected bare-Codex no-result contracts eligible for the future rerun.
- `workflow-sessions/` — active provider-backed compact workflow evidence. It is currently empty because the prior corpus was archived before rerun.
- `archive/lifecycle-v1-pre-corrected-prompts-20260813/` — immutable pre-correction sessions, comparisons, protocols, campaign audits, and archive-only registry metadata.
- `archive/lifecycle-v1-raw-metric-protocols-20260815/` — two unexecuted protocols superseded when weighted token cost became the sole metric.
- `audits/` — current qualification, invalidation, archive, installation-parity, and general research receipts.

<!-- generated:corpus-summary -->
The active registry contains 4 accepted provider-backed sessions: 4 baselines. By sequence: 2 `beets-lifecycle-sequence-v1`, 2 `fastify-lifecycle-sequence-v1`. By runtime: Codex CLI 4.

Archived generations: `lifecycle-v1-pre-capped-suite-20260815` (2 sessions); `lifecycle-v1-pre-corrected-prompts-20260813` (103 sessions).
<!-- /generated:corpus-summary -->

The corrected qualifications are `fixtures/medium/fastify-fastify/qualification-lifecycle-v1-20260813.json` and `fixtures/medium/beetbox-beets/qualification-lifecycle-v1-20260813.json`. No provider-backed result exists under those corrected identities yet; a future rerun requires fresh provider execution and explicit authorization.

Historical audit receipts and papers retain their provenance and point to the archived result paths where applicable. They must not be read as current findings until a new corrected-contract corpus is executed and published.
