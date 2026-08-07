# Phase 2: Lifecycle V1 natural-use screening of token-saving integrations

## Executive summary

- **Scope:** 18 accepted product/runtime conditions, 36 persistent workflow sessions, and 108 accepted task outcomes across Fastify and Beets.
- **Codex:** nine product profiles used **32,960,518 raw provider tokens** and **6,223,979.8 weighted token-cost units**, versus **22,192,524** and **4,644,340.2** for repeated bare-Codex baselines: **+48.52% raw, +34.01% weighted**.
- **OpenCode:** nine product profiles used **27,628,957 raw provider tokens** and **5,417,264.0 weighted units**, versus **34,901,208** and **6,579,482.4** for the matched no-treatment OpenCode runtime control: **−20.84% raw, −17.66% weighted**.
- **Correctness:** all 108 accepted V1 tasks passed the active compile-based acceptance checks. Quality and maintainability were diagnostic, not token-eligibility gates.
- **Conclusion:** the screen shows a strong runtime × integration interaction. It does **not** establish a universally effective token-saving product or a stable ranking.

![Weighted token-cost change by runtime and product](figures/phase-2-lifecycle-v1-runtime-contrast.svg)

## Research question

Does assigning a documented token-saving integration reduce provider token usage in a realistic persistent coding workflow, relative to the matched no-treatment condition for the same runtime?

The estimand is assignment to the installed, native product surface under natural use. The evaluator did not require tool calls, minimum uptake, or a passing implementation to retain a token sample.

## Experimental design

| Item | Definition |
|---|---|
| Workflow | Fastify and Beets; feature implementation, behavior-preserving refactor, code review/correction |
| Session model | Three sequential tasks in one persistent agent session |
| Codex condition | Codex CLI, OpenAI GPT-5.6 Sol, `high` reasoning; bare-Codex matched baseline |
| OpenCode condition | OpenCode CLI 1.18.9, OpenAI GPT-5.6 Sol, `high` reasoning; native no-treatment runtime control |
| Treatment policy | Pinned native integration; natural use; no evaluator-forced invocation |
| Primary measure | Raw provider-reported token volume |
| Secondary measure | `fresh input + 0.1 × cached input + 6 × output` |
| Accounting | Reasoning is an output subset and is not added again |
| Evidence snapshot | 2026-08-05; registry SHA-256 `2a24d8f70d0e4a50927ce68f5498008bfce3c28f92bb0e70aefbec2533604a00` |

The same two baseline sessions are repeated descriptively across conditions within each runtime. Repetition does not create independent controls. Codex and OpenCode are reported separately because their runtime surfaces, event schemas, and control conditions differ.

## Results

### Aggregate runtime results

| Runtime | Conditions | Treatment sessions | Tasks | Treatment raw | Repeated baseline raw | Raw change | Treatment weighted | Baseline weighted | Weighted change |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Codex | 9 | 18 | 54/54 | 32,960,518 | 22,192,524 | +48.52% | 6,223,979.8 | 4,644,340.2 | +34.01% |
| OpenCode | 9 | 18 | 54/54 | 27,628,957 | 34,901,208 | -20.84% | 5,417,264.0 | 6,579,482.4 | -17.66% |

### Product/runtime contrasts

| Product | Codex weighted | OpenCode weighted | Codex raw | OpenCode raw | Codex tasks | OpenCode tasks |
|---|---:|---:|---:|---:|---:|---:|
| RTK | +42.31% | -26.12% | +55.76% | -34.62% | 6/6 | 6/6 |
| Serena | +0.83% | -26.03% | -6.79% | -30.03% | 6/6 | 6/6 |
| TokenJuice | +8.37% | -28.49% | +17.48% | -32.38% | 6/6 | 6/6 |
| Ponytail | +30.48% | -12.13% | +40.31% | -13.72% | 6/6 | 6/6 |
| Caveman | +32.24% | -27.43% | +48.47% | -29.66% | 6/6 | 6/6 |
| jCodeMunch | +28.45% | -3.34% | +51.43% | +2.29% | 6/6 | 6/6 |
| CodeGraph | +48.72% | -15.74% | +70.15% | -22.35% | 6/6 | 6/6 |
| SigMap | +27.74% | +2.54% | +33.68% | -0.20% | 6/6 | 6/6 |
| LowFat | — | -22.24% | — | -26.86% | blocked | 6/6 |
| Token Savior | +86.96% | — | +126.21% | — | 6/6 | blocked |

Negative values indicate lower treatment usage. The table is descriptive; it is not a stable product ranking.

![Sequence-level weighted token-cost change](figures/phase-2-lifecycle-v1-sequence-heatmap.svg)

### Token accounting decomposition

| Runtime | Component | Treatment | Repeated baseline | Difference |
|---|---|---:|---:|---:|
| Codex | Fresh input | 1,867,009 | 1,551,771 | 315,238 |
| Codex | Cached input | 30,882,048 | 20,466,432 | 10,415,616 |
| Codex | Output | 211,461 | 174,321 | 37,140 |
| Codex | Raw provider tokens | 32,960,518 | 22,192,524 | 10,767,994 |
| Codex | Weighted token cost | 6,223,979.8 | 4,644,340.2 | 1,579,639.6 |
| OpenCode | Fresh input | 1,630,694 | 1,834,668 | -203,974 |
| OpenCode | Cached input | 25,797,120 | 32,822,784 | -7,025,664 |
| OpenCode | Output | 201,143 | 243,756 | -42,613 |
| OpenCode | Raw provider tokens | 27,628,957 | 34,901,208 | -7,272,251 |
| OpenCode | Weighted token cost | 5,417,264.0 | 6,579,482.4 | -1,162,218.4 |

In Codex, the weighted increase is distributed across fresh input, cached input, and output. In OpenCode, all three components decrease in aggregate; the cached-input reduction contributes most of the weighted reduction.

![Weighted-cost component differences](figures/phase-2-lifecycle-v1-component-deltas.svg)

## Interpretation

### Codex

- No Codex profile reduced weighted usage in this screen.
- Serena was approximately neutral at **+0.83%**; TokenJuice was **+8.37%**; the remaining profiles were higher by **+27.74% to +86.96%**.
- RTK’s official Codex setup was used: `rtk init --global --codex`, lane-private `AGENTS.md` and `RTK.md`, and a pinned binary. Codex has an instruction-based integration rather than RTK’s automatic hook. The trace used many RTK prefixes, but unsupported forms such as `rtk rg` and `rtk sed` should be treated as passthrough rather than specialized filters.
- Caveman’s skills installed successfully, but the trace did not show behavioral activation. Its intended compression targets natural-language responses while coding commands, code, and reasoning remain in the workflow context.

### OpenCode

- Eight of nine OpenCode profiles reduced weighted usage; SigMap was slightly higher at **+2.54%**.
- The largest reductions were TokenJuice (**−28.49%**), RTK (**−26.12%**), Serena (**−26.03%**), and Caveman (**−27.43%**).
- These are OpenCode-native integration observations. They should not be transferred to bare Codex, where the integration surface and trajectory differ.

### Runtime interaction

The direction changes are systematic rather than a single outlier: the Codex aggregate increased by 34.01% weighted, while the OpenCode aggregate decreased by 17.66%. This is evidence of runtime-specific behavior, not proof that one runtime or product caused the full difference. Prompt serialization, caching, tool routing, command trajectories, and runtime accounting semantics remain potential contributors.

## Blocked combinations

- **LowFat / Codex:** No qualified native Codex integration; no PATH-only or generic adapter substitution.
- **Token Savior / OpenCode:** No qualified native OpenCode integration; no generic adapter substitution.

These combinations consumed no provider tokens and are excluded from the treatment totals.

## Limitations

- Each product/runtime condition has one treatment assignment per workflow; there is no within-condition replicate.
- Repeated baselines are descriptive and do not provide 18 independent control pairs.
- The two workflows cover only TypeScript and Python projects; results may not generalize to other repositories or task families.
- Raw and weighted measures answer different questions. Weighted cost is a declared diagnostic convention, not monetary cost.
- Provider usage does not identify which exact prompt, cached context, tool result, or trajectory step produced a difference.
- Compile/verifier success does not establish equal maintainability, correctness outside the tested contracts, latency, CPU cost, memory cost, or operational cost.
- Cross-runtime contrasts are screening evidence. They are not a causal comparison of Codex versus OpenCode.

## Conclusion

Lifecycle V1 shows that token-saving integrations can reduce provider usage in one runtime and increase it in another. In this screen, all nine Codex treatment conditions were at or above the matched weighted baseline, while eight of nine OpenCode conditions were below it. The result supports runtime-specific replication and better trajectory instrumentation—not a universal token-saving claim or deployment recommendation.

## Data availability

- Authoritative registry: [`data/workflow-sessions.json`](../../data/workflow-sessions.json)
- Derived report dataset: [`phase-2-lifecycle-v1-report-data-20260807.json`](../../sources/evaluations/audits/phase-2-lifecycle-v1-report-data-20260807.json)
- Accepted requested-tool audit: [`requested-five-tools-lifecycle-v1-20260805.json`](../../sources/evaluations/audits/requested-five-tools-lifecycle-v1-20260805.json)
- Codex panel: [`current-panel-codex-sol-high-lifecycle-v1-20260805.json`](../../sources/evaluations/audits/current-panel-codex-sol-high-lifecycle-v1-20260805.json)
- OpenCode panel: [`requested-panel-opencode-sol-high-lifecycle-v1-20260805.json`](../../sources/evaluations/audits/requested-panel-opencode-sol-high-lifecycle-v1-20260805.json)
- Compact workflow evidence: [`sources/evaluations/workflow-sessions/`](../../sources/evaluations/workflow-sessions/)
