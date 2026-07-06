# Phase 3 report: TokenJuice + jcodemunch MCP lifecycle-v0 stack screen

> **Report status:** withdrawn historical product-effect screen. The narrative preserves the arithmetic reported at the time, but the three corrupted stack sessions, comparisons, compact bundles, and protocols were deleted from the active corpus under receipt. The decision is superseded by the [official-integration parity audit](official-integration-parity-audit.md).
>
> **Accounting supersession (2026-07-18):** persistent-session totals in this report also sum cumulative Codex `ThreadTokenUsage.total` snapshots and are inflated. Use the [cumulative usage correction audit](../../sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json) for retained-session accounting. The deleted stack rows remain historical arithmetic only.
>
> **Superseding adjudication (2026-07-18):** TokenJuice's required Codex hook was absent and explicitly disabled; jcodemunch used an unverified launcher and retained no successful MCP handshake. The stack records were deleted rather than relabelled as baseline. No corrected stack protocol will be created until both versioned individual components have valid evidence.

**Report date:** 2026-07-18

**Evidence collection:** 2026-07-18

**Evidence stage:** `reproduction`

**Runtime/model condition:** Codex CLI, OpenAI GPT-5.6 Luna, `xhigh` reasoning

**Primary metric:** cumulative provider-reported tokens per complete persistent workflow session

## Abstract

This Phase 3 screen evaluates the compatibility-safe `stack-tokenjuice-jcodemunch-mcp` profile on the unchanged lifecycle-v0 Fastify, Beets, and Terraform workflows. TokenJuice owns the terminal-output surface and jcodemunch MCP owns retrieval context. The experiment reuses the compatible retained `r1` bare-Codex, TokenJuice-only, and jcodemunch-only records and adds only the missing stack treatment in each lane.

The three stack executions completed, passed tool-isolation and verifier-integrity checks, and passed all nine structured workflow verifiers. Their retained provider totals were 67,155,585 tokens: 6,737,862 fewer than bare Codex (-9.12%), 14,354,637 more than the historical TokenJuice arm (+27.19%), and 6,253,564 more than the historical jcodemunch arm (+10.27%). These are forensic accounting contrasts across defective or unverified treatments, not valid component or stack effects.

No TokenJuice hook could execute because the historical Codex configuration disabled hooks and no `hooks.json` was installed. No retained jcodemunch handshake or completed model MCP call proves that component was operational. The prior “does not advance” decision is therefore withdrawn; the tested condition cannot accept or reject the correctly installed stack.

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

Zero visible use is not itself grounds for an outcome-selected rerun. Here, however, independent retained setup evidence proves that the TokenJuice mechanism was disabled, while the jcodemunch assignment lacks the required operational handshake proof. The observed differences therefore remain provider-accounting trajectories under a partial configuration and cannot support product, mechanism, or interaction claims.

## 6. Decision

The prior **does not advance** decision is withdrawn. The historical `stack-tokenjuice-jcodemunch-mcp` profile did not assign the intended two-product stack and therefore cannot satisfy or fail its preregistered incremental-value criteria.

The retained arithmetic still records what occurred:

1. the partial configuration used 9.12% fewer tokens than bare Codex in aggregate;
2. it used 27.19% more than the historical TokenJuice CLI-only arm;
3. all nine workflow verifiers passed;
4. the TokenJuice Codex mechanism was disabled;
5. jcodemunch operational assignment was not positively proven.

The sessions and comparisons remain in the dataset as excluded forensic records. They must not be rerun in place or relabeled as the corrected treatment.

## 7. Next research step

Do not move directly to another stack based on these component rankings. First qualify the versioned `terminal-tokenjuice-codex-hook-v1` and neutral `retrieval-jcodemunch-mcp-direct-v1` assignments. If the intended jcodemunch estimand includes its separate usage-guidance layer, preregister that as another versioned instruction-policy profile. A corrected stack requires separate preregistration and new profile identity after the intended individual assignments are proven.

## 8. Reproducibility pointers

- Profile registry: [`data/evaluation-profiles.json`](../../data/evaluation-profiles.json)
- Session registry: [`data/workflow-sessions.json`](../../data/workflow-sessions.json)
- Frozen protocols: [`sources/evaluations/protocols/`](../../sources/evaluations/protocols/)
- Compact run evidence: [`sources/evaluations/workflow-sessions/`](../../sources/evaluations/workflow-sessions/)
- Evaluation framework: [`docs/evaluations/design/framework.md`](../evaluations/design/framework.md)
- Phase 2 component screen: [`docs/papers/phase-2-lifecycle-v0-natural-use-screening.md`](phase-2-lifecycle-v0-natural-use-screening.md)
