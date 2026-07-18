# GPT-5.6 Sol/High Persistent-Baseline Variance Screen

**Status:** corrected descriptive model-condition screen; not confirmatory

**Evidence collected:** 2026-07-16 (Luna/`xhigh`) and 2026-07-18 (Sol/`high`)

## Abstract

Three accepted persistent lifecycle replicates were available for each of Fastify, Beets, and Terraform under two compound conditions:

- GPT-5.6 Luna with `xhigh` reasoning;
- GPT-5.6 Sol with `high` reasoning.

A post-run accounting audit found that the legacy extractor summed three cumulative Codex thread-usage snapshots. Codex 0.144.0 emits `ThreadTokenUsage.total` in each `turn.completed.usage` record, so the correct session total is the final cumulative snapshot for each thread, not the sum of snapshots. The raw compact bundles remain unchanged; this report uses the correction audit.

After correction, the nine Sol/`high` sessions used **68,275,315 total provider tokens**, compared with **100,856,945** for Luna/`xhigh`. This is a **32.30% lower pooled total**. The geometric mean of the three paired portfolio ratios is **0.6720**, or **32.80% lower**.

Variance did not improve uniformly. Sequence-level coefficient of variation fell for Fastify and Beets but rose for Terraform. Portfolio CV rose from **5.66%** to **16.29%**, largely because corrected Terraform r0 remained high at 15.526M tokens versus 10.962M and 10.762M in r1 and r2. The evidence supports **lower observed token volume with mixed variance**, not a general variance-reduction claim.

## Accounting correction

The retained runner used `scripts/extract_codex_usage.py` to sum all `turn.completed.usage` blocks. That is incorrect for resumed persistent threads:

1. Codex 0.144.0 receives `ThreadTokenUsageUpdated`, whose payload contains `total` and `last` usage.
2. The JSONL event processor stores the notification and emits `usage_from_last_total()` at turn completion.
3. `usage_from_last_total()` reads `token_usage.total`.
4. Each of the three workflow tasks resumed the same thread, so its usage blocks were cumulative snapshots.

The correction therefore:

- selects the final cumulative usage snapshot for each distinct thread;
- sums only across distinct threads;
- computes per-task usage by differencing consecutive cumulative snapshots from the same thread;
- fails closed if a cumulative counter decreases;
- preserves every historical compact bundle and legacy registry value.

The correction audit covers all 30 retained workflow sessions. Every session required correction. Across that larger registry, the legacy extractor reported 624,852,758 tokens versus a corrected 312,219,452.

Source evidence is pinned to OpenAI Codex `rust-v0.144.0`, commit `767822446c7a594caa19609ca435281a9ec67e0d`, `codex-rs/exec/src/event_processor_with_jsonl_output.rs`, lines 496–522.

## Research question

Does changing the persistent bare-Codex baseline from Luna/`xhigh` to Sol/`high` reduce total provider-token volume or its replicate-to-replicate dispersion across the retained lifecycle workflows?

This is a descriptive screen of a compound condition. It does not isolate model from reasoning effort.

## Evidence panel

| Condition | Model | Effort | Sequences | Replicates | Sessions | Tasks |
|---|---|---:|---:|---:|---:|---:|
| Luna baseline | `gpt-5.6-luna` | `xhigh` | 3 | 3 | 9 | 27 |
| Sol comparison | `gpt-5.6-sol` | `high` | 3 | 3 | 9 | 27 |

For all 18 selected sessions:

- compact manifests passed: 18/18;
- compact manifest files matched: 54/54;
- accounting corrections reconciled task increments to final thread totals: 18/18;
- task verifiers passed: 54/54;
- final concealed verifiers passed: 18/18;
- operational retries: 0;
- tool-isolation and verifier-integrity checks passed;
- external-retrieval hits: 0.

Checksum validity is not the same as strict nested parseability. Recursive review checked 368 embedded JSON, JSONL, and TOML artifacts. Thirty-four Codex event JSONL artifacts contain 2,228 raw stderr or non-object physical lines, counting duplication between aggregate and per-task streams. Structured usage records remain complete and reconcile under the corrected accounting rule.

## Corrected provider-token results

### Per sequence and replicate

| Sequence | Condition | r0 | r1 | r2 | Three-replicate sum |
|---|---|---:|---:|---:|---:|
| Fastify | Luna/`xhigh` | 6,420,074 | 6,712,770 | 4,617,123 | 17,749,967 |
| Fastify | Sol/`high` | 4,464,422 | 4,465,189 | 3,954,296 | 12,883,907 |
| Beets | Luna/`xhigh` | 12,244,729 | 8,728,732 | 9,238,446 | 30,211,907 |
| Beets | Sol/`high` | 7,048,538 | 5,284,953 | 5,808,516 | 18,142,007 |
| Terraform | Luna/`xhigh` | 15,863,828 | 19,453,066 | 17,578,177 | 52,895,071 |
| Terraform | Sol/`high` | 15,526,000 | 10,961,655 | 10,761,746 | 37,249,401 |
| **Portfolio** | **Luna/`xhigh`** | **34,528,631** | **34,894,568** | **31,433,746** | **100,856,945** |
| **Portfolio** | **Sol/`high`** | **27,038,960** | **20,711,797** | **20,524,558** | **68,275,315** |

All nine sequence/replicate cells used fewer corrected tokens under Sol/`high`.

### Component totals

| Component | Luna/`xhigh` | Sol/`high` | Pooled change |
|---|---:|---:|---:|
| Fresh input | 3,047,685 | 1,772,924 | −41.83% |
| Cached input | 97,370,624 | 66,216,192 | −32.00% |
| Output | 438,636 | 286,199 | −34.75% |
| Reasoning subset | 210,611 | 117,484 | −44.22% |
| **Total provider tokens** | **100,856,945** | **68,275,315** | **−32.30%** |

Cached input contributed 96.54% of Luna total and 96.98% of Sol total. Persistent-context replay remains the dominant accounting component.

Reasoning tokens are a subset of output tokens and are not added again to total provider tokens.

## Dispersion

### Sequence-level total-token dispersion

| Sequence | Luna mean | Luna CV | Luna log SD | Sol mean | Sol CV | Sol log SD | Mean change |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fastify | 5.917M | 19.18% | 0.2044 | 4.295M | 6.86% | 0.0701 | −27.41% |
| Beets | 10.071M | 18.87% | 0.1813 | 6.047M | 14.98% | 0.1468 | −39.95% |
| Terraform | 17.632M | 10.18% | 0.1020 | 12.416M | 21.70% | 0.2065 | −29.58% |

### Portfolio-level dispersion

| Condition | Replicate totals | Mean | CV | Log SD |
|---|---|---:|---:|---:|
| Luna/`xhigh` | 34.529M, 34.895M, 31.434M | 33.619M | 5.66% | 0.0575 |
| Sol/`high` | 27.039M, 20.712M, 20.525M | 22.758M | 16.29% | 0.1566 |

The corrected result still rejects a blanket variance-reduction interpretation. Fastify and Beets were less dispersed, while Terraform and the aggregate portfolio were more dispersed.

## Terraform Sol/High r0 forensic note

Terraform r0 is a real trajectory outlier, but its legacy 31.472M total was not real session usage. The corrected total is **15,526,000**.

Corrected per-task increments were:

| Task | r0 | r1 | r2 |
|---|---:|---:|---:|
| Feature implementation | 4,999,516 | 2,315,861 | 2,255,641 |
| Behavior-preserving refactor | 5,946,754 | 4,425,306 | 4,084,274 |
| Review correction | 4,579,730 | 4,220,488 | 4,421,831 |

The excess is concentrated in task 1 and, through persistent context replay, task 2. r0 made more task-1 command executions and edits, ran broader focused, vet, formatting, and race checks, and produced a larger task-1 patch. It had no provider error event, no operational retry, and all concealed verifiers passed.

One diagnostics defect remains: Codex could not write the task-1 `--output-last-message` file because its parent artifact directory was absent. The final task-1 agent message is still present in the valid JSONL event stream, and tasks 2–3 resumed the same thread successfully. This affects diagnostics completeness, not provider accounting or task execution eligibility.

## Paired portfolio comparison

| Replicate | Luna/`xhigh` | Sol/`high` | Ratio | Change |
|---|---:|---:|---:|---:|
| r0 | 34,528,631 | 27,038,960 | 0.7831 | −21.69% |
| r1 | 34,894,568 | 20,711,797 | 0.5936 | −40.64% |
| r2 | 31,433,746 | 20,524,558 | 0.6529 | −34.71% |

The geometric mean paired ratio is 0.6720, corresponding to **32.80% lower** Sol/`high` usage. Because six of nine pairs differ in fixture-runner hash and the condition changes both model and effort, these paired ratios are descriptive rather than strict causal estimates.

## Task-order interpretation

Corrected per-task increments change the earlier order-effect interpretation. Across all workflows:

| Task class | Luna mean | Sol mean |
|---|---:|---:|
| Feature implementation | 3.599M | 1.933M |
| Behavior-preserving refactor | 4.766M | 3.034M |
| Review correction | 2.842M | 2.618M |

The legacy extractor made later tasks appear most expensive because each later block included all earlier thread usage. After differencing cumulative snapshots, the refactor task has the largest average incremental cost, and the review-correction task shows the smallest model-condition reduction.

## Trajectory diagnostics

Sol/`high` issued fewer native command executions and fewer provider events across the panel. These are plausible mechanisms for lower token usage, not covariates to remove from the primary outcome. Command counts do not explain every cell; Terraform r0 retained a heavier task-1 trajectory and persistent replay burden.

Provider tool-call counts remain zero because the bare baseline represents native shell operations as `command_execution` items rather than provider tool-call items.

## Interpretation

The corrected evidence supports three limited statements:

1. Sol/`high` used fewer provider tokens in every matched sequence/replicate cell.
2. The reduction was large in pooled and paired summaries, at roughly 32–33%.
3. Variance effects were heterogeneous: lower for Fastify and Beets, higher for Terraform and the portfolio aggregate.

It does not support:

- a model-only causal effect;
- an effort-only causal effect;
- a general claim that Sol lowers persistent-workflow variance;
- exclusion of Terraform r0 merely because it is high;
- continued use of legacy registry token totals without the correction overlay.

## Limitations

1. There are only three replicates per sequence and condition.
2. Model and reasoning effort change together.
3. Collection date was not randomized or blocked.
4. Six of nine matched pairs use a different fixture-runner hash; only r2 is an exact runner-hash match.
5. The correction is derived from immutable raw events and pinned Codex source semantics; historical registry and compact provider-summary values remain legacy values.
6. Some embedded JSONL diagnostics contain raw stderr and are not strictly line-parseable.
7. Verifier success establishes task-contract acceptance, not equivalence of implementation quality across replicas.

## Reproduction

From the repository root:

```bash
python3 scripts/audit_codex_cumulative_usage.py
python3 scripts/analyze_model_condition_baselines.py
```

Machine-readable evidence:

- [Cumulative Codex usage correction audit](../../sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json)
- [Corrected Sol/high variance audit](../../sources/evaluations/audits/gpt-5-6-sol-high-baseline-variance-20260718.json)
- [Workflow session registry](../../data/workflow-sessions.json)
- [Compact workflow evidence bundles](../../sources/evaluations/workflow-sessions/)

## Conclusion

After correcting cumulative-thread accounting, Sol/`high` used materially fewer provider tokens than Luna/`xhigh`, but the experiment still does not show general variance reduction. Terraform r0 is a valid high-trajectory sample at 15.526M corrected tokens, not a 31.472M session. The main defect was systemic extraction, not a provider failure unique to that run.
