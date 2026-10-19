# Evaluation sources

This directory contains Lifecycle V2 fixture implementations, frozen execution contracts, retained provider-run evidence, derived comparisons, and audit receipts.

- `fixtures/` — Fastify and Beets Lifecycle V2 fixtures and their generated qualification evidence.
- `protocols/` — frozen execution contracts, content-addressed and derived at run time ([ADR 0010](../../docs/architecture/decision-records/0010-protocols-are-derived-at-run-time.md)); one file per apparatus that has actually run.
- `workflow-sessions/` — active provider-backed compact workflow evidence and the derived comparison artifacts beside it.
- `archive/` — superseded generations, retained only while they remain compatible controls.
- `audits/` — current qualification, invalidation, retirement, installation-parity, and general research receipts.

<!-- generated:corpus-summary -->
The active registry contains 147 accepted provider-backed sessions: 18 baselines, 11 replacement-runtime controls, 118 individual-tool treatments. By sequence: 73 `beets-lifecycle-sequence-v2`, 74 `fastify-lifecycle-sequence-v2`. By runtime: Claude Code 69, Codex CLI 39, OpenCode CLI 39.

Weighted token cost decomposes as agent steps × weighted cost per step. Each pool mixes its controls with every treatment measured against them, so these spreads describe the pool, not any one product.

| Pool | Runtime · sequence | Sessions | Agent steps (min–median–max) | Step spread | Cost-per-step spread |
|---|---|---:|---|---:|---:|
| `05d5af94b07a` | OpenCode CLI · `beets-lifecycle-sequence-v2` | 18 | 90–125.5–191 | 112.2% | 167.9% |
| `4c934a33cbd1` | OpenCode CLI · `fastify-lifecycle-sequence-v2` | 17 | 110–128–166 | 50.9% | 239.5% |
| `94cb0f4a5c49` | Claude Code · `fastify-lifecycle-sequence-v2` | 34 | 51–68–110 | 115.7% | 79.3% |
| `c86863838e8b` | Codex CLI · `beets-lifecycle-sequence-v2`; OpenCode CLI · `beets-lifecycle-sequence-v2` | 20 | 60–71–123 | 105.0% | 169.5% |
| `dc16afea3ad5` | Codex CLI · `fastify-lifecycle-sequence-v2`; OpenCode CLI · `fastify-lifecycle-sequence-v2` | 21 | 64–76–138 | 115.6% | 76.2% |
| `e257557e288c` | Claude Code · `beets-lifecycle-sequence-v2` | 33 | 35–49–79 | 125.7% | 163.0% |
<!-- /generated:corpus-summary -->

The active qualifications are `fixtures/medium/fastify-fastify/qualification-lifecycle-v2-20260821.json` and `fixtures/medium/beetbox-beets/qualification-lifecycle-v2-20260822.json`. Both lanes carry provider-backed results under those identities; a qualification proves preparation only and is never an effectiveness result.

Historical audit receipts and papers retain their provenance and point to the archived result paths where applicable. They are not current findings and must not be reused as controls for the Lifecycle V2 corpus.
