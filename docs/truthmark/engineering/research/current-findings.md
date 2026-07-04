---
status: active
truth_kind: engineering-behavior
last_reviewed: 2026-07-17
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
- Ponytail's `r1` instruction-layer screen used 12,994,738 tokens on Fastify (-0.63%), 23,130,928 on Beets (+32.76%), and 36,870,055 on Terraform (-15.03%). All three sessions passed 3/3 verifier tasks and are token-accounting eligible.
- Across the matched `r1` portfolio, Ponytail used 72,995,721 tokens, a reduction of 897,726 tokens (-1.21%). The lane effects are mixed, and this single replicate is not a stable estimate.
- Token Savior's `r1` natural-use screen used 7,583,285 tokens on Fastify (-42.01%), 17,188,521 on Beets (-1.35%), and 38,118,793 on Terraform (-12.15%). All three sessions are token-accounting eligible; verifier diagnostics were 2/3, 2/3, and 3/3, respectively.
- Across the matched `r1` portfolio, Token Savior used 62,890,599 tokens, a reduction of 11,002,848 tokens (-14.89%). Verifier outcomes remain separate from the primary provider-token comparison.
- Graphify's `r1` natural-use screen used 8,707,133 tokens on Fastify (-33.42%), 17,235,153 on Beets (-1.08%), and 35,845,436 on Terraform (-17.39%). All three sessions are token-accounting eligible; verifier diagnostics were 2/3, 3/3, and 3/3, respectively.
- Across the matched `r1` portfolio, Graphify used 61,787,722 tokens, a reduction of 12,105,725 tokens (-16.38%). This remains a single replicate per lane rather than a stable population estimate.
- CodeGraph's `r1` natural-use screen used 8,358,733 tokens on Fastify (-36.08%), 18,870,554 on Beets (+8.30%), and 33,993,794 on Terraform (-21.66%). All three sessions passed 3/3 verifier tasks and are token-accounting eligible.
- Across the matched `r1` portfolio, CodeGraph used 61,223,081 tokens, a reduction of 12,670,366 tokens (-17.15%). The Beets increase makes the lane effects mixed despite the aggregate reduction.
- jcodemunch MCP's `r1` natural-use screen used 6,697,747 tokens on Fastify (-48.78%), 17,318,314 on Beets (-0.60%), and 36,885,960 on Terraform (-14.99%). All three sessions passed 3/3 verifier tasks and are token-accounting eligible.
- Across the matched `r1` portfolio, jcodemunch MCP used 60,902,021 tokens, a reduction of 12,991,426 tokens (-17.58%).
- SigMap's `r1` natural-use screen used 10,570,387 tokens on Fastify (-19.17%), 19,351,542 on Beets (+11.07%), and 52,610,520 on Terraform (+21.24%). All three sessions passed 3/3 verifier tasks and are token-accounting eligible.
- Across the matched `r1` portfolio, SigMap used 82,532,449 tokens, an increase of 8,639,002 tokens (+11.69%).
- LeanCTX's `r1` natural-use screen used 11,305,098 tokens on Fastify (-13.55%), 23,460,229 on Beets (+34.65%), and 35,342,005 on Terraform (-18.55%). All three sessions passed 3/3 verifier tasks and are token-accounting eligible.
- Across the matched `r1` portfolio, LeanCTX used 70,107,332 tokens, a reduction of 3,786,115 tokens (-5.12%). Its lane effects are mixed and the Beets increase is substantial.
- Snip's `r1` natural-use screen used 7,893,367 tokens on Fastify (-39.64%), 19,165,738 on Beets (+10.00%), and 32,679,643 on Terraform (-24.69%). All three sessions are operationally valid and token-accounting eligible; verifier diagnostics were 2/3, 3/3, and 3/3.
- Across the matched `r1` portfolio, Snip used 59,738,748 tokens, a reduction of 14,154,699 tokens (-19.16%). The Beets increase makes the lane effects mixed.
- TokenJuice's `r1` natural-use screen used 8,582,919 tokens on Fastify (-34.37%), 18,143,576 on Beets (+4.13%), and 26,074,453 on Terraform (-39.91%). All three sessions are operationally valid and token-accounting eligible and passed 9/9 verifier tasks.
- Across the matched `r1` portfolio, TokenJuice used 52,800,948 tokens, a reduction of 21,092,499 tokens (-28.54%), the largest aggregate reduction among the fourteen full-tool screens.
- Default Headroom's `r1` natural-use screen used 10,742,031 tokens on Fastify (-17.86%), 25,934,311 on Beets (+48.85%), and 34,821,358 on Terraform (-19.75%). All three sessions are operationally valid and token-accounting eligible; verifier diagnostics were 2/3, 3/3, and 3/3.
- Across the matched `r1` portfolio, default Headroom used 71,497,700 tokens, a reduction of 2,395,747 tokens (-3.24%). Its required proxy-only companion ablation used 77,931,962 tokens (+5.47%) with 8/9 verifier tasks passed; the ablation is not ranked as a separate full-tool screen.
- Cartog's `r1` natural-use screen used 6,055,080 tokens on Fastify (-53.70%), 14,563,339 on Beets (-16.42%), and 39,515,464 on Terraform (-8.93%). All three sessions are operationally valid and token-accounting eligible; verifier diagnostics were 2/3, 3/3, and 3/3.
- Across the matched `r1` portfolio, Cartog used 60,133,883 tokens, a reduction of 13,759,564 tokens (-18.62%). It reduced provider-token usage on all three lanes in this initial screen.
- CodeScope's `r1` natural-use screen used 5,516,066 tokens on Fastify (-57.82%), 15,344,837 on Beets (-11.93%), and 64,579,065 on Terraform (+48.83%). All three sessions passed 3/3 verifier tasks and are token-accounting eligible.
- Across the matched `r1` portfolio, CodeScope used 85,439,968 tokens, an increase of 11,546,521 tokens (+15.63%). Its large Terraform increase dominated reductions on the two medium lanes. No explicit model-issued CodeScope MCP call was observed; availability without forced invocation remains the frozen estimand.
- SwarmVault's `r1` natural-use screen used 16,974,841 tokens on Fastify (+29.80%), 15,464,870 on Beets (-11.24%), and 28,715,407 on Terraform (-33.82%). All three sessions passed 3/3 verifier tasks and are token-accounting eligible.
- Across the matched `r1` portfolio, SwarmVault used 61,155,118 tokens, a reduction of 12,738,329 tokens (-17.24%). Its offline heuristic warm index used the product-native deterministic 500-file cap on every lane. No explicit model-issued SwarmVault MCP call was observed; the sample is retained without forced uptake or an outcome-selected rerun.

## Evidence Boundary

Qualification proves fixture mechanics and discriminative diagnostics, not model effectiveness. Baseline runs establish token controls. A token-usage comparison requires compatible treatment records bound to the same baseline-pool fingerprint and replicate; verifier and review outcomes are reported alongside the comparison without gating it.

A prior Headroom proxy-only attempt was excluded as a controller-audit false positive because the audit interpreted the wrapper's explicit disabled-component startup notices as active tool exposure. The corrected first valid ablation is the only retained sample and no tokens from the excluded attempt are included in comparisons.

An artifact-packaging audit found that the three Graphify bundles had included generated `graphify-out` indexes in cumulative source diffs and the CodeScope Fastify bundle had included generated embedding-cache state. Those generated paths were removed under `source-diff-generated-state-exclusion-v1`; source changes, provider events and usage, verifier output, comparisons, and result interpretation were unchanged. Original artifact hashes and sizes remain recorded in each repaired `run.json`.

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
- ../../../../docs/reports/phase-2-lifecycle-v0-natural-use-screening.md
