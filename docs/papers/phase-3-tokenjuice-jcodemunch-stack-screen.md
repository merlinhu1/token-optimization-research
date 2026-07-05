# Phase 3 report: TokenJuice + jcodemunch MCP lifecycle-v0 stack screen

> **Report status:** completed single-replicate stack screen. Results are scoped descriptive evidence, not a population estimate or deployment recommendation.

**Report date:** 2026-07-18

**Evidence collection:** 2026-07-18

**Evidence stage:** `reproduction`

**Runtime/model condition:** Codex CLI, OpenAI GPT-5.6 Luna, `xhigh` reasoning

**Primary metric:** cumulative provider-reported tokens per complete persistent workflow session

## Abstract

This Phase 3 screen evaluates the compatibility-safe `stack-tokenjuice-jcodemunch-mcp` profile on the unchanged lifecycle-v0 Fastify, Beets, and Terraform workflows. TokenJuice owns the terminal-output surface and jcodemunch MCP owns retrieval context. The experiment reuses the compatible retained `r1` bare-Codex, TokenJuice-only, and jcodemunch-only records and adds only the missing stack treatment in each lane.

All three stack sessions were operationally valid, passed tool-isolation and verifier-integrity checks, and passed all nine structured workflow verifiers. The stack used 67,155,585 provider tokens, 6,737,862 fewer than bare Codex (-9.12%). It nevertheless used 14,354,637 more tokens than TokenJuice alone (+27.19%) and 6,253,564 more than jcodemunch alone (+10.27%). It was worse than the better individual component in every lane. The aggregate descriptive interaction contrast was +27,346,063 provider tokens, with positive contrasts in all three lanes.

No explicit model-issued TokenJuice command or jcodemunch MCP call was observed in any stack lane. The retained individual TokenJuice and jcodemunch sessions also had zero such explicit calls. These valid natural-availability samples therefore measure assignment to the configured profiles and resulting trajectories, not realized terminal compaction or retrieval mechanism use. The stack fails the preregistered incremental-value criterion and should not advance under this model/runtime condition.

## 1. Research question and claim boundary

The primary question is:

> Does TokenJuice plus jcodemunch MCP reduce provider-reported tokens relative to both bare Codex and the better individual component on the same lifecycle-v0 workflows?

The experiment permits claims about:

- observed provider-token totals in the retained compatible `r1` records;
- observed lane-level and aggregate differences;
- the descriptive four-arm interaction contrast;
- structured verifier, isolation, and artifact-integrity outcomes;
- explicit model-issued command and MCP-call diagnostics present in the retained event streams.

It does not permit claims about:

- population-average stack effects or statistical significance;
- cross-model, cross-runtime, or cross-workload generalization;
- causal savings from terminal compaction or retrieval when neither mechanism was explicitly invoked;
- stable rankings from one stack replicate per lane;
- latency or monetary cost.

## 2. Design

### 2.1 Reused lifecycle-v0 contract

No task, fixture, prompt, verifier, model condition, runtime image, baseline pool, or replicate index was changed. Each lane contains feature implementation, behavior-preserving refactoring, and code review/correction in one persistent Codex session. Prompts are disclosed sequentially, repository and tool state persist between prompts, and concealed verification runs only after the final prompt.

The four descriptive arms are:

```text
N  = retained bare-Codex r1 baseline
A  = retained TokenJuice-only r1 treatment
B  = retained jcodemunch-MCP-only r1 treatment
AB = new TokenJuice+jcodemunch-MCP r1 stack treatment
```

Only `AB` required new provider executions. The retained `N`, `A`, and `B` records share the same lane-specific causal baseline-pool fingerprint and replicate index.

### 2.2 Stack composition

The frozen profile is `stack-tokenjuice-jcodemunch-mcp`:

- TokenJuice owns `terminal-output` through its normal cold CLI exposure on lane-specific `PATH`;
- jcodemunch MCP owns `retrieval-context` through its sole configured MCP server and warm repository index;
- overlapping memory, prompt, hook, proxy, and additional retrieval surfaces are disabled;
- use is natural: evaluator-authored instructions do not require, prefer, or quota either component.

### 2.3 Metrics

For any two conditions `X` and `Y`:

```text
delta(X, Y) = tokens(X) - tokens(Y)
delta_percent(X, Y) = delta(X, Y) / tokens(Y) × 100
```

The descriptive pair interaction is:

```text
interaction = AB - A - B + N
```

A negative value would be consistent with token synergy in this sample. A positive value indicates that the stack used more tokens than the additive four-arm contrast predicts. With one sample per arm and no explicit component uptake, this statistic is descriptive rather than a stable causal interaction estimate.

The secondary cache-adjusted view is:

```text
freshish = fresh_input_tokens + output_tokens
```

## 3. Execution and evidence integrity

The three provider-backed stack sessions completed successfully:

- [Fastify stack session](../../sources/evaluations/workflow-sessions/tokenjuice-jcodemunch-fastify-20260718-p-769d40697529-r1/run.json)
- [Beets stack session](../../sources/evaluations/workflow-sessions/tokenjuice-jcodemunch-beets-20260718-p-b440da225a3a-r1/run.json)
- [Terraform stack session](../../sources/evaluations/workflow-sessions/tokenjuice-jcodemunch-terraform-20260718-p-ded8609b4172-r1/run.json)

Every session has a checksum-verified four-file compact evidence bundle. All three:

- were accepted for token accounting;
- passed tool-isolation audit;
- passed verifier-integrity audit;
- recorded no prohibited external retrieval;
- completed all three persistent workflow turns;
- passed 3/3 structured final-state verifier tasks.

The matrix merged all three records and published compatible bare-baseline comparisons:

- [Fastify baseline comparison](../../sources/evaluations/workflow-sessions/baseline-fastify-20260718-vs-tokenjuice-jcodemunch-p-769d40697529-r1.json)
- [Beets baseline comparison](../../sources/evaluations/workflow-sessions/baseline-beets-20260718-vs-tokenjuice-jcodemunch-p-b440da225a3a-r1.json)
- [Terraform baseline comparison](../../sources/evaluations/workflow-sessions/baseline-terraform-20260718-vs-tokenjuice-jcodemunch-p-ded8609b4172-r1.json)

## 4. Results

### Table 1. Provider-token four-arm results

| Lane | Bare `N` | TokenJuice `A` | jcodemunch `B` | Stack `AB` | Stack vs bare | Better component | Stack vs better | Interaction |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| Fastify | 13,077,552 | 8,582,919 | 6,697,747 | 7,308,107 | -44.12% | jcodemunch | +9.11% | +5,104,993 |
| Beets | 17,423,571 | 18,143,576 | 17,318,314 | 18,458,613 | +5.94% | jcodemunch | +6.58% | +420,294 |
| Terraform | 43,392,324 | 26,074,453 | 36,885,960 | 41,388,865 | -4.62% | TokenJuice | +58.73% | +21,820,776 |
| **Aggregate** | **73,893,447** | **52,800,948** | **60,902,021** | **67,155,585** | **-9.12%** | **TokenJuice** | **+27.19%** | **+27,346,063** |

The stack beat bare Codex on Fastify and Terraform but increased tokens on Beets. It did not beat the better individual component in any lane.

### Table 2. Incremental stack comparisons

| Comparison | Provider-token delta | Percent |
|---|---:|---:|
| Stack vs bare Codex | -6,737,862 | -9.12% |
| Stack vs TokenJuice | +14,354,637 | +27.19% |
| Stack vs jcodemunch MCP | +6,253,564 | +10.27% |
| Stack vs aggregate best component | +14,354,637 | +27.19% |

Beating bare Codex is insufficient for stack promotion because the additional component must improve on the better individual profile. This stack fails that criterion clearly.

### Table 3. Aggregate token components

| Condition | Fresh input | Cached input | Output | Reasoning diagnostic | Provider total |
|---|---:|---:|---:|---:|---:|
| Bare Codex `N` | 2,107,031 | 71,452,672 | 333,744 | 165,237 | 73,893,447 |
| TokenJuice `A` | 1,716,779 | 50,767,104 | 317,065 | 156,373 | 52,800,948 |
| jcodemunch MCP `B` | 1,888,310 | 58,712,576 | 301,135 | 148,780 | 60,902,021 |
| Stack `AB` | 1,973,227 | 64,878,848 | 303,510 | 147,445 | 67,155,585 |

Cached input dominates every provider total. The secondary aggregate freshish result is directionally consistent with the primary decision:

- stack vs bare: -164,038 (-6.72%);
- stack vs TokenJuice: +242,893 (+11.94%);
- stack vs jcodemunch: +87,292 (+3.99%);
- interaction contrast: +494,223.

## 5. Correctness and natural-use diagnostics

All four retained conditions passed 9/9 structured verifier tasks across the three lanes. The stack therefore shows no structured correctness regression in this screen.

The compact Codex event streams show:

| Condition | Explicit TokenJuice commands | Explicit jcodemunch MCP calls |
|---|---:|---:|
| TokenJuice-only `A` | 0 | not configured |
| jcodemunch-only `B` | not configured | 0 |
| Stack `AB` | 0 | 0 |

Zero explicit use is valid under the frozen natural-availability estimand and is not grounds for a rerun. It materially limits mechanism interpretation, however. The observed differences cannot be attributed to realized TokenJuice output compaction, realized jcodemunch retrieval, or interaction between those mechanisms. They are trajectory observations under the named configured conditions.

## 6. Decision

The `stack-tokenjuice-jcodemunch-mcp` pair should **not advance** under the evaluated Codex/GPT-5.6-Luna lifecycle-v0 condition.

The decision follows the preregistered criteria:

1. **Versus bare baseline:** pass in aggregate (-9.12%), but fail on Beets (+5.94%).
2. **Versus the better component:** fail in every lane and aggregate (+27.19% versus aggregate-best TokenJuice).
3. **Interaction direction:** positive in all lanes; aggregate +27,346,063 provider tokens.
4. **Correctness:** pass, with 9/9 verifier tasks.
5. **Integrity and reproducibility:** pass, with all sessions accepted and all isolation/integrity checks passing.
6. **Portfolio robustness:** fail; the aggregate result is dominated by Terraform, where the stack is 58.73% worse than TokenJuice.
7. **Mechanism evidence:** absent; neither component was explicitly invoked in the stack sessions.

The first valid samples must remain in the dataset. They should not be rerun merely to seek component uptake or a more favorable outcome.

## 7. Next research step

Phase 3 should move to a different preregistered pair rather than replicate this stack immediately. The next candidate should preserve non-overlapping ownership while improving the chance that lifecycle-v0 naturally exercises both integrations. Any new pair should reuse compatible retained component records and add only the missing stack sessions, following the same first-valid-run and no-forced-uptake rules.

## 8. Reproducibility pointers

- Profile registry: [`data/evaluation-profiles.json`](../../data/evaluation-profiles.json)
- Session registry: [`data/workflow-sessions.json`](../../data/workflow-sessions.json)
- Frozen protocols: [`sources/evaluations/protocols/`](../../sources/evaluations/protocols/)
- Compact run evidence: [`sources/evaluations/workflow-sessions/`](../../sources/evaluations/workflow-sessions/)
- Evaluation framework: [`docs/evaluations/design/framework.md`](../evaluations/design/framework.md)
- Phase 2 component screen: [`docs/papers/phase-2-lifecycle-v0-natural-use-screening.md`](phase-2-lifecycle-v0-natural-use-screening.md)
