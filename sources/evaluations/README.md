# Evaluation sources

This directory contains the lifecycle-v0 fixture implementations, frozen execution contracts, and retained compact provider-run evidence.

- `fixtures/` — pinned Fastify, Beets, and Terraform lifecycle lanes.
- `protocols/` — immutable frozen execution contracts. Their embedded readiness text records freeze-time state; current execution state lives in `data/workflow-sessions.json`.
- `workflow-sessions/` — retained four-file evidence bundles for completed operational runs and compatible comparisons.

Six operational baseline bundles are retained: two replicates for each active lane. Fifty-four historical treatment bundles are retained across individual-tool, Headroom ablation, and TokenJuice+jcodemunch stack profiles. The official-integration audit marks 42 treatment sessions objective-ineligible while preserving every provider event, token component, verifier outcome, and bundle checksum.

The historical protocols and evidence remain immutable execution records. Six additional frozen no-provider protocols bind the corrected `terminal-tokenjuice-codex-hook-v1` and `retrieval-jcodemunch-mcp-direct-v1` treatments across the three lifecycle-v0 lanes. No corrected provider-backed session exists.

Four compact bundles carry a `source-diff-generated-state-exclusion-v1` repair receipt: the three Graphify lanes exclude `graphify-out`, and CodeScope Fastify excludes `.fastembed_cache` and `.codescope`. Those paths are generated treatment state, not source checkpoints. Repaired `run.json` records preserve the original artifact hashes, sizes, and removed-section counts; manifests hash the corrected compact bytes.
