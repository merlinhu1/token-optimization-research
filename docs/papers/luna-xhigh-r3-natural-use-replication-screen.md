# A second natural-use replicate of seven token-saving integration profiles in persistent Codex workflows

## Abstract

Token-saving integrations can alter coding-agent trajectories as well as the local source or command output they expose. This study prospectively repeated seven frozen integration profiles with OpenAI Codex, GPT-5.6 Luna, and `xhigh` reasoning across persistent Fastify, Beets, and Terraform workflows. Each workflow comprised feature implementation, behavior-preserving refactoring, and code review in one resumed agent session. The primary outcome was provider-reported tokens relative to three newly executed bare-Codex baseline sessions. Treatment availability was natural: documented product guidance was installed when it belonged to the frozen profile, but the evaluator did not require tool invocation.

The seven profiles used 257,591,572 provider tokens against 236,364,772 tokens for the baseline panel repeated descriptively across profile contrasts, an increase of 8.98%. Five profiles were above baseline in aggregate. jcodemunch-mcp v2 was 9.93% below baseline with 9/9 verifier tasks, while Ponytail was 1.29% below baseline with 8/9. TokenJuice was near baseline at +0.32%; SigMap, RTK, Cartog, and CodeGraph ranged from +8.91% to +29.29%. Treatment verifiers passed in 62 of 63 tasks. Five of seven profile-level directions differed from the preceding natural-use screen. These observations show substantial trajectory sensitivity and do not support a stable ranking or a general token-reduction claim.

## 1. Research question

This study asks: **When seven previously screened integration profiles are assigned again under the same natural-use lifecycle design, what provider-token contrasts are observed against a fresh bare-Codex baseline?**

The estimand is assignment to each frozen profile, not efficiency conditional on explicit tool use. The results are descriptive assignment-level observations from one additional session per profile and repository. They do not estimate an average effect for token-saving products as a class.

## 2. Experimental design

### 2.1 Workflows and execution

Evidence was collected on 20 July 2026. The experimental unit was one persistent three-task workflow session. The three repositories and pinned revisions were:

| Repository | Language | Pinned revision |
|---|---|---|
| Fastify | TypeScript | `94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd` |
| Beets | Python | `9acb1ecff6c7ee0a1e83e3b983c94792345712c5` |
| Terraform | Go | `e02391ad384c9c38f1d7f40b853c0d2297348094` |

Each workflow presented feature implementation, behavior-preserving refactoring, and code review/correction sequentially in one Codex thread. Repository changes, agent state, treatment state, indexes, and caches persisted between tasks. The controller used independently qualified composite starting states and concealed acceptance checks.

All sessions used Codex CLI 0.144.0, GPT-5.6 Luna, and `xhigh` reasoning. The seven treatments were TokenJuice, SigMap, Ponytail, RTK, Cartog, CodeGraph, and jcodemunch-mcp v2. Claims apply only to the exact frozen surfaces recorded in the profile registry. Product-authored routing or instruction layers were retained when the documented integration installed them; evaluator-authored steering and mandatory-uptake requirements were absent.

This evidence used the natural-use lifecycle contracts frozen before the later assisted-v1 activation. The solution-directed contracts are not part of these sessions.

### 2.2 Assignment and eligibility

The analysis contains three unique bare-Codex baseline sessions and 21 treatment sessions. Every treatment profile was assigned once to each repository. The same three baseline sessions are reused for all seven profile-level contrasts. Repeating their total is a descriptive weighting device and does not create 21 independent control observations.

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

| Profile | Treatment tokens | Baseline tokens | Change | Tasks passed | Prior-screen change |
|---|---:|---:|---:|---:|---:|
| jcodemunch-mcp v2 | 30,412,523 | 33,766,396 | **-9.93%** | 9/9 | +0.38% |
| Ponytail | 33,332,279 | 33,766,396 | **-1.29%** | 8/9 | -17.01% |
| TokenJuice | 33,873,390 | 33,766,396 | +0.32% | 9/9 | -22.28% |
| SigMap | 36,774,274 | 33,766,396 | +8.91% | 9/9 | -9.60% |
| RTK | 37,990,585 | 33,766,396 | +12.51% | 9/9 | -1.90% |
| Cartog | 41,552,273 | 33,766,396 | +23.06% | 9/9 | -1.00% |
| CodeGraph | 43,656,248 | 33,766,396 | +29.29% | 9/9 | +0.79% |

Five profiles were above baseline and two were below. Five of the seven aggregate directions changed relative to the preceding screen. Ponytail remained below baseline but moved substantially toward zero; CodeGraph remained above baseline and increased in magnitude. No profile was below baseline on all three repositories in both screens.

### 3.3 Repository-level contrasts

| Profile | Fastify | Beets | Terraform | Direction |
|---|---:|---:|---:|---|
| TokenJuice | +53.89% | -15.47% | +2.51% | Mixed |
| SigMap | +38.97% | +11.24% | +2.76% | Higher in all lanes |
| Ponytail | +81.60% | -1.32% | -13.98% | Mixed |
| RTK | +144.71% | -39.50% | +26.53% | Mixed |
| Cartog | +121.50% | +18.62% | +10.88% | Higher in all lanes |
| CodeGraph | +87.15% | +23.62% | +24.15% | Higher in all lanes |
| jcodemunch-mcp v2 | +132.69% | -22.55% | -23.50% | Mixed |

Fifteen of 21 lane contrasts were increases and six were reductions. Fastify was higher for every treatment, while the aggregate reductions for Ponytail and jcodemunch were driven by Beets and Terraform. Because Terraform is the largest baseline lane, its direction has disproportionate influence on aggregate totals.

### 3.4 Panel accounting

The complete selected panel used 257,591,572 provider tokens against 236,364,772 repeated matched-baseline tokens, a descriptive increase of 21,226,800 tokens or 8.98%. This panel total summarizes the selected profiles and must not be interpreted as a product-class effect.

| Component | Treatments | Repeated baselines | Difference |
|---|---:|---:|---:|
| Fresh input | 6,999,385 | 6,163,745 | +835,640 |
| Cached input | 249,475,072 | 229,141,248 | +20,333,824 |
| Output | 1,117,115 | 1,059,779 | +57,336 |
| Reasoning subset | 506,163 | 507,031 | -868 |
| Total provider tokens | 257,591,572 | 236,364,772 | +21,226,800 |

Most of the accounting difference was cached input. This decomposition does not identify a causal mechanism: cached content may include treatment instructions, tool schemas and results, repository material, or prior workflow turns.

### 3.5 Quality diagnostics

Treatment verifiers passed in 62 of 63 tasks. Ponytail's Fastify feature task failed its concealed verifier; the session remained eligible for token accounting under the preregistered diagnostic-only quality policy. All baseline tasks passed. The bounded verifiers establish task-contract behavior, not comprehensive maintainability or merge readiness.

## 4. Discussion

The additional replicate does not reproduce the strongest reductions from the preceding screen. TokenJuice moved from -22.28% to +0.32%, SigMap from -9.60% to +8.91%, RTK from -1.90% to +12.51%, and Cartog from -1.00% to +23.06%. Conversely, jcodemunch moved from +0.38% to -9.93%. These reversals are consistent with substantial trajectory variance in persistent coding workflows.

The results do not show that the integrations have no effect. They show that one additional natural-use assignment per repository is insufficient to separate product effects from variation in model trajectory, command selection, retained context, and repository-specific weighting. The selected panel's 8.98% increase also does not estimate the average effect of integrations as a broader class.

A standardized solution-directed protocol is therefore a useful next experiment for this study's token-usage objective. Holding target files, implementation recipe, validation commands, environment constraints, and stop conditions constant can reduce irrelevant search and debugging variance. That design answers a narrower question—provider-token usage while following a standardized workflow—and should be reported separately from the natural-use evidence here.

## 5. Threats to validity

Each profile has only one r3 treatment session per repository, and the three baseline sessions are reused across all profile contrasts. No confidence intervals or stable ranking are warranted. The workload panel contains only three repositories and three task classes. Aggregate totals are workload-weighted, with Terraform contributing most baseline tokens.

The treatment profiles expose heterogeneous mechanisms. Hooks, instruction layers, plugins, and callable retrieval tools do not share one invocation model. Assignment proves availability of the frozen treatment surface but does not prove that every optional tool was explicitly used. Runtime activity counters were unavailable for some automatic surfaces, limiting mechanism attribution.

Provider-token accounting is dominated by cached input and does not identify the originating turn or content segment. Verifier checks are bounded and remain separate from independent software-quality review.

## 6. Conclusion

In a second natural-use screen of seven frozen profiles, two profiles were below a fresh bare-Codex baseline in aggregate and five were above it. The selected panel used 8.98% more provider tokens than its repeated matched baselines, and five profile-level directions changed from the preceding screen. The evidence supports continued methodological control and replication, not a stable product ranking or a general claim that token-saving integrations reduce provider usage.

## Data availability

The machine-readable analysis is [`luna-xhigh-r3-replication-screen-20260720.json`](../../sources/evaluations/audits/luna-xhigh-r3-replication-screen-20260720.json). Session records are indexed by [`data/workflow-sessions.json`](../../data/workflow-sessions.json), with compact evidence under [`sources/evaluations/workflow-sessions/`](../../sources/evaluations/workflow-sessions/). Frozen profile definitions are in [`data/evaluation-profiles.json`](../../data/evaluation-profiles.json). The preceding natural-use analysis is [`phase-2-corrected-analysis-20260720.json`](../../sources/evaluations/audits/phase-2-corrected-analysis-20260720.json).
