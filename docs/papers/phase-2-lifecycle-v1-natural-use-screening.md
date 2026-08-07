# Phase 2: Lifecycle V1 natural-use screening of token-saving integrations

## Executive summary

- **Scope:** 23 matched product/runtime conditions, 46 persistent workflow sessions, and 138 accepted task outcomes across Fastify and Beets.
- **Codex:** 14 product profiles used **9,760,614.0 weighted token-cost units**, versus **7,224,529.2** for repeated bare-Codex baselines: **+35.10%**.
- **OpenCode:** 9 product profiles used **5,417,264.0 weighted token-cost units**, versus **6,579,482.4** for the matched no-treatment OpenCode runtime control: **-17.66%**.
- **Correctness:** all 138 accepted V1 tasks passed the active compile-based acceptance checks. Quality and maintainability were diagnostic, not token-eligibility gates.
- **Conclusion:** the screen shows a strong runtime × integration interaction. It does **not** establish a universally effective token-saving product or a stable ranking.

![Weighted token-cost change by runtime and product](figures/phase-2-lifecycle-v1-runtime-contrast.svg)

## Research question

Does assigning a documented token-saving integration reduce **weighted token cost** in a realistic persistent coding workflow, relative to the matched no-treatment condition for the same runtime?

The estimand is assignment to the installed, native product surface under natural use. The evaluator did not require tool calls, minimum uptake, or a passing implementation to retain a token sample.

## Experimental design

| Item | Definition |
|---|---|
| Workflow | Fastify and Beets; feature implementation, behavior-preserving refactor, code review/correction |
| Session model | Three sequential tasks in one persistent agent session |
| Codex condition | Codex CLI, OpenAI GPT-5.6 Sol, `high` reasoning; bare-Codex matched baseline |
| OpenCode condition | OpenCode CLI 1.18.9, OpenAI GPT-5.6 Sol, `high` reasoning; native no-treatment runtime control |
| Treatment policy | Pinned native integration; natural use; no evaluator-forced invocation |
| Primary measure | Weighted token cost |
| Accounting | `fresh input + 0.1 × cached input + 6 × output`; reasoning is an output subset and is not added again |
| Evidence snapshot | 2026-08-07; registry SHA-256 `dd5b72d37e6159726ba9d79a7103a762f395ecd64acc3acc1b9fe58941b6348f` |

The same two baseline sessions are repeated descriptively across conditions within each runtime. Repetition does not create independent controls. Codex and OpenCode are reported separately because their runtime surfaces, event schemas, and control conditions differ.

## Results

### Aggregate runtime results

| Runtime | Conditions | Treatment sessions | Tasks | Treatment weighted cost | Baseline weighted cost | Weighted change |
|---|---:|---:|---:|---:|---:|---:|
| Codex | 14 | 28 | 84/84 | 9,760,614.0 | 7,224,529.2 | +35.10% |
| OpenCode | 9 | 18 | 54/54 | 5,417,264.0 | 6,579,482.4 | -17.66% |

### Product/runtime contrasts

| Product | Codex weighted Δ | OpenCode weighted Δ | Codex tasks | OpenCode tasks |
|---|---:|---:|---:|---:|
| RTK | +42.31% | -26.12% | 6/6 | 6/6 |
| Serena | +0.83% | -26.03% | 6/6 | 6/6 |
| TokenJuice | +8.37% | -28.49% | 6/6 | 6/6 |
| Ponytail | +30.48% | -12.13% | 6/6 | 6/6 |
| Caveman | +32.24% | -27.43% | 6/6 | 6/6 |
| jCodeMunch | +28.45% | -3.34% | 6/6 | 6/6 |
| CodeGraph | +48.72% | -15.74% | 6/6 | 6/6 |
| SigMap | +27.74% | +2.54% | 6/6 | 6/6 |
| LowFat | — | -22.24% | blocked | 6/6 |
| Token Savior | +86.96% | — | 6/6 | blocked |
| Graphify | +70.45% | — | 6/6 | blocked |
| LeanCTX | +31.24% | — | 6/6 | blocked |
| Snip | +20.29% | — | 6/6 | blocked |
| Cartog | +52.02% | — | 6/6 | blocked |
| CodeScope | +11.34% | — | 6/6 | blocked |

Negative values indicate lower treatment usage. The table is descriptive; it is not a stable product ranking.

![Sequence-level weighted token-cost change](figures/phase-2-lifecycle-v1-sequence-heatmap.svg)

### Token accounting decomposition

| Runtime | Component | Treatment | Repeated baseline | Difference |
|---|---|---:|---:|---:|
| Codex | Fresh input | 2,897,706.0 | 2,413,866.0 | 483,840.0 |
| Codex | Cached input × 0.1 | 4,856,064.0 | 3,183,667.2 | 1,672,396.8 |
| Codex | Output × 6 | 2,006,844.0 | 1,626,996.0 | 379,848.0 |
| Codex | Weighted token cost | 9,760,614.0 | 7,224,529.2 | 2,536,084.8 |
| OpenCode | Fresh input | 1,630,694.0 | 1,834,668.0 | -203,974.0 |
| OpenCode | Cached input × 0.1 | 2,579,712.0 | 3,282,278.4 | -702,566.4 |
| OpenCode | Output × 6 | 1,206,858.0 | 1,462,536.0 | -255,678.0 |
| OpenCode | Weighted token cost | 5,417,264.0 | 6,579,482.4 | -1,162,218.4 |

In Codex, the weighted increase is distributed across fresh input, cached input, and output. In OpenCode, all three components decrease in aggregate; the cached-input reduction contributes most of the weighted reduction.

![Weighted-cost component differences](figures/phase-2-lifecycle-v1-component-deltas.svg)

## Interpretation

### Codex

- 0 of 14 Codex profiles reduced weighted token cost in this screen.
- These Codex observations are descriptive screening evidence; they do not establish a stable product ranking.
- RTK’s official Codex setup was used: `rtk init --global --codex`, lane-private `AGENTS.md` and `RTK.md`, and a pinned binary. Codex has an instruction-based integration rather than RTK’s automatic hook.
- Caveman’s skills installed successfully, but the trace did not show behavioral activation. Its intended compression targets natural-language responses while coding commands, code, and reasoning remain in the workflow context.

### OpenCode

- 8 of 9 OpenCode profiles reduced weighted token cost in this screen.
- These are OpenCode-native integration observations. They should not be transferred to bare Codex, where the integration surface and trajectory differ.

### Runtime interaction

The Codex aggregate changed by +35.10% weighted, while the OpenCode aggregate changed by -17.66%. This is evidence of runtime-specific behavior, not proof that one runtime or product caused the full difference. Prompt serialization, caching, tool routing, command trajectories, and runtime accounting semantics remain potential contributors.

## Blocked combinations

- **LowFat / Codex:** No qualified native Codex integration; no PATH-only or generic adapter substitution.
- **Token Savior / OpenCode:** No qualified native OpenCode integration; no generic adapter substitution.

These combinations produced no provider-backed treatment result and are excluded from the treatment totals.

## Limitations

- Each product/runtime condition has one treatment assignment per workflow; there is no within-condition replicate.
- Repeated baselines are descriptive and do not provide 23 independent control pairs.
- The two workflows cover only TypeScript and Python projects; results may not generalize to other repositories or task families.
- Weighted token cost is the sole outcome reported here. It is a declared accounting convention, not monetary cost.
- The weighted account does not identify which exact prompt, cached context, tool result, or trajectory step produced a difference.
- Compile/verifier success does not establish equal maintainability, correctness outside the tested contracts, latency, CPU cost, memory cost, or operational cost.
- Cross-runtime contrasts are screening evidence. They are not a causal comparison of Codex versus OpenCode.

## Conclusion

Lifecycle V1 shows that token-saving integrations can reduce **weighted token cost** in one runtime and increase it in another. In this screen, 0 of 14 Codex treatment conditions and 8 of 9 OpenCode conditions were below the matched weighted baseline. The result supports runtime-specific replication and better trajectory instrumentation—not a universal token-saving claim or deployment recommendation.

## Data availability

- Authoritative registry: [`data/workflow-sessions.json`](../../data/workflow-sessions.json)
- Derived report dataset: [`phase-2-lifecycle-v1-report-data-20260807.json`](../../sources/evaluations/audits/phase-2-lifecycle-v1-report-data-20260807.json)
- Cumulative Codex usage audit: [`codex-cumulative-usage-accounting-20260718.json`](../../sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json)
- Compact workflow evidence: [`sources/evaluations/workflow-sessions/`](../../sources/evaluations/workflow-sessions/)
