---
status: active
truth_kind: engineering-behavior
last_reviewed: 2026-07-16
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
- Fastify contributes two retained baseline token samples: 12,950,066 tokens at `r0` and 13,077,552 at `r1`. Both passed 3/3 verifier tasks; review fields remain diagnostic.
- Invalid fixture records and stale protocols were removed at the experiment owner's explicit direction.
- Beets contributes two retained baseline token samples: 25,369,525 tokens at `r0` and 17,423,571 at `r1`. Both passed 3/3 verifier tasks; full-suite and review findings remain diagnostic.
- The active Terraform review verifier exercises pagination through rendered policy-summary output and permits equivalent private helper structures.
- Terraform contributes two retained baseline token samples: 33,564,150 tokens at `r0` and 43,392,324 at `r1`. Both passed 3/3 verifier tasks; no source review is required for token eligibility.
- The six retained baseline samples contain 145,777,188 provider-reported workflow tokens in total.
- Caveman's `r1` treatment screen is complete across all three lanes. Fastify used 6,663,664 tokens versus 13,077,552 baseline (-49.05%); Beets used 19,476,791 versus 17,423,571 (+11.78%); Terraform used 37,369,943 versus 43,392,324 (-13.88%).
- All three Caveman sessions passed 3/3 verifier tasks and are token-accounting eligible. Across the matched `r1` portfolio, Caveman used 63,510,398 tokens versus 73,893,447 baseline, a reduction of 10,383,049 tokens (-14.05%). This is a single replicate per lane, not yet a stable population estimate.
- RTK's `r1` availability screen is complete. Fastify used 11,353,460 tokens (-13.18%), Beets used 19,707,981 (+13.11%), and Terraform used 33,432,750 (-22.95%) against the same matched baselines. All three sessions passed 3/3 verifier tasks and are token-accounting eligible.
- Across the matched `r1` portfolio, the RTK-assigned arm used 64,494,191 tokens, a reduction of 9,399,256 tokens (-12.72%). A post-hoc count of explicit model-issued `rtk` command strings is not a valid universal measure of integration activity and is not part of the frozen estimand; no inactivity or no-effect claim is inferred from that count.
- Serena's `r1` availability screen used 12,778,273 tokens on Fastify (-2.29%), 16,314,633 on Beets (-6.36%), and 42,381,834 on Terraform (-2.33%). All three sessions passed 3/3 verifier tasks and are token-accounting eligible.
- Across the matched `r1` portfolio, the Serena-assigned arm used 71,474,740 tokens, a reduction of 2,418,707 tokens (-3.27%). Explicit model-visible calls are diagnostic rather than an eligibility gate, and the natural-use sample is preserved without forced invocation or a post-hoc mechanism rewrite.

## Evidence Boundary

Qualification proves fixture mechanics and discriminative diagnostics, not model effectiveness. Baseline runs establish token controls. A token-usage comparison requires compatible treatment records bound to the same baseline-pool fingerprint and replicate; verifier and review outcomes are reported alongside the comparison without gating it.

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
- ../../../../sources/evaluations/workflow-sessions/
- ../../../../docs/evaluations/workflow-evaluation-runbook.md
