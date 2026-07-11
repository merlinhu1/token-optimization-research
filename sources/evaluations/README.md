# Evaluation sources

This directory contains lifecycle-v0 fixture implementations, frozen execution contracts, retained compact provider-run evidence, derived comparisons, and audit receipts.

- `fixtures/` — pinned Fastify, Beets, and Terraform lifecycle lanes.
- `protocols/` — immutable frozen execution contracts. Their embedded readiness text records freeze-time state; current execution state lives in `data/workflow-sessions.json`.
- `workflow-sessions/` — retained four-file compact bundles for accepted operational runs plus co-located derived matched baseline/treatment comparison JSON; cumulative-accounting corrections supersede legacy totals copied from historical registry records.
- `audits/` — qualification, accounting, deletion, installation-parity, actual-use, and aggregate-analysis receipts.

The active registry contains 90 accepted provider-backed sessions: 24 controls and 66 eligible individual-tool treatments. Invalid historical treatments were deleted—not relabelled as baseline—under explicit experiment-owner receipts. The current Phase 2 synthesis is derived from `audits/phase-2-corrected-analysis-20260720.json`; later natural-use and assisted-v1 records retain their own frozen populations.

Baseline V2 is the active task generation for future execution. Its three provider-free qualification receipts and frozen bare-model pilot contracts are indexed by `audits/baseline-v2-task-family-qualification-20260721.json`. They prove fixture mechanics only: no Baseline V2 provider call or treatment result exists. Focused acceptance behavior is model-visible, and treatment protocol freezing, preparation, and execution fail closed until the exact pilot protocol is bound to a passing independent zero-incident audit.

Provider-free qualification receipts prove setup, warm state, assignment, concealment, and applicable MCP handshakes for their exact frozen protocol hashes. They do not prove provider execution, natural uptake, or product effect. Accepted provider-backed evidence lives in the compact session bundles and current registry.

Four compact bundles carry a `source-diff-generated-state-exclusion-v1` repair receipt: the three Graphify lanes exclude `graphify-out`, and CodeScope Fastify excludes `.fastembed_cache` and `.codescope`. Those paths are generated treatment state, not source checkpoints. Repaired `run.json` records preserve the original artifact hashes, sizes, and removed-section counts; manifests hash the corrected compact bytes.
