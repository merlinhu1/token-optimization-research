---
status: active
truth_kind: engineering-behavior
last_reviewed: 2026-07-18
---

# Current Findings

## Purpose

Record the repository's current decision-bearing evaluation state without overstating qualification or baseline evidence.

## Scope

This document covers the active lifecycle-v0 portfolio and retained production baseline evidence. It does not claim token savings before paired treatment runs exist.

## Current Implementation Behavior

- The runnable portfolio contains exactly three lifecycle-v0 sequences: Fastify, Beets, and Terraform.
- Every sequence contains feature implementation, behavior-preserving refactor, and code review/correction in that order.
- Each lane uses a composite preseeded start, sequential prompt disclosure, persistent agent/tool state, controller-only acceptance, and final-only cumulative verification.
- Codex 0.144.0 emits cumulative `ThreadTokenUsage.total` snapshots in every resumed `turn.completed.usage` event. The legacy extractor summed those snapshots, so all 30 retained persistent sessions carry inflated legacy totals in their immutable compact summaries and registry records. The source-backed correction audit preserves those artifacts and supplies authoritative final-per-thread session totals plus differenced per-task increments.
- Fastify contributes three retained Luna/`xhigh` active-default baseline token samples after correction: 6,420,074 tokens at `r0`, 6,712,770 at `r1`, and 4,617,123 at `r2`. All passed 3/3 verifier tasks; review fields remain diagnostic.
- Invalid fixture records and stale protocols were removed at the experiment owner's explicit direction.
- Beets contributes three corrected retained Luna/`xhigh` samples: 12,244,729 tokens at `r0`, 8,728,732 at `r1`, and 9,238,446 at `r2`. All passed 3/3 verifier tasks; full-suite and review findings remain diagnostic.
- The active Terraform review verifier exercises pagination through rendered policy-summary output and permits equivalent private helper structures.
- Terraform contributes three corrected retained Luna/`xhigh` samples: 15,863,828 tokens at `r0`, 19,453,066 at `r1`, and 17,578,177 at `r2`. All passed 3/3 verifier tasks; no source review is required for token eligibility.
- The nine corrected Luna/`xhigh` active-default baseline samples contain 100,856,945 provider tokens in total. The `r2` matrix contributed 31,433,746 tokens.
- A separate GPT-5.6 Sol/`high` model-comparison panel contributes nine valid baseline sessions and 68,275,315 corrected provider tokens. Every session passed 3/3 tasks and final verification with zero operational retries; all compact-artifact manifests passed. A recursive diagnostics audit nevertheless found raw stderr/non-object lines in retained Codex event JSONL streams, so checksum integrity must not be read as strict nested parseability.
- Sol/`high` used 32.30% fewer pooled corrected provider tokens than the retained Luna/`xhigh` panel, and every sequence/replicate cell was lower. This is a descriptive compound-condition contrast, not a model-only causal estimate: effort changed from `xhigh` to `high`, and six of nine pairs froze a different fixture-runner hash.
- The corrected Sol variance result is mixed: Fastify CV decreased from 19.18% to 6.86% and Beets from 18.87% to 14.98%, while Terraform increased from 10.18% to 21.70% and the three-lane portfolio increased from 5.66% to 16.29%. Terraform Sol/`high` r0 is a valid 15,526,000-token high-trajectory sample; its legacy 31,471,786 value was cumulative-snapshot double counting.
- The official-integration parity audit covers all 18 historical treatment profiles and all 54 historical treatment sessions. At the experiment owner's direction, 42 corrupted sessions and their active comparisons, compact bundles, and occupied protocols were deleted under receipt rather than relabelled as baseline. The active registry contains 18 controls and 12 eligible treatment records.
- Four three-lane conditions retain objective eligibility: Caveman as an always-on behavioral instruction policy, Ponytail as an always-on full-mode artifact policy, default Headroom as the pinned Codex wrapper treatment, and the Headroom proxy-only ablation.
- Under corrected accounting, Caveman used 34,108,648 tokens versus 34,894,568 matched baseline (-2.25%) with 9/9 verifier tasks. Ponytail used 34,839,756 (-0.16%) with 9/9 verifier tasks. These are narrow instruction-policy estimates, not installer/plugin lifecycle estimates.
- Default Headroom used 38,075,992 corrected tokens (+9.12%) with 8/9 verifier tasks; its proxy-only ablation used 36,062,796 (+3.35%) with 8/9 verifier tasks. The ablation is not a separate full-product ranking entry.
- TokenJuice, RTK, snip, Graphify, CodeGraph, and Lean Context were invalid historical product treatments because the runner omitted required Codex hook/rules/skill/index/hybrid surfaces or otherwise materially changed the product setup.
- The historical jcodemunch arm was invalid because it used an on-demand launcher, retained no successful MCP handshake, and did not identify whether it represented neutral MCP availability or the separate product-guidance layer.
- Cartog, CodeScope, SwarmVault, Serena, SigMap, and Token Savior were operationally unproven historical assignments. Their active results were deleted under the same no-baseline-relabel policy.
- The historical TokenJuice+jcodemunch stack was deleted because both component assignments were defective or unverified; its prior “does not advance” decision is withdrawn. No corrected stack contract exists pending valid individual evidence.
- Thirteen versioned corrected individual profiles now cover every deleted individual condition: TokenJuice, jcodemunch, RTK, snip, Graphify, CodeGraph, Lean Context, Cartog, CodeScope, SwarmVault, Serena, SigMap, and Token Savior. Each has a fixture-specific frozen protocol for Fastify, Beets, and Terraform and requires its pinned official or documented compatibility-safe Codex materialization.
- All 39 corrected fixture/profile protocols passed provider-free preparation, host-integration, warm-state, and applicable MCP `initialize` plus non-empty `tools/list` gates. No corrected provider-backed sessions have run; historical profile IDs remain non-runnable.

## Evidence Boundary

Qualification proves fixture mechanics and discriminative diagnostics, not model effectiveness. Product-effect eligibility additionally requires parity with the pinned official Codex integration and positive treatment-assignment evidence. For MCP profiles, configuration/listing is not a substitute for a retained protocol handshake or completed MCP call. Immutable compact bundles and legacy registry totals remain provenance; current token claims must use the cumulative-usage correction audit. The experiment-owner-authorized treatment repair remains a separate explicit exception, with corrupted active records deleted under machine-readable receipts rather than converted into controls.

A prior Headroom proxy-only attempt was excluded as a controller-audit false positive because the audit interpreted the wrapper's explicit disabled-component startup notices as active tool exposure. The corrected first valid ablation is the only retained sample and no tokens from the excluded attempt are included in comparisons.

A prior artifact-packaging audit found that the now-deleted historical Graphify bundles had included generated `graphify-out` indexes and one deleted CodeScope bundle had included embedding-cache state. That packaging repair remains historical provenance only; the later treatment-deletion receipts supersede those bundle identities in the active corpus.

## Product Truth Links

- None. This is an engineering research evidence surface.

## Maintenance Notes

- Update this document when a treatment, comparison, exclusion, or accepted baseline changes the current evidence state.
- Keep replay provenance and excluded fixture-failure records explicit.
- Never aggregate both an original provider execution and its replay as separate token spend.

## Source References

- ../../../../data/workflow-task-sequences.json
- ../../../../data/repository-fixtures.json
- ../../../../data/workflow-sessions.json
- ../../../../sources/evaluations/audits/official-integration-parity-20260718.json
- ../../../../sources/evaluations/audits/invalid-treatment-result-deletions-20260718.json
- ../../../../sources/evaluations/audits/unproven-treatment-result-deletions-20260718.json
- ../../../../sources/evaluations/audits/corrected-integration-qualification-20260718.json
- ../../../../sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json
- ../../../../sources/evaluations/audits/gpt-5-6-sol-high-baseline-variance-20260718.json
- ../../../../scripts/audit_codex_cumulative_usage.py
- ../../../../sources/evaluations/workflow-sessions/
- ../../../../docs/evaluations/operations/runbook.md
- ../../../../docs/papers/gpt-5-6-sol-high-baseline-variance-screen.md
- ../../../../docs/papers/phase-2-lifecycle-v0-natural-use-screening.md
- ../../../../docs/papers/phase-3-tokenjuice-jcodemunch-stack-screen.md
