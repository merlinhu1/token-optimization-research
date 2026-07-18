# Evaluation sources

This directory contains the lifecycle-v0 fixture implementations, frozen execution contracts, and retained compact provider-run evidence.

- `fixtures/` — pinned Fastify, Beets, and Terraform lifecycle lanes.
- `protocols/` — immutable frozen execution contracts. Their embedded readiness text records freeze-time state; current execution state lives in `data/workflow-sessions.json`.
- `workflow-sessions/` — retained four-file evidence bundles for completed operational runs and compatible comparisons.

Six operational baseline bundles are retained: two replicates for each active lane. Forty-eight `r1` natural-use treatment bundles—three each for Caveman, RTK, Serena, Ponytail, Token Savior, Graphify, CodeGraph, jcodemunch MCP, SigMap, LeanCTX, Snip, TokenJuice, default Headroom, Cartog, CodeScope, and SwarmVault—and their compatible comparison records are retained. Three additional Headroom proxy-only ablation bundles provide the required component diagnostic, for 57 total workflow sessions in the registry. Verifier and review outcomes are diagnostic rather than token-eligibility gates. Current status and token totals are indexed by `data/workflow-sessions.json`.

Three frozen, not-yet-run protocols prepare the Phase 3 `stack-tokenjuice-jcodemunch-mcp` screen on the unchanged lifecycle-v0 lanes. They reuse the retained compatible baseline and individual-component evidence; no new provider-backed stack session is claimed until it appears in `data/workflow-sessions.json`.

Four compact bundles carry a `source-diff-generated-state-exclusion-v1` repair receipt: the three Graphify lanes exclude `graphify-out`, and CodeScope Fastify excludes `.fastembed_cache` and `.codescope`. Those paths are generated treatment state, not source checkpoints. Repaired `run.json` records preserve the original artifact hashes, sizes, and removed-section counts; manifests hash the corrected compact bytes.
