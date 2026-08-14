# Prospective natural-use replication of six token-saving integration profiles in persistent Codex workflows

> **Retired evidence.** This report describes Lifecycle V0 results. V0 was retired on
> 2026-08-14 under [`lifecycle-v0-framework-retired-20260814.json`](../../sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json);
> its sessions, artifacts, and protocols were deleted from the active corpus, so the
> numbers below are no longer reproducible from this repository. The report is retained
> because negative findings and exclusions are part of the research record.

## Abstract

Token-saving integrations can alter coding-agent trajectories as well as the local source or command output they expose. This study prospectively repeated six eligible frozen integration profiles with OpenAI Codex, GPT-5.6 Luna, and `xhigh` reasoning across persistent Fastify, Beets, and Terraform workflows. Each workflow comprised feature implementation, behavior-preserving refactoring, and code review in one resumed agent session. The primary outcome was provider-reported tokens relative to three newly executed bare-Codex baseline sessions. Treatment availability was natural: documented product guidance was installed when it belonged to the frozen profile, but the evaluator did not require tool invocation. A seventh attempted profile, Cartog direct MCP v1, was deleted after a parity audit established that it omitted the product-authored Codex routing and official live-watch installer surfaces.

Across 18 eligible treatment sessions, 12 of 18 repository-level contrasts and four of six profile aggregates were above their matched r3 baselines. Profile-level contrasts ranged from -9.93% for jcodemunch-mcp v2 to +29.29% for CodeGraph. jcodemunch-mcp v2 passed 9/9 verifier tasks; Ponytail was 1.29% below baseline with 8/9. Treatment verifiers passed in 53 of 54 tasks.

Four of six profile-level directions differed from the preceding natural-use screen. These changes show that the single-session contrasts were not stable across the two screens; because baseline realizations, execution timing, and two treatment-guidance identities also differed, they do not by themselves identify trajectory variance as the cause. The evidence does not support a stable ranking or general token-reduction claim.

## 1. Introduction and research question

This study asks: **When six eligible previously screened integration profiles are assigned again under the same natural-use lifecycle design, what provider-token contrasts are observed against a fresh bare-Codex baseline?**

The estimand is assignment to each frozen profile, not efficiency conditional on explicit tool use. The results are descriptive assignment-level observations from one additional session per profile and repository. They do not estimate an average effect for token-saving products as a class. No formal replication-success threshold was preregistered; cross-screen sign and magnitude comparisons are descriptive.

Cross-screen comparisons were not byte-identical for every condition. TokenJuice and RTK used revised evaluator isolation guidance in r3 (`9b2f1577…` to `cb08dba8…`) that clarified that installed product-authored guidance remained authoritative; their first rendered task prompts therefore differed from r2. The bare-Codex model-facing task prompts were unchanged, but the r2 and r3 baseline fixture-runner hashes also differed (`eea63c24…` and `6fa8271b…`). Comparisons with the preceding screen are consequently cross-generation descriptive comparisons rather than pure repeated assignments under an identical execution condition.

## 2. Experimental design

### 2.1 Workflows and execution

Evidence was collected on 20 July 2026. The experimental unit was one persistent three-task workflow session. The three repositories and pinned revisions were:

| Repository | Language | Pinned revision |
|---|---|---|
| Fastify | TypeScript | `94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd` |
| Beets | Python | `9acb1ecff6c7ee0a1e83e3b983c94792345712c5` |
| Terraform | Go | `e02391ad384c9c38f1d7f40b853c0d2297348094` |

Each workflow delivered feature implementation, behavior-preserving refactoring, and code review/correction prompts sequentially in one Codex thread. At lane start, all three latent defects were already present in one committed composite broken-start tree. Later prompts and concealed verifier assets remained hidden, but code associated with later regressions was present from the start. No repository, thread, agent, treatment, index, or cache reset and no concealed verification occurred between prompts. Before each new session, the checkout, agent and profile homes, indexes, caches, configuration, and temporary state were reset.

Model-launched shell commands and Codex web search had no external network access. The controller allowed up to 3,600 seconds per task. Provider-token accounting began with Codex execution and included model-visible setup, retries, and corrections; controller-side installation, local indexing compute, and setup latency were outside the token boundary unless their output entered the Codex event stream.

All sessions used Codex CLI 0.144.0, GPT-5.6 Luna, and `xhigh` reasoning. Claims apply only to these frozen treatment boundaries:

| Profile | Frozen surface and state |
|---|---|
| TokenJuice | Codex post-tool-use hook and terminal-output compaction; cold CLI |
| SigMap | Warm index, MCP retrieval, product `AGENTS.md` guidance, and live watcher |
| Ponytail | Official Codex plugin with skills, commands, and session, prompt, and subagent hooks |
| RTK | Product-authored global Codex instructions and terminal-output compaction |
| CodeGraph | Warm index, MCP retrieval, global instructions, and live-index watch |
| jcodemunch-mcp v2 | Warm-index MCP retrieval with product-authored Codex guidance |

Product-authored routing or instruction layers were retained when the documented integration installed them; evaluator-authored tool steering and mandatory-uptake requirements were absent.

This evidence used the natural-use lifecycle contracts frozen before the later assisted-v1 activation. The solution-directed contracts are not part of these sessions.

### 2.2 Assignment and eligibility

The analysis contains three unique bare-Codex baseline sessions and 18 eligible treatment sessions. Every retained treatment profile was assigned once to each repository. The same three baseline sessions are reused for all six profile-level contrasts. Repeating their total is a descriptive weighting device and does not create 18 independent control observations. The reused controls were `baseline-fastify-20260720-p-769d40697529-r3`, `baseline-beets-20260720-p-b440da225a3a-r3`, and `baseline-terraform-20260720-p-ded8609b4172-r3`.

Conditions were not randomized or interleaved. The three baseline sessions completed before the retained treatment matrices, which ran in fixed order: TokenJuice, SigMap, Ponytail, RTK, CodeGraph, and jcodemunch-mcp v2. The deleted Cartog matrix had occurred between RTK and CodeGraph but contributes no result. “Matched” denotes shared repository, lifecycle, baseline-pool, model-condition, and replicate identity; it does not denote simultaneous execution or randomized pairing.

The first operationally valid assignment sample was retained. A session was eligible when it completed under its frozen protocol and profile, passed integrity and isolation checks, was accepted for the provider-token objective, and had a valid compact-artifact manifest. Token direction and verifier outcome did not affect eligibility, and no session was repeated to improve an outcome.

### 2.3 Measures

The primary metric is total provider tokens from the final cumulative usage snapshot for each persistent thread. Fresh input, cached input, and output are retained as components. Reasoning tokens are a subset of output and are not added to the total.

For each profile, the three treatment sessions are summed and compared with the three compatible r3 baseline sessions. Concealed verifier results are reported as quality diagnostics rather than selection gates.

## 3. Results

### 3.1 Fresh baseline

The r3 baseline used 33,766,396 provider tokens and passed 9/9 task verifiers.

| Repository | Provider tokens | Tasks passed |
|---|---:|---:|
| Fastify | 2,857,781 | 3/3 |
| Beets | 12,284,833 | 3/3 |
| Terraform | 18,623,782 | 3/3 |
| **Total** | **33,766,396** | **9/9** |

The aggregate baseline was 7.42% above r2, but lane movement was heterogeneous: Fastify fell 38.10%, Beets rose 32.97%, and Terraform rose 5.95%. This variation reinforces the need to compare treatments only with their matched replicate rather than with a historical baseline chosen after observation.

### 3.2 Profile-level contrasts

Negative values indicate lower provider usage than the fresh r3 baseline.

| Profile | Treatment tokens | Baseline tokens | Change | Tasks passed | Prior-screen contrast |
|---|---:|---:|---:|---:|---:|
| jcodemunch-mcp v2 | 30,412,523 | 33,766,396 | **-9.93%** | 9/9 | +0.38% |
| Ponytail | 33,332,279 | 33,766,396 | **-1.29%** | 8/9 | -17.01% |
| TokenJuice | 33,873,390 | 33,766,396 | +0.32% | 9/9 | -22.28% |
| SigMap | 36,774,274 | 33,766,396 | +8.91% | 9/9 | -9.60% |
| RTK | 37,990,585 | 33,766,396 | +12.51% | 9/9 | -1.90% |
| CodeGraph | 43,656,248 | 33,766,396 | +29.29% | 9/9 | +0.79% |

Four profiles were above baseline and two were below. Four of the six aggregate directions changed relative to the preceding screen. Ponytail remained below baseline but moved substantially toward zero; CodeGraph remained above baseline and increased in magnitude. No profile was below baseline on all three repositories in both screens. These cross-screen changes demonstrate instability of the observed contrasts, but they do not isolate trajectory variance from baseline variation, execution-time effects, or the guidance change affecting TokenJuice and RTK.

### 3.3 Repository-level contrasts

| Profile | Fastify | Beets | Terraform | Direction |
|---|---:|---:|---:|---|
| TokenJuice | +53.89% | -15.47% | +2.51% | Mixed |
| SigMap | +38.97% | +11.24% | +2.76% | Higher in all lanes |
| Ponytail | +81.60% | -1.32% | -13.98% | Mixed |
| RTK | +144.71% | -39.50% | +26.53% | Mixed |
| CodeGraph | +87.15% | +23.62% | +24.15% | Higher in all lanes |
| jcodemunch-mcp v2 | +132.69% | -22.55% | -23.50% | Mixed |

Twelve of 18 eligible lane contrasts were increases and six were reductions. Fastify was higher for every treatment, while the aggregate reductions for Ponytail and jcodemunch were driven by Beets and Terraform. Baseline weights were 8.46% for Fastify, 36.38% for Beets, and 55.15% for Terraform, so Terraform disproportionately determines profile aggregates.

### 3.4 Secondary selected-panel decomposition

For accounting decomposition only, summing the six eligible selected profiles yields 216,039,299 provider tokens versus 202,598,376 tokens after repeating the same three-session baseline six times, a difference of 13,440,923 tokens or 6.63%. This constructed total is not an independent estimand, does not add control observations, and does not estimate a portfolio or product-class effect.

| Component | Treatments | Repeated baselines | Difference |
|---|---:|---:|---:|
| Fresh input | 5,980,423 | 5,283,210 | +697,213 |
| Cached input | 209,122,048 | 196,406,784 | +12,715,264 |
| Output | 936,828 | 908,382 | +28,446 |
| Reasoning subset | 425,930 | 434,598 | -8,668 |
| Total provider tokens | 216,039,299 | 202,598,376 | +13,440,923 |

Most of the accounting difference was cached input. This decomposition does not identify a causal mechanism: cached content may include treatment instructions, tool schemas and results, repository material, or prior workflow turns.

### 3.5 Quality diagnostics

Treatment verifiers passed in 53 of 54 eligible tasks. Ponytail's Fastify feature task failed its concealed verifier; the session remained eligible for token accounting under the preregistered diagnostic-only quality policy. All baseline tasks passed. No independent source-quality review was performed for these r3 sessions. The bounded verifiers establish task-contract behavior, not comprehensive maintainability or merge readiness.

## 4. Discussion

The prospective screen does not reproduce the strongest reductions from the preceding screen. TokenJuice moved from -22.28% to +0.32%, SigMap from -9.60% to +8.91%, and RTK from -1.90% to +12.51%. Conversely, jcodemunch moved from +0.38% to -9.93%. These reversals establish cross-screen variability, but they do not isolate model-trajectory variance: the baseline realizations and execution times differed, and TokenJuice and RTK also crossed a treatment-guidance generation.

The results do not show that the integrations have no effect. They show that one additional natural-use assignment per repository is insufficient to separate product effects from variation in baseline realization, model trajectory, command selection, retained context, execution time, guidance generation, and repository-specific weighting. The selected panel's secondary 6.63% decomposition also does not estimate the average effect of integrations as a broader class.

A standardized solution-directed protocol is therefore a useful next experiment for this study's token-usage objective. Holding target files, implementation recipe, validation commands, environment constraints, and stop conditions constant is designed to reduce irrelevant search and debugging variance. That design answers a narrower question—provider-token usage while following a standardized workflow—and should be reported separately from the natural-use evidence here.

## 5. Threats to validity

Each profile has only one r3 treatment session per repository, and the three baseline sessions are reused across all profile contrasts. No confidence intervals or stable ranking are warranted. The workload panel contains only three repositories and three task classes. Aggregate totals are workload-weighted, with Terraform contributing most baseline tokens.

Conditions ran serially in a fixed order, so treatment identity is confounded with execution time and any unmeasured provider-side temporal variation. Cross-screen comparisons are additionally cross-generation for TokenJuice and RTK because their evaluator isolation guidance changed; the baseline fixture-runner hash also changed even though bare model-facing task prompts did not.

The treatment profiles expose heterogeneous mechanisms. Hooks, instruction layers, plugins, and callable retrieval tools do not share one invocation model. Assignment proves availability of the frozen treatment surface but does not prove that every optional tool was explicitly used. Runtime activity counters were unavailable for some automatic surfaces, limiting mechanism attribution.

Provider-token accounting is dominated by cached input and does not identify the originating turn or content segment. Verifier checks are bounded and remain separate from independent software-quality review.

## 6. Conclusion

In this prospective screen, two profile aggregates were below their fresh bare-Codex baselines and four were above; 12 of 18 repository-level contrasts were increases. Four profile-level directions differed from the preceding screen, although two comparisons also crossed a guidance-generation change. The evidence supports additional randomized or interleaved replication under byte-identical conditions, not a stable product ranking or a general token-reduction claim.

## Data availability

The machine-readable analysis is [`luna-xhigh-r3-replication-screen-20260720.json`](../../sources/evaluations/audits/luna-xhigh-r3-replication-screen-20260720.json). The Cartog deletion and recovery boundary is recorded in [`invalid-cartog-result-deletions-20260720.json`](../../sources/evaluations/audits/invalid-cartog-result-deletions-20260720.json). Session records are indexed by [`data/workflow-sessions.json`](../../data/workflow-sessions.json), with compact evidence under [`sources/evaluations/workflow-sessions/`](../../sources/evaluations/workflow-sessions/). Frozen profile definitions are in [`data/evaluation-profiles.json`](../../data/evaluation-profiles.json). The preceding natural-use analysis is [`phase-2-corrected-analysis-20260720.json`](../../sources/evaluations/audits/phase-2-corrected-analysis-20260720.json).
