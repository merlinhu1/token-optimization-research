# Phase 2 report: corrected lifecycle-v0 natural-use screening of token-saving tools for Codex workflows

> **Current corrected report — 2026-07-20.** This document replaces the numerically invalid earlier Phase 2 text. The earlier version summed cumulative `ThreadTokenUsage.total` snapshots as if they were per-turn deltas and also interpreted treatment assignments that were later deleted for incomplete or unproven official integration. Git history preserves that superseded text; the tables and conclusions below use the final cumulative total per thread, retain only accepted faithful assignments, and treat structured correctness separately from the token objective.

**Evidence stage:** controlled reproduction screen

**Evidence dates:** 2026-07-16 through 2026-07-20

**Primary estimand:** provider-reported token usage under assignment to a faithfully installed treatment, with natural model uptake

**Model/runtime for treatment comparisons:** OpenAI Codex, GPT-5.6 Luna, `xhigh` reasoning

**Workflow unit:** one persistent three-task lifecycle-v0 session per repository lane

## Abstract

This corrected Phase 2 screen compares 17 accepted treatment conditions—16 canonical product assignments and one explicit Headroom proxy-only ablation—against matched bare-Codex baselines on persistent Fastify, Beets, and Terraform workflows. The evidence comprises 51 treatment sessions and 153 structured task outcomes. Corrected accounting selects the final cumulative provider-usage snapshot per thread rather than summing successive snapshots. All cited compact manifests verify, and deleted invalid treatments are excluded.

Five of 17 conditions used fewer aggregate provider tokens than their matched baseline in this one-replicate-per-lane screen: TokenJuice (-22.28%), Ponytail (-17.01%), SigMap (-9.60%), RTK (-1.90%), and Cartog (-1.00%). Only TokenJuice and SigMap were lower on all three lanes. The other 12 conditions were higher in aggregate, ranging from jcodemunch v2 at +0.38% and CodeGraph at +0.79% to Graphify at +63.90%. Across all 17 matched assignments, treatments used 582,180,587 corrected provider tokens versus 541,295,326 repeated matched-baseline tokens, a descriptive +7.55%. Structured verifiers passed 150/153 tasks; all three failures were the same Fastify feature type mismatch under different assignments.

These observations are screening evidence, not stable tool rankings or deployment estimates. Each treatment has one accepted assignment replicate per lane, Terraform contributes more than half of the matched r2 baseline total, and cached input dominates provider usage. The report therefore identifies replication candidates and negative findings without claiming universal savings, quality equivalence, or monetary cost reduction.

## 1. Research question and claim boundary

The research question is:

> Under natural-use assignment in persistent Codex software workflows, how does each faithfully installed token-saving treatment change provider-reported token usage relative to a compatible bare-Codex baseline, while preserving structured correctness as a separate diagnostic?

The estimand is assignment-level availability, not efficiency conditional on explicit invocation. Normal product setup—including author-provided wrappers, hooks, skills, rules, MCP wiring, and behavioral guidance—is part of the treatment. Evaluator-authored steering, forced calls, and invocation quotas are excluded. Zero explicit model-issued use remains an eligible natural-use observation after faithful installation.

The report supports descriptive claims for these frozen profiles, model conditions, fixtures, protocols, and first valid samples. It does **not** establish:

- a stable ordering across tools or future replicates;
- a universal per-task or per-language effect;
- causal attribution to a specific hook, tool call, or instruction surface without matching instrumentation;
- quality equivalence from verifier passes alone;
- local indexing, latency, or monetary cost savings;
- deployment readiness.

## 2. Why the earlier report was wrong

Two independent defects invalidated the earlier Phase 2 interpretation.

1. **Cumulative-provider accounting was summed incorrectly.** Codex emits cumulative thread snapshots. Summing each snapshot double-counted replayed history. The correction audit selects the final monotonic snapshot for each distinct thread and derives task increments by differencing successive snapshots. The active session registry retains legacy values for historical provenance in some older records; the correction audit and this report govern current accounting claims.
2. **Several treatment identities were not faithful canonical products.** Historical sessions were deleted—not relabelled as baseline—when official-integration review found missing hooks, wrappers, skills, product guidance, handshake proof, or runtime availability. Corrected profiles were installed through their pinned author-documented surfaces and qualified without provider calls before execution.

Existing comparison JSON files remain execution-provenance artifacts, but any baseline total copied from a legacy registry record is superseded by the deterministic cumulative-usage correction overlay. The machine-readable analysis receipt used for every number below is [`phase-2-corrected-analysis-20260720.json`](../../sources/evaluations/audits/phase-2-corrected-analysis-20260720.json).

## 3. Methods

### 3.1 Workflow design

Each lane is a persistent three-task lifecycle-v0 sequence:

1. feature implementation;
2. behavior-preserving refactor;
3. code review and correction.

Fastify, Beets, and Terraform use pinned upstream snapshots, concealed controller acceptance tests, neutral task aliases, and persistent resumed Codex sessions. Each next task is disclosed only after the preceding task and verifier boundary. The final cumulative tree is also verified. Setup, index building, and controller-side handshake checks occur outside provider-token accounting.

### 3.2 Baseline and treatment matching

Every treatment lane is paired by model condition, protocol family, sequence, and replicate index. Headroom default and its proxy-only ablation retain their first valid r1 assignments. The other 15 conditions retain first valid r2 assignments. No sample was replaced because its token result was large, its direction was unfavorable, or a callable tool received zero natural uptake.

The r0 Luna baseline is retained to characterize baseline variability but is not used for a treatment comparison in this report. A separate Sol/`high` baseline panel remains a compound model-and-effort comparison and is not mixed into the Luna/`xhigh` treatment estimates.

### 3.3 Corrected token accounting

The primary metric is `total_provider_tokens` from the final cumulative usage snapshot for each distinct Codex thread. Fresh input, cached input, output, and total provider tokens are provider-reported fields. Reasoning tokens are a subset of output accounting and are **not additive** to total provider tokens.

For each treatment profile:

- lane delta = corrected treatment total minus the matched corrected baseline total;
- aggregate delta = the sum of three lane treatment totals minus the sum of three matched baseline totals;
- percentage delta = aggregate delta divided by the matched baseline aggregate.

The all-profile aggregate repeats the matched baseline once per assignment. It describes the selected panel; it is not a pooled estimate of a tool population.

### 3.4 Treatment validity and uptake

Canonical product profiles include author-recommended integration surfaces needed for normal Codex use. Reduced surfaces are separately named ablations. Qualification proves installation and transport readiness, not model uptake or product effect. MCP registration is distinguished from `initialize`/`tools/list`, and both are distinguished from model-issued calls.

CodeGraph has additional retained actual-use evidence: all nine tasks issued successful product calls, with 23 completed `codegraph explore` executions in total. That confirms uptake for CodeGraph but does not turn its +0.79% observation into a stable mechanism estimate. Other automatic wrappers, hooks, and instruction treatments may act without explicit model commands; absence of commands is not interpreted as absence of exposure.

### 3.5 Correctness and integrity

Provider-token eligibility is independent of verifier success. Structured correctness outcomes are retained diagnostically and never used to rerun or select a more favorable token sample. All cited treatment and baseline compact-artifact manifests verify. Isolation audits, frozen protocol identities, provider usage, and deletion receipts define the accepted corpus.

## 4. Evidence inventory

| Evidence layer | Current evidence | Disposition |
|---|---:|---|
| Accepted Luna/`xhigh` baseline sessions | 9 | Three replicates across three repository lanes |
| Separate Sol/`high` baseline sessions | 9 | Context only; excluded from treatment matching |
| Accepted individual-tool treatment sessions | 51 | 17 conditions × three lanes |
| Structured treatment task outcomes | 153 | 150 passed, three diagnostic failures |
| Compact manifests cited by analysis | 69 sessions | All verified |
| Deleted invalid historical treatments | Excluded | Governed by explicit deletion receipts |
| Provider-free qualification | Passed before corrected runs | Setup evidence only; zero provider calls |

The 51 treatment sessions are all GPT-5.6 Luna/`xhigh`. Six sessions belong to the r1 Headroom full/ablation pair; 45 belong to the r2 corrected-profile panel.

## 5. Baseline behavior

### Table 1. Corrected Luna/`xhigh` baseline replicates

| Replicate | Fastify | Beets | Terraform | Aggregate provider tokens | Tasks |
|---|---:|---:|---:|---:|---:|
| r0 | 6,420,074 | 12,244,729 | 15,863,828 | 34,528,631 | 9/9 |
| r1 | 6,712,770 | 8,728,732 | 19,453,066 | 34,894,568 | 9/9 |
| r2 | 4,617,123 | 9,238,446 | 17,578,177 | 31,433,746 | 9/9 |

The three aggregate baseline replicates average 33,618,982 tokens with a sample standard deviation of 1,901,294 and a coefficient of variation (CV) of 5.66%. Lane-level CVs are higher: Fastify 19.18%, Beets 18.87%, and Terraform 10.18%. This variability is material relative to several near-zero treatment deltas.

The matched r2 baseline totals 31,433,746 tokens. Terraform contributes 17,578,177 tokens (55.92%), Beets 9,238,446 (29.39%), and Fastify 4,617,123 (14.69%). Aggregate signs can therefore be dominated by Terraform even when two smaller lanes move in the opposite direction.

## 6. Corrected treatment results

### Table 2. Matched provider-token results

Each lane cell shows corrected provider tokens followed by percentage change from its matched baseline. Negative percentages use fewer provider tokens.

| Treatment | Match | Fastify | Beets | Terraform | Aggregate | Aggregate delta | Tasks |
|---|---:|---:|---:|---:|---:|---:|---:|
| Headroom default Codex wrapper | r1 | 5,835,553 (-13.07%) | 13,750,119 (+57.53%) | 18,490,320 (-4.95%) | 38,075,992 | +9.12% | 8/9 |
| Headroom proxy-only | r1 | 4,655,914 (-30.64%) | 9,099,910 (+4.25%) | 22,306,972 (+14.67%) | 36,062,796 | +3.35% | 8/9 |
| TokenJuice | r2 | 2,759,005 (-40.24%) | 7,035,670 (-23.84%) | 14,634,423 (-16.75%) | 24,429,098 | -22.28% | 9/9 |
| RTK | r2 | 4,409,305 (-4.50%) | 11,132,590 (+20.50%) | 15,293,139 (-13.00%) | 30,835,034 | -1.90% | 9/9 |
| Snip | r2 | 4,445,104 (-3.73%) | 7,141,019 (-22.70%) | 20,543,255 (+16.87%) | 32,129,378 | +2.21% | 9/9 |
| Graphify | r2 | 7,204,296 (+56.03%) | 14,405,795 (+55.93%) | 29,910,544 (+70.16%) | 51,520,635 | +63.90% | 9/9 |
| Token Savior | r2 | 3,807,810 (-17.53%) | 11,731,406 (+26.98%) | 23,464,210 (+33.48%) | 39,003,426 | +24.08% | 9/9 |
| Ponytail | r2 | 5,768,026 (+24.93%) | 7,078,275 (-23.38%) | 13,241,637 (-24.67%) | 26,087,938 | -17.01% | 9/9 |
| Caveman | r2 | 8,026,762 (+73.85%) | 10,210,615 (+10.52%) | 21,493,956 (+22.28%) | 39,731,333 | +26.40% | 9/9 |
| LeanCTX | r2 | 4,735,271 (+2.56%) | 12,500,278 (+35.31%) | 17,531,315 (-0.27%) | 34,766,864 | +10.60% | 9/9 |
| Cartog | r2 | 5,531,588 (+19.81%) | 9,047,320 (-2.07%) | 16,541,498 (-5.90%) | 31,120,406 | -1.00% | 9/9 |
| CodeScope | r2 | 2,576,564 (-44.20%) | 12,703,830 (+37.51%) | 17,671,148 (+0.53%) | 32,951,542 | +4.83% | 9/9 |
| SwarmVault | r2 | 8,550,172 (+85.18%) | 7,001,834 (-24.21%) | 22,049,697 (+25.44%) | 37,601,703 | +19.62% | 9/9 |
| Serena | r2 | 3,777,040 (-18.19%) | 9,093,649 (-1.57%) | 23,345,023 (+32.81%) | 36,215,712 | +15.21% | 9/9 |
| SigMap | r2 | 4,318,341 (-6.47%) | 8,448,147 (-8.55%) | 15,648,958 (-10.98%) | 28,415,446 | -9.60% | 9/9 |
| CodeGraph | r2 | 5,561,571 (+20.46%) | 8,763,423 (-5.14%) | 17,355,866 (-1.26%) | 31,680,860 | +0.79% | 9/9 |
| jcodemunch v2 | r2 | 4,941,478 (+7.03%) | 5,452,170 (-40.98%) | 21,158,776 (+20.37%) | 31,552,424 | +0.38% | 8/9 |

### 6.1 Main observations

- **TokenJuice** is the strongest descriptive reduction in this screen: -22.28% aggregate, lower on all three lanes, with 9/9 task verifiers.
- **SigMap** is also lower on all three lanes: -9.60% aggregate with 9/9 task verifiers.
- **Ponytail** is lower in aggregate (-17.01%) but mixed by lane: Fastify rises 24.93% while Beets and Terraform fall.
- **RTK** (-1.90%) and **Cartog** (-1.00%) are near neutral relative to baseline variability and have mixed lane signs.
- **jcodemunch v2** (+0.38%) and **CodeGraph** (+0.79%) are also near neutral in aggregate; jcodemunch has one Fastify verifier failure, while CodeGraph has 9/9 verifiers and direct actual-use proof.
- **Graphify** is the largest descriptive increase (+63.90%) and is higher on all three lanes. **Caveman** (+26.40%) is also higher on every lane.
- The Headroom full wrapper (+9.12%) and proxy-only ablation (+3.35%) are both higher than their r1 baseline and each has the same Fastify feature diagnostic. One sample per condition does not support attribution of their difference to the proxy surface.

Across the 15-profile r2 panel, treatments use 508,041,799 tokens against 471,506,190 repeated matched-baseline tokens: +36,535,609, or +7.75%. Across all 17 assignments including the r1 Headroom pair, treatments use 582,180,587 against 541,295,326: +40,885,261, or +7.55%. These repeated-baseline aggregates summarize this panel only.

### Table 3. Corrected aggregate provider-token components

Reasoning is shown diagnostically as a subset of output and must not be added to the total.

| Treatment | Fresh input | Cached input | Output | Reasoning subset | Provider total |
|---|---:|---:|---:|---:|---:|
| Headroom default Codex wrapper | 1,272,757 | 36,630,784 | 172,451 | 81,401 | 38,075,992 |
| Headroom proxy-only | 1,047,436 | 34,856,448 | 158,912 | 77,993 | 36,062,796 |
| TokenJuice | 814,467 | 23,474,176 | 140,455 | 60,643 | 24,429,098 |
| RTK | 809,083 | 29,869,568 | 156,383 | 72,933 | 30,835,034 |
| Snip | 1,099,840 | 30,882,816 | 146,722 | 64,872 | 32,129,378 |
| Graphify | 1,361,015 | 49,986,816 | 172,804 | 79,196 | 51,520,635 |
| Token Savior | 981,020 | 37,852,672 | 169,734 | 87,710 | 39,003,426 |
| Ponytail | 852,101 | 25,110,272 | 125,565 | 64,493 | 26,087,938 |
| Caveman | 921,873 | 38,646,784 | 162,676 | 73,914 | 39,731,333 |
| LeanCTX | 1,128,232 | 33,489,408 | 149,224 | 76,152 | 34,766,864 |
| Cartog | 817,420 | 30,142,976 | 160,010 | 76,376 | 31,120,406 |
| CodeScope | 832,939 | 31,977,472 | 141,131 | 63,421 | 32,951,542 |
| SwarmVault | 1,059,184 | 36,398,592 | 143,927 | 69,286 | 37,601,703 |
| Serena | 855,463 | 35,223,552 | 136,697 | 71,625 | 36,215,712 |
| SigMap | 828,409 | 27,435,264 | 151,773 | 72,999 | 28,415,446 |
| CodeGraph | 917,852 | 30,593,536 | 169,472 | 79,489 | 31,680,860 |
| jcodemunch v2 | 835,162 | 30,611,200 | 106,062 | 59,935 | 31,552,424 |

Cached input dominates every aggregate. Differences in visible output are much smaller than total differences, so behavioral brevity cannot be assumed to explain provider-total movement. Large effects require trajectory-level analysis of replayed context, turns, tool outputs, and product guidance before any mechanism attribution.

## 7. Correctness diagnostics

Three of 153 treatment task outcomes fail their concealed verifier. All three occur on `fastify-lifecycle-feature-v0` and report the same TypeScript mismatch: the hidden check expected `FastifyRequest.mediaType` to remain `string | undefined`, while the produced implementation exposed `string`.

| Condition | Lane | Failed task | Treatment tasks passed |
|---|---|---|---:|
| Headroom default Codex wrapper | Fastify | `fastify-lifecycle-feature-v0` | 2/3 |
| Headroom proxy-only | Fastify | `fastify-lifecycle-feature-v0` | 2/3 |
| jcodemunch v2 | Fastify | `fastify-lifecycle-feature-v0` | 2/3 |

The later refactor and review tasks pass their individual concealed verifiers on the final cumulative tree. No causal claim is made that these tools caused the failures; each result combines treatment assignment with ordinary model stochasticity. The failures remain accepted for the token objective and visible as quality diagnostics.

## 8. Interpretation by treatment family

### 8.1 Terminal hooks and instructions

TokenJuice is lower on every lane and is the clearest replication candidate. RTK is modestly lower in aggregate but increases Beets by 20.50%. Snip is modestly higher in aggregate and increases Terraform by 16.87%. The family does not support a uniform claim from one sample each.

### 8.2 Retrieval and context systems

SigMap is lower on all three lanes. Cartog is near neutral with mixed signs. CodeGraph and jcodemunch are near neutral in aggregate despite materially different lane movements; CodeGraph's 23 successful product calls prove uptake but do not show that those calls caused its token result. Serena, LeanCTX, CodeScope, Token Savior, and SwarmVault are higher in aggregate. Graphify is substantially higher on every lane. Product category alone does not predict direction.

Warm-index and graph profiles incur local setup compute and latency outside the provider-token boundary. A token result cannot be converted into end-to-end operational efficiency without measuring those costs.

### 8.3 Plugins and behavioral policies

Ponytail's aggregate reduction is driven by Beets and Terraform while Fastify increases. Caveman is higher on every lane. These profiles can change model trajectory through instructions, skills, or hooks without explicit callable-tool events; interpretation remains assignment-level.

### 8.4 Headroom full product and ablation

The full wrapper is +9.12% and the proxy-only ablation is +3.35% against the same r1 baseline. Both have the same 8/9 structured result. The observed difference does not isolate a stable proxy effect because each condition has one assignment replicate and the wrapper owns additional surfaces.

## 9. Threats to validity

### 9.1 One treatment replicate per lane

Each profile contributes one accepted assignment sample on each repository. Model trajectory variance can be comparable to the small effects near zero. Descriptive ordering must not be read as a stable rank.

### 9.2 Baseline variability and replicate mismatch

Headroom conditions pair with r1; other treatments pair with r2. Each comparison is internally compatible, but cross-profile ordering also reflects the selected baseline replicate. The r0-r2 baseline CV is 5.66%, larger than several observed aggregate deltas.

### 9.3 Aggregate weighting

Terraform accounts for 55.92% of the r2 baseline aggregate. Aggregate results are therefore workload-weighted, not an equal-repository average.

### 9.4 Cache-heavy accounting

Cached input dominates total provider tokens. Total movement may reflect longer retained history, repeated tool output, instruction manifests, or different turn structure. Component totals alone do not identify the mechanism.

### 9.5 Treatment heterogeneity

Wrappers, hooks, instructions, MCP servers, indexes, and behavioral policies expose different surfaces. Full products and the Headroom ablation are named separately; results should not be generalized beyond each frozen profile.

### 9.6 Natural uptake

The experiment measures availability under product-authored guidance, not forced use. Zero explicit calls can be valid. Conversely, a successful handshake or command does not prove benefit.

### 9.7 Correctness and independent quality

Concealed verifiers provide bounded task diagnostics, not comprehensive merge-readiness review. The screen does not establish quality equivalence across treatments.

### 9.8 Setup boundary and cost

Local installation, indexing, CPU time, memory, latency, and monetary pricing are outside the primary metric. Provider-token changes are not automatically cost or wall-clock changes.

### 9.9 Limited workload population

The panel covers three repository workflows and three lifecycle tasks. It does not estimate performance over all languages, repository scales, or software-engineering task classes.

## 10. Decision use and next experiments

This screen supports prospective replication, not deployment selection.

1. **Replicate TokenJuice and SigMap first.** Both are lower on all three lanes with 9/9 verifiers and provide the strongest sign-consistent observations.
2. **Replicate Ponytail to test sign stability.** Its aggregate reduction is large enough to matter but is mixed by lane.
3. **Use RTK, Cartog, CodeGraph, and jcodemunch as near-neutral controls.** Their aggregate effects are small relative to baseline variation; CodeGraph additionally offers verified product uptake.
4. **Retain negative findings.** Graphify, Caveman, Token Savior, SwarmVault, Serena, LeanCTX, CodeScope, Snip, and both Headroom conditions should not be rerun to replace unfavorable samples. Any new replicate must be prospective and separately indexed.
5. **Keep mechanism instrumentation separate from eligibility.** Future runs should record wrapper/proxy/hook activity, MCP calls, turn counts, and setup latency where available, without forcing treatment use.

A future stack experiment requires a separately preregistered profile and cannot be inferred by adding individual percentages. The deleted historical TokenJuice+jcodemunch stack remains invalid and is not revived by valid individual evidence.

## 11. Claim-evidence audit

| Claim | Type | Evidence | Status / boundary |
|---|---|---|---|
| The earlier Phase 2 totals were inflated by cumulative-snapshot summation | Accounting | Cumulative usage correction audit plus raw provider events | Supported; corrected overlay governs |
| TokenJuice is -22.28% in this screen | Benchmark | Corrected r2 treatment and matched baseline totals | Supported for one assignment replicate per lane |
| SigMap is lower on all three evaluated lanes | Benchmark | Three corrected lane comparisons | Supported for this screen only |
| The 17-profile panel is +7.55% in aggregate | Benchmark | Repeated matched-baseline aggregation | Supported descriptively; not a population effect |
| CodeGraph was actually used | Reproduction | 23 completed product calls across all nine tasks | Supported; does not establish benefit |
| Faithful setup was present | Compatibility | Protocol-bound qualification and integration receipts | Supported for frozen profiles; setup is not uptake |
| Verifier success implies equal software quality | Quality | No comprehensive independent review | Unsupported; explicitly not claimed |
| Provider-token changes imply monetary savings | Recommendation | No pricing or local-compute model | Unsupported; explicitly not claimed |
| A stable tool ranking exists | Recommendation | One sample per profile/lane | Unsupported; replication required |

## 12. Reproducibility and evidence map

### Machine authority

- Session registry: [`data/workflow-sessions.json`](../../data/workflow-sessions.json)
- Treatment profile registry: [`data/evaluation-profiles.json`](../../data/evaluation-profiles.json)
- Workflow sequence registry: [`data/workflow-task-sequences.json`](../../data/workflow-task-sequences.json)
- Corrected Phase 2 analysis receipt: [`phase-2-corrected-analysis-20260720.json`](../../sources/evaluations/audits/phase-2-corrected-analysis-20260720.json)
- Cumulative provider-accounting correction: [`codex-cumulative-usage-accounting-20260718.json`](../../sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json)
- Corrected Luna/`xhigh` campaign receipt: [`corrected-luna-xhigh-r2-campaign-20260720.json`](../../sources/evaluations/audits/corrected-luna-xhigh-r2-campaign-20260720.json)
- CodeGraph actual-use audit: [`codegraph-provider-actual-use-20260720.json`](../../sources/evaluations/audits/codegraph-provider-actual-use-20260720.json)

### Eligibility and deletion receipts

- Official-integration parity audit: [`official-integration-parity-audit.md`](official-integration-parity-audit.md)
- Invalid treatment deletion receipt: [`invalid-treatment-result-deletions-20260718.json`](../../sources/evaluations/audits/invalid-treatment-result-deletions-20260718.json)
- Unproven treatment deletion receipt: [`unproven-treatment-result-deletions-20260718.json`](../../sources/evaluations/audits/unproven-treatment-result-deletions-20260718.json)
- Invalid CodeGraph deletion receipt: [`invalid-codegraph-v1-result-deletion-20260719.json`](../../sources/evaluations/audits/invalid-codegraph-v1-result-deletion-20260719.json)
- Invalid jcodemunch deletion receipt: [`invalid-jcodemunch-direct-v1-result-deletion-20260719.json`](../../sources/evaluations/audits/invalid-jcodemunch-direct-v1-result-deletion-20260719.json)
- Invalid Ponytail/Caveman deletion receipt: [`invalid-ponytail-caveman-result-deletion-20260719.json`](../../sources/evaluations/audits/invalid-ponytail-caveman-result-deletion-20260719.json)

### Execution artifacts

Each accepted session has a compact directory under [`sources/evaluations/workflow-sessions/`](../../sources/evaluations/workflow-sessions/) containing `run.json`, `changes.diff`, `evidence.jsonl.gz`, and `manifest.sha256`. Pairwise derived comparison JSON files are co-located under that directory. The cumulative correction audit is authoritative when a legacy comparison copied an inflated registry total.

## 13. Conclusion

Correcting both provider accounting and treatment identity reverses the earlier Phase 2 story. The current 17-condition panel is not an aggregate savings result: it uses 7.55% more corrected provider tokens than its repeated matched baselines. Five conditions are lower in aggregate, but only TokenJuice and SigMap are lower on all three lanes. Twelve conditions are higher, several substantially so. Structured correctness remains high at 150/153 tasks, but it is diagnostic rather than a sample-selection gate.

The evidence supports prospective replication of sign-consistent candidates and retention of negative findings. It does not support a stable ranking, universal savings claim, or deployment recommendation.
