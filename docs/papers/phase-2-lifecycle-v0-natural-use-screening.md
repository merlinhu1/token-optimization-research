# Phase 2: A natural-use reproduction screen of token-saving integration profiles in persistent Codex workflows

## Abstract

Token-saving tools for coding agents operate through different mechanisms, including terminal-output compression, retrieval, indexing, hooks, proxies, plugins, and behavioral instructions. Their effect on provider token usage is difficult to infer from mechanism alone because each integration can also change the agent's turn structure and retained context. This study evaluates 17 treatment conditions in persistent Codex workflows on Fastify, Beets, and Terraform. Each workflow contains a feature task, a behavior-preserving refactor, and a code-review task. Treatments were installed through their documented Codex integration surfaces and used without evaluator-imposed invocation requirements.

The primary outcome was provider-reported token usage relative to a matched bare-Codex baseline. The study retained 51 treatment sessions and 153 task outcomes. Five conditions used fewer aggregate tokens than their matched baselines: TokenJuice (-22.28%), Ponytail (-17.01%), SigMap (-9.60%), RTK (-1.90%), and Cartog (-1.00%). TokenJuice and SigMap were the only conditions with reductions on all three repositories. Twelve conditions increased aggregate usage. Across the complete panel, treatments used 582,180,587 tokens compared with 541,295,326 tokens for the repeated matched baselines, an increase of 7.55%. Concealed task verifiers passed in 150 of 153 cases.

The results do not support a general claim that token-saving integrations reduce provider usage. Within this panel, TokenJuice and SigMap are the strongest candidates for replication, while many other profiles were near baseline or higher. Because each treatment has one accepted assignment per repository, the estimates are descriptive rather than confirmatory.

## 1. Introduction

Coding agents accumulate context from source files, command output, tool responses, instructions, and prior turns. Token-saving products attempt to reduce this load in several ways. Some compress terminal output. Others replace broad source inspection with retrieval or repository graphs. Hooks and proxies can alter data before it reaches the model, while plugins and behavioral policies can change how the agent works.

These mechanisms do not guarantee lower provider usage. A retrieval system may return concise evidence, but its tool descriptions and results also enter the context. A behavioral policy may shorten visible responses while leaving source reads and cached history unchanged. A graph index may reduce search effort in one repository and add overhead in another. Product evaluation therefore requires direct provider accounting in realistic, persistent workflows.

This study asks: **RQ1: In three persistent coding workflows, what provider-token differences are observed when Codex is run with each frozen integration profile rather than bare Codex under a natural-use availability policy?** The contrasts are descriptive assignment-level observations; the design does not estimate a population-level effect for token-saving integrations as a class. Correctness is measured separately so that token outcomes are not selected according to whether a particular implementation passed its task verifier.

## 2. Experimental design

### 2.1 Study scope and unit of analysis

This reproduction screen analyzes sessions collected from 16 to 20 July 2026. The experimental unit is one persistent three-task workflow session. The analysis contains 51 treatment sessions: 17 profiles evaluated once on each of three repositories. Each profile therefore has one assignment-level observation per repository and no within-profile treatment replicate.

Fifteen profiles are compared with the same three r2 baseline sessions, one for each repository. The two Headroom profiles are compared with the same three r1 baseline sessions. The r0 baseline is used only to describe baseline variability. The complete-panel baseline total repeats six unique baseline sessions across 17 profile-level contrasts; it does not represent 51 independently executed baseline sessions.

A treatment session is eligible when it completed under its frozen profile, sequence, model condition, and replicate assignment; is accepted for the provider-token objective; and has a verified compact-artifact manifest. Token direction and verifier outcome do not determine eligibility.

### 2.2 Workflows

The evaluation uses three lifecycle-v0 workflows:

- Fastify, representing a TypeScript application framework;
- Beets, representing a Python application;
- Terraform, representing a large Go codebase.

Each workflow consists of three ordered tasks completed in one persistent agent session: feature implementation, behavior-preserving refactoring, and code review with correction. The controller reveals tasks sequentially and runs concealed acceptance checks at each boundary. All tasks in a workflow use the same pinned repository snapshot and agent thread.

Table 1 identifies the pinned repository revision and the matched r1 and r2 baseline sessions for each workflow.

| Repository | Language | Pinned commit | r1 baseline session | r2 baseline session |
|---|---|---|---|---|
| Fastify | TypeScript | `94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd` | `baseline-fastify-20260716-p-769d40697529-r1` | `baseline-fastify-20260718-p-769d40697529-r2` |
| Beets | Python | `9acb1ecff6c7ee0a1e83e3b983c94792345712c5` | `baseline-beets-20260716-p-b440da225a3a-r1` | `baseline-beets-20260718-p-b440da225a3a-r2` |
| Terraform | Go | `e02391ad384c9c38f1d7f40b853c0d2297348094` | `baseline-terraform-20260716-p-ded8609b4172-r1` | `baseline-terraform-20260718-p-ded8609b4172-r2` |

### 2.3 Model and runtime

Treatment comparisons use OpenAI Codex with GPT-5.6 Luna and `xhigh` reasoning. The baseline is bare Codex under the same model condition. Headroom's full wrapper and proxy-only ablation use the retained r1 baseline. The other 15 treatment conditions use r2. A third baseline replicate, r0, is included only to characterize baseline variability.

### 2.4 Treatment profiles

The screen evaluates 17 frozen integration profiles: 16 named integration profiles and one Headroom proxy-only ablation. The profiles span terminal hooks, behavioral instructions, wrappers, retrieval services, MCP integrations, plugins, repository graphs, and hybrid configurations. Claims in this paper apply to the evaluated profile boundaries rather than to every surface or configuration offered by the corresponding upstream product.

The display names used in the results map one-to-one to profile IDs and mechanism families in the supplementary analysis dataset and profile registry.

Installation and readiness checks occurred before provider execution. The configured surfaces were available during the workflow, but the evaluator imposed neither mandatory invocation nor a minimum call count. The estimand is therefore assignment to the frozen profile under natural-use conditions, including non-adoption of optional callable tools.

### 2.5 Outcomes

The primary outcome is total provider tokens for the complete three-task session. Usage is derived from the final cumulative provider snapshot for each persistent thread. Fresh input, cached input, and output are retained as components. Reasoning tokens are a subset of output and are not added to the total.

For each repository, the treatment total is compared with the compatible baseline from the same replicate. Aggregate change is computed by summing the three treatment sessions and the three matched baseline sessions. The complete-panel total repeats the applicable baseline once for each treatment assignment and is used only as a descriptive summary.

Correctness is measured with concealed task verifiers. Verifier outcomes do not determine token eligibility and do not trigger replacement runs. All treatment and matched-baseline manifests referenced by the analysis dataset passed checksum verification.

## 3. Results

### 3.1 Baseline variation

Table 2 reports the three Luna/`xhigh` baseline replicates. Aggregate usage ranges from 31,433,746 to 34,894,568 tokens. The mean is 33,618,982, with a sample standard deviation of 1,901,294 and a coefficient of variation of 5.66%. Lane-level variation is higher: 19.18% for Fastify, 18.87% for Beets, and 10.18% for Terraform.

| Replicate | Fastify | Beets | Terraform | Total provider tokens |
|---|---:|---:|---:|---:|
| r0 | 6,420,074 | 12,244,729 | 15,863,828 | 34,528,631 |
| r1 | 6,712,770 | 8,728,732 | 19,453,066 | 34,894,568 |
| r2 | 4,617,123 | 9,238,446 | 17,578,177 | 31,433,746 |

Terraform contributes 55.92% of the r2 baseline total, compared with 29.39% for Beets and 14.69% for Fastify. Aggregate effects are therefore weighted toward Terraform.

### 3.2 Observed treatment-baseline differences

Table 3 reports aggregate profile contrasts and makes the matched baseline replicate explicit. Table 4 reports repository-level changes. Fifteen profiles reuse the r2 baseline panel, and two Headroom profiles reuse the r1 baseline panel. Rows are ordered by observed aggregate change for readability; the ordering is descriptive and is not a statistical ranking. Negative values indicate lower provider usage.

| Profile | Baseline | Treatment tokens | Matched-baseline tokens | Aggregate change | Tasks passed |
|---|---:|---:|---:|---:|---:|
| TokenJuice | r2 | 24,429,098 | 31,433,746 | -22.28% | 9/9 |
| Ponytail | r2 | 26,087,938 | 31,433,746 | -17.01% | 9/9 |
| SigMap | r2 | 28,415,446 | 31,433,746 | -9.60% | 9/9 |
| RTK | r2 | 30,835,034 | 31,433,746 | -1.90% | 9/9 |
| Cartog | r2 | 31,120,406 | 31,433,746 | -1.00% | 9/9 |
| jcodemunch v2 | r2 | 31,552,424 | 31,433,746 | +0.38% | 8/9 |
| CodeGraph | r2 | 31,680,860 | 31,433,746 | +0.79% | 9/9 |
| Snip | r2 | 32,129,378 | 31,433,746 | +2.21% | 9/9 |
| Headroom proxy-only | r1 | 36,062,796 | 34,894,568 | +3.35% | 8/9 |
| CodeScope | r2 | 32,951,542 | 31,433,746 | +4.83% | 9/9 |
| Headroom default Codex wrapper | r1 | 38,075,992 | 34,894,568 | +9.12% | 8/9 |
| LeanCTX | r2 | 34,766,864 | 31,433,746 | +10.60% | 9/9 |
| Serena | r2 | 36,215,712 | 31,433,746 | +15.21% | 9/9 |
| SwarmVault | r2 | 37,601,703 | 31,433,746 | +19.62% | 9/9 |
| Token Savior | r2 | 39,003,426 | 31,433,746 | +24.08% | 9/9 |
| Caveman | r2 | 39,731,333 | 31,433,746 | +26.40% | 9/9 |
| Graphify | r2 | 51,520,635 | 31,433,746 | +63.90% | 9/9 |

| Profile | Fastify change | Beets change | Terraform change | Direction |
|---|---:|---:|---:|---|
| TokenJuice | -40.24% | -23.84% | -16.75% | Lower in all lanes |
| Ponytail | +24.93% | -23.38% | -24.67% | Mixed |
| SigMap | -6.47% | -8.55% | -10.98% | Lower in all lanes |
| RTK | -4.50% | +20.50% | -13.00% | Mixed |
| Cartog | +19.81% | -2.07% | -5.90% | Mixed |
| jcodemunch v2 | +7.03% | -40.98% | +20.37% | Mixed |
| CodeGraph | +20.46% | -5.14% | -1.26% | Mixed |
| Snip | -3.73% | -22.70% | +16.87% | Mixed |
| Headroom proxy-only | -30.64% | +4.25% | +14.67% | Mixed |
| CodeScope | -44.20% | +37.51% | +0.53% | Mixed |
| Headroom default Codex wrapper | -13.07% | +57.53% | -4.95% | Mixed |
| LeanCTX | +2.56% | +35.31% | -0.27% | Mixed |
| Serena | -18.19% | -1.57% | +32.81% | Mixed |
| SwarmVault | +85.18% | -24.21% | +25.44% | Mixed |
| Token Savior | -17.53% | +26.98% | +33.48% | Mixed |
| Caveman | +73.85% | +10.52% | +22.28% | Higher in all lanes |
| Graphify | +56.03% | +55.93% | +70.16% | Higher in all lanes |

TokenJuice produced the largest aggregate reduction and was lower on all three repositories. Its reductions ranged from 16.75% on Terraform to 40.24% on Fastify. SigMap was also lower on all three repositories, with a narrower range of 6.47% to 10.98%.

Ponytail reduced aggregate usage by 17.01%, but the result was not consistent across repositories. Usage increased by 24.93% on Fastify and fell by more than 23% on both Beets and Terraform. RTK and Cartog were slightly below baseline in aggregate, but their effects were mixed and smaller than the observed baseline variation.

CodeGraph and jcodemunch were close to baseline in aggregate at +0.79% and +0.38%, respectively. A separately retained [actual-use receipt](../../sources/evaluations/audits/codegraph-provider-actual-use-20260720.json) records 23 completed CodeGraph calls across the nine tasks. Despite this observed uptake, the profile-level aggregate difference was +0.79%; the design does not estimate the causal contribution of those calls.

Graphify had the largest increase at 63.90% and was higher on all three repositories. Caveman was also higher on every repository, with an aggregate increase of 26.40%. The remaining positive conditions had mixed repository-level effects.

Across the 15 r2 treatments, aggregate usage was 508,041,799 tokens compared with 471,506,190 tokens for the repeated r2 baseline, an increase of 7.75%. Including the two r1 Headroom conditions, the complete panel increased usage by 7.55%.

### 3.3 Token composition

Cached input accounted for 96.1% to 97.3% of provider-reported tokens across the treatment profiles. Fresh input accounted for 2.3% to 3.4%, and provider-reported output accounted for less than 0.6%. Reasoning tokens are included within output and are not additive.

At complete-panel level, the 40,885,261-token increase was almost entirely an increase in cached input. Cached input increased by 40,942,848 tokens, while fresh input decreased by 131,379 and output increased by 73,792.

Table 5 decomposes the complete-panel totals. The matched baseline is repeated once for each profile-level contrast, as described in Section 2.1.

| Component | Treatments | Repeated matched baselines | Difference |
|---|---:|---:|---:|
| Fresh input | 16,434,253 | 16,565,632 | -131,379 |
| Cached input | 563,182,336 | 522,239,488 | +40,942,848 |
| Output | 2,563,998 | 2,490,206 | +73,792 |
| Reasoning subset | 1,232,438 | 1,155,012 | +77,426 |
| Total provider tokens | 582,180,587 | 541,295,326 | +40,885,261 |

Reasoning tokens are shown diagnostically and are not added to total provider tokens. The decomposition is accounting, not a causal explanation. Cached input may reflect instructions, tool schemas, tool results, repository material, prior turns, or other replayed prompt content.

### 3.4 Correctness

Concealed verifiers passed 150 of 153 treatment tasks. The three failures occurred on the Fastify feature task under Headroom default Codex wrapper, Headroom proxy-only, and jcodemunch v2. In each case, the implementation exposed `FastifyRequest.mediaType` as `string` rather than `string | undefined`. The subsequent refactor and review tasks passed their individual checks.

The token results for these sessions remain part of the study. With one assignment per treatment and repository, the common failure cannot be attributed to the integration rather than ordinary model variation.

## 4. Discussion

### 4.1 Reductions were not consistent across the screened profiles

Five of the 17 screened profiles were below their matched baseline in aggregate, and two were below baseline on all three repositories. The selected 17-profile panel used more tokens than its repeated matched baselines. These observations show that lower provider usage was not a uniform outcome in this screen; they do not estimate the average effect of token-saving integrations as a broader product class.

### 4.2 The strongest signals are candidates for replication

TokenJuice and SigMap combine sign consistency with complete verifier success. Their mechanisms differ: TokenJuice operates through terminal-output handling, while SigMap provides repository retrieval. The common result is empirical rather than mechanistic. Both require independent replicates before the observed reductions can support a stable effect estimate.

Ponytail also merits replication because its aggregate reduction is substantial, but the repository-level disagreement is central to the result. A larger panel should test whether the Fastify increase recurs and whether the Beets and Terraform reductions persist.

### 4.3 Near-zero effects should not be overinterpreted

RTK, Cartog, CodeGraph, and jcodemunch fall within roughly two percentage points of baseline in aggregate. These differences are small relative to baseline variation. The present study cannot distinguish small product effects from normal trajectory variation for these conditions.

### 4.4 Integration overhead can outweigh local savings

Several treatments increased provider usage despite mechanisms intended to reduce context. This is plausible in persistent workflows because product instructions, tool schemas, query results, and additional turns also enter the context. Graphify produced the largest increase and was higher on all three repositories. In this screen, the evaluated profiles for Caveman, Token Savior, SwarmVault, Serena, LeanCTX, CodeScope, Snip, and both Headroom conditions were also above their matched baselines in aggregate.

The results measure provider tokens only. They do not include local indexing time, CPU use, memory, latency, or product operating cost. A provider-token reduction would not by itself establish lower end-to-end cost, and a token increase would not establish that a tool lacks other operational value.

## 5. Threats to validity

The principal limitation is replication. Each treatment has one accepted assignment per repository. Baseline variation shows that model trajectories can differ materially under identical conditions, especially on Fastify and Beets. No confidence intervals or significance tests are reported because the treatment sample size does not support them.

The aggregate measure is workload-weighted. Terraform contributes more than half of the r2 baseline total, so its direction has disproportionate influence. The three repositories also represent a limited set of languages, project structures, and task types.

The study measures assignment to a product integration rather than effect conditional on explicit use. This is appropriate for hooks, proxies, and behavioral policies that may act without model-issued commands, but it limits mechanism claims. Even when direct calls are observed, as with CodeGraph, the study cannot isolate the calls from the rest of the treatment surface.

Correctness is assessed with bounded concealed verifiers rather than comprehensive human review. The 150/153 pass rate should not be interpreted as evidence of equal maintainability or merge readiness across conditions.

Provider token usage is dominated by cached input. Provider totals establish the accounting outcome but do not reveal which earlier turn or integration surface caused the later context to grow or shrink.

## 6. Implications and future work

The next phase should replicate TokenJuice and SigMap first because they produced reductions on all three repositories with complete verifier success. Ponytail is a second priority because of its large but heterogeneous aggregate reduction. Additional bare-Codex replicates are required to estimate trajectory variance. RTK, Cartog, CodeGraph, and jcodemunch may be retained as near-baseline comparison profiles for evaluating instrumentation sensitivity, but they are not untreated controls.

Future runs should retain the first valid sample policy and index new replicates prospectively. Additional instrumentation should measure turn counts, explicit tool calls, tool-result volume, wrapper or hook activity, and setup latency. These measurements should remain diagnostic and should not force treatment uptake.

A larger study should add repositories without changing the persistent workflow design. Equal-weight and workload-weighted summaries should both be reported so that large repositories do not obscure heterogeneous effects.

## 7. Conclusion

In this 17-profile reproduction screen, five profiles were below their matched baseline in aggregate, while the descriptive panel total was 7.55% higher than the repeated matched-baseline total. TokenJuice and SigMap were the only profiles with observed reductions on Fastify, Beets, and Terraform. These results identify replication candidates but do not establish a class-level effect or a stable ranking.

The results show why direct workflow measurement is necessary. In this panel, profiles that compress, retrieve, or guide sometimes increased the context carried through a persistent agent session. Provider-token outcomes depend on the entire trajectory, not only on the advertised local mechanism.

## Data availability

The analysis dataset is available in [`phase-2-corrected-analysis-20260720.json`](../../sources/evaluations/audits/phase-2-corrected-analysis-20260720.json). Accepted session records are indexed by [`data/workflow-sessions.json`](../../data/workflow-sessions.json), with compact evidence bundles under [`sources/evaluations/workflow-sessions/`](../../sources/evaluations/workflow-sessions/). Treatment definitions are recorded in [`data/evaluation-profiles.json`](../../data/evaluation-profiles.json). Provider-usage components and per-thread accounting are available in [`codex-cumulative-usage-accounting-20260718.json`](../../sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json).
