# Phase 2: Natural-use evaluation of token-saving integrations in persistent Codex workflows

## Abstract

Token-saving tools for coding agents operate through different mechanisms, including terminal-output compression, retrieval, indexing, hooks, proxies, plugins, and behavioral instructions. Their effect on provider token usage is difficult to infer from mechanism alone because each integration can also change the agent's turn structure and retained context. This study evaluates 17 treatment conditions in persistent Codex workflows on Fastify, Beets, and Terraform. Each workflow contains a feature task, a behavior-preserving refactor, and a code-review task. Treatments were installed through their documented Codex integration surfaces and used without evaluator-imposed invocation requirements.

The primary outcome was provider-reported token usage relative to a matched bare-Codex baseline. The study retained 51 treatment sessions and 153 task outcomes. Five conditions used fewer aggregate tokens than their matched baselines: TokenJuice (-22.28%), Ponytail (-17.01%), SigMap (-9.60%), RTK (-1.90%), and Cartog (-1.00%). TokenJuice and SigMap were the only conditions with reductions on all three repositories. Twelve conditions increased aggregate usage. Across the complete panel, treatments used 582,180,587 tokens compared with 541,295,326 tokens for the repeated matched baselines, an increase of 7.55%. Concealed task verifiers passed in 150 of 153 cases.

The results do not support a general claim that token-saving integrations reduce provider usage. They identify TokenJuice and SigMap as the strongest candidates for replication, while showing that many integrations can be neutral or increase usage under natural-use conditions. Because each treatment has one accepted assignment per repository, the estimates are descriptive rather than confirmatory.

## 1. Introduction

Coding agents accumulate context from source files, command output, tool responses, instructions, and prior turns. Token-saving products attempt to reduce this load in several ways. Some compress terminal output. Others replace broad source inspection with retrieval or repository graphs. Hooks and proxies can alter data before it reaches the model, while plugins and behavioral policies can change how the agent works.

These mechanisms do not guarantee lower provider usage. A retrieval system may return concise evidence, but its tool descriptions and results also enter the context. A behavioral policy may shorten visible responses while leaving source reads and cached history unchanged. A graph index may reduce search effort in one repository and add overhead in another. Product evaluation therefore requires direct provider accounting in realistic, persistent workflows.

This study asks whether assignment to a documented token-saving integration changes provider-reported token usage relative to bare Codex. The intervention is the availability of the frozen product profile, not forced model uptake. Correctness is measured separately so that token outcomes are not selected according to whether a particular implementation passed its task verifier.

## 2. Experimental design

### 2.1 Workflows

The evaluation uses three lifecycle-v0 workflows:

- Fastify, representing a TypeScript application framework;
- Beets, representing a Python application;
- Terraform, representing a large Go codebase.

Each workflow consists of three ordered tasks completed in one persistent agent session: feature implementation, behavior-preserving refactoring, and code review with correction. The controller reveals tasks sequentially and runs concealed acceptance checks at each boundary. All tasks in a workflow use the same pinned repository snapshot and agent thread.

### 2.2 Model and runtime

Treatment comparisons use OpenAI Codex with GPT-5.6 Luna and `xhigh` reasoning. The baseline is bare Codex under the same model condition. Headroom's full wrapper and proxy-only ablation use the retained r1 baseline. The other 15 treatment conditions use r2. A third baseline replicate, r0, is included only to characterize baseline variability.

### 2.3 Treatment conditions

The study covers 16 named product profiles and one explicit ablation. Each product profile includes the author-recommended Codex surfaces specified by its frozen contract, such as hooks, wrappers, plugins, skills, product-authored instructions, MCP registration, and warm indexes. The Headroom proxy-only condition is analyzed separately from the full wrapper.

Installation and readiness checks occurred before provider execution. Callable tools were available to the model, but the evaluator did not require a minimum number of calls. This preserves the natural-use estimand: the result measures assignment to the integration, including the possibility that the model does not adopt an available tool.

### 2.4 Outcomes

The primary outcome is total provider tokens for the complete three-task session. Usage is derived from the final cumulative provider snapshot for each persistent thread. Fresh input, cached input, and output are retained as components. Reasoning tokens are a subset of output and are not added to the total.

For each repository, the treatment total is compared with the compatible baseline from the same replicate. Aggregate change is computed by summing the three treatment sessions and the three matched baseline sessions. The complete-panel total repeats the applicable baseline once for each treatment assignment and is used only as a descriptive summary.

Correctness is measured with concealed task verifiers. Verifier outcomes do not determine token eligibility and do not trigger replacement runs. All reported sessions passed execution-integrity and artifact-manifest checks.

## 3. Results

### 3.1 Baseline variation

Table 1 reports the three Luna/`xhigh` baseline replicates. Aggregate usage ranges from 31,433,746 to 34,894,568 tokens. The mean is 33,618,982, with a sample standard deviation of 1,901,294 and a coefficient of variation of 5.66%. Lane-level variation is higher: 19.18% for Fastify, 18.87% for Beets, and 10.18% for Terraform.

| Replicate | Fastify | Beets | Terraform | Total provider tokens |
|---|---:|---:|---:|---:|
| r0 | 6,420,074 | 12,244,729 | 15,863,828 | 34,528,631 |
| r1 | 6,712,770 | 8,728,732 | 19,453,066 | 34,894,568 |
| r2 | 4,617,123 | 9,238,446 | 17,578,177 | 31,433,746 |

Terraform contributes 55.92% of the r2 baseline total, compared with 29.39% for Beets and 14.69% for Fastify. Aggregate effects are therefore weighted toward Terraform.

### 3.2 Treatment effects

Table 2 reports repository-level percentage changes, aggregate treatment totals, verifier outcomes, and sign consistency. Conditions are ordered by their observed aggregate change. Negative values indicate lower provider usage.

| Treatment | Fastify | Beets | Terraform | Treatment tokens | Aggregate change | Tasks passed | Direction |
|---|---:|---:|---:|---:|---:|---:|---|
| TokenJuice | -40.24% | -23.84% | -16.75% | 24,429,098 | -22.28% | 9/9 | Lower in all lanes |
| Ponytail | +24.93% | -23.38% | -24.67% | 26,087,938 | -17.01% | 9/9 | Mixed |
| SigMap | -6.47% | -8.55% | -10.98% | 28,415,446 | -9.60% | 9/9 | Lower in all lanes |
| RTK | -4.50% | +20.50% | -13.00% | 30,835,034 | -1.90% | 9/9 | Mixed |
| Cartog | +19.81% | -2.07% | -5.90% | 31,120,406 | -1.00% | 9/9 | Mixed |
| jcodemunch v2 | +7.03% | -40.98% | +20.37% | 31,552,424 | +0.38% | 8/9 | Mixed |
| CodeGraph | +20.46% | -5.14% | -1.26% | 31,680,860 | +0.79% | 9/9 | Mixed |
| Snip | -3.73% | -22.70% | +16.87% | 32,129,378 | +2.21% | 9/9 | Mixed |
| Headroom proxy-only | -30.64% | +4.25% | +14.67% | 36,062,796 | +3.35% | 8/9 | Mixed |
| CodeScope | -44.20% | +37.51% | +0.53% | 32,951,542 | +4.83% | 9/9 | Mixed |
| Headroom default Codex wrapper | -13.07% | +57.53% | -4.95% | 38,075,992 | +9.12% | 8/9 | Mixed |
| LeanCTX | +2.56% | +35.31% | -0.27% | 34,766,864 | +10.60% | 9/9 | Mixed |
| Serena | -18.19% | -1.57% | +32.81% | 36,215,712 | +15.21% | 9/9 | Mixed |
| SwarmVault | +85.18% | -24.21% | +25.44% | 37,601,703 | +19.62% | 9/9 | Mixed |
| Token Savior | -17.53% | +26.98% | +33.48% | 39,003,426 | +24.08% | 9/9 | Mixed |
| Caveman | +73.85% | +10.52% | +22.28% | 39,731,333 | +26.40% | 9/9 | Higher in all lanes |
| Graphify | +56.03% | +55.93% | +70.16% | 51,520,635 | +63.90% | 9/9 | Higher in all lanes |

TokenJuice produced the largest aggregate reduction and was lower on all three repositories. Its reductions ranged from 16.75% on Terraform to 40.24% on Fastify. SigMap was also lower on all three repositories, with a narrower range of 6.47% to 10.98%.

Ponytail reduced aggregate usage by 17.01%, but the result was not consistent across repositories. Usage increased by 24.93% on Fastify and fell by more than 23% on both Beets and Terraform. RTK and Cartog were slightly below baseline in aggregate, but their effects were mixed and smaller than the observed baseline variation.

CodeGraph and jcodemunch were close to baseline in aggregate at +0.79% and +0.38%, respectively. CodeGraph had confirmed model uptake, with 23 completed product calls across the nine tasks, yet direct use did not produce an observed aggregate reduction in this sample.

Graphify had the largest increase at 63.90% and was higher on all three repositories. Caveman was also higher on every repository, with an aggregate increase of 26.40%. The remaining positive conditions had mixed repository-level effects.

Across the 15 r2 treatments, aggregate usage was 508,041,799 tokens compared with 471,506,190 tokens for the repeated r2 baseline, an increase of 7.75%. Including the two r1 Headroom conditions, the complete panel increased usage by 7.55%.

### 3.3 Token composition

Cached input accounted for 96.1% to 97.3% of provider tokens across the treatment conditions. Fresh input contributed approximately 2.3% to 3.4%, and visible output contributed less than 0.6%. The observed differences are therefore primarily differences in accumulated and replayed context, not differences in visible response length.

The component totals do not identify a single cause. An integration can change the number of turns, the size of tool results, the instruction surface, or the amount of repository material carried forward. Mechanism attribution requires trajectory and runtime instrumentation in addition to provider totals.

### 3.4 Correctness

Concealed verifiers passed 150 of 153 treatment tasks. The three failures occurred on the Fastify feature task under Headroom full, Headroom proxy-only, and jcodemunch. In each case, the implementation exposed `FastifyRequest.mediaType` as `string` rather than `string | undefined`. The subsequent refactor and review tasks passed their individual checks.

The token results for these sessions remain part of the study. With one assignment per treatment and repository, the common failure cannot be attributed to the integration rather than ordinary model variation.

## 4. Discussion

### 4.1 Token reduction was not a general property of the tools

Only five of the 17 conditions were below baseline in aggregate, and only two were lower on every repository. The complete panel used more tokens than its repeated matched baselines. Product labels such as retrieval, compression, or context management are therefore insufficient to predict provider usage under natural-use conditions.

### 4.2 The strongest signals are candidates for replication

TokenJuice and SigMap combine sign consistency with complete verifier success. Their mechanisms differ: TokenJuice operates through terminal-output handling, while SigMap provides repository retrieval. The common result is empirical rather than mechanistic. Both require independent replicates before the observed reductions can support a stable effect estimate.

Ponytail also merits replication because its aggregate reduction is substantial, but the repository-level disagreement is central to the result. A larger panel should test whether the Fastify increase recurs and whether the Beets and Terraform reductions persist.

### 4.3 Near-zero effects should not be overinterpreted

RTK, Cartog, CodeGraph, and jcodemunch fall within roughly two percentage points of baseline in aggregate. These differences are small relative to baseline variation. The present study cannot distinguish small product effects from normal trajectory variation for these conditions.

### 4.4 Integration overhead can outweigh local savings

Several treatments increased provider usage despite mechanisms intended to reduce context. This is plausible in persistent workflows because product instructions, tool schemas, query results, and additional turns also enter the context. Graphify produced the largest increase and was higher on all three repositories. Caveman, Token Savior, SwarmVault, Serena, LeanCTX, CodeScope, Snip, and both Headroom conditions also failed to show an aggregate reduction.

The results measure provider tokens only. They do not include local indexing time, CPU use, memory, latency, or product operating cost. A provider-token reduction would not by itself establish lower end-to-end cost, and a token increase would not establish that a tool lacks other operational value.

## 5. Threats to validity

The principal limitation is replication. Each treatment has one accepted assignment per repository. Baseline variation shows that model trajectories can differ materially under identical conditions, especially on Fastify and Beets. No confidence intervals or significance tests are reported because the treatment sample size does not support them.

The aggregate measure is workload-weighted. Terraform contributes more than half of the r2 baseline total, so its direction has disproportionate influence. The three repositories also represent a limited set of languages, project structures, and task types.

The study measures assignment to a product integration rather than effect conditional on explicit use. This is appropriate for hooks, proxies, and behavioral policies that may act without model-issued commands, but it limits mechanism claims. Even when direct calls are observed, as with CodeGraph, the study cannot isolate the calls from the rest of the treatment surface.

Correctness is assessed with bounded concealed verifiers rather than comprehensive human review. The 150/153 pass rate should not be interpreted as evidence of equal maintainability or merge readiness across conditions.

Provider token usage is dominated by cached input. Provider totals establish the accounting outcome but do not reveal which earlier turn or integration surface caused the later context to grow or shrink.

## 6. Implications and future work

The next phase should replicate TokenJuice and SigMap first because they produced reductions on all three repositories with complete verifier success. Ponytail is a second priority because of its large but heterogeneous aggregate reduction. RTK, Cartog, CodeGraph, and jcodemunch are useful near-baseline controls for estimating trajectory variance and instrumentation sensitivity.

Future runs should retain the first valid sample policy and index new replicates prospectively. Additional instrumentation should measure turn counts, explicit tool calls, tool-result volume, wrapper or hook activity, and setup latency. These measurements should remain diagnostic and should not force treatment uptake.

A larger study should add repositories without changing the persistent workflow design. Equal-weight and workload-weighted summaries should both be reported so that large repositories do not obscure heterogeneous effects.

## 7. Conclusion

Natural-use token-saving integrations did not reduce provider usage as a class. Five of 17 conditions were lower in aggregate, while the complete panel was 7.55% higher than its repeated matched baselines. TokenJuice and SigMap were the only conditions with reductions on Fastify, Beets, and Terraform. They are the strongest replication candidates, not established winners.

The study also shows why direct workflow measurement is necessary. Integrations that compress, retrieve, or guide can still increase the context carried through a persistent agent session. Provider-token outcomes depend on the entire trajectory, not only on the advertised local mechanism.

## Data availability

The analysis dataset is available in [`phase-2-corrected-analysis-20260720.json`](../../sources/evaluations/audits/phase-2-corrected-analysis-20260720.json). Accepted session records are indexed by [`data/workflow-sessions.json`](../../data/workflow-sessions.json), with compact evidence bundles under [`sources/evaluations/workflow-sessions/`](../../sources/evaluations/workflow-sessions/). Treatment definitions are recorded in [`data/evaluation-profiles.json`](../../data/evaluation-profiles.json). Provider-usage components and per-thread accounting are available in [`codex-cumulative-usage-accounting-20260718.json`](../../sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json).
