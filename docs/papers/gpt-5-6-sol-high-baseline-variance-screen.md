# GPT-5.6 Sol/High Persistent-Baseline Variance Screen

**Status:** descriptive model-condition screen; not confirmatory

**Evidence collected:** 2026-07-16 (Luna/`xhigh`) and 2026-07-18 (Sol/`high`)

**Runtime:** Codex CLI 0.144.0

**Workflow unit:** one persistent three-task lifecycle-v0 session

**Primary metric:** provider-reported total tokens, including cached input

## Abstract

Three fresh replicates of each Fastify, Beets, and Terraform persistent baseline were run with GPT-5.6 Sol at `high` reasoning. All nine Sol sessions completed without operational retry, passed all 27 task verifiers and all nine final concealed verifiers, passed isolation/integrity checks, and retained checksum-valid compact evidence bundles.

Across the nine sessions, Sol/`high` used **130,385,748** total provider tokens versus **208,531,229** for the retained Luna/`xhigh` panel, a descriptive pooled difference of **-37.47%**. The geometric mean of the three portfolio-level replicate ratios was **-38.19%**. Every sequence/replicate cell was lower under Sol/`high`.

This screen does **not** show that Sol/`high` generally reduces run-to-run variance. Fastify and Beets dispersion decreased, but Terraform dispersion increased, and the three-lane portfolio coefficient of variation increased from **8.54%** to **21.17%** because Sol replicate 0 was much larger than replicates 1 and 2. The strongest supported result is lower observed token volume in this panel, not lower variance.

## Research question and claim boundary

The screen asks whether changing the compound agent condition from GPT-5.6 Luna/`xhigh` to GPT-5.6 Sol/`high` changes token volume and descriptive run-to-run dispersion in the existing persistent baseline workflows.

The estimand is condition assignment for the complete workflow. Tool commands, event counts, and accumulated context are post-treatment trajectory mechanisms and are not regressed out of the primary outcome.

The evidence supports descriptive statements about these 18 retained sessions. It does not isolate model identity from reasoning effort, estimate a population variance with useful precision, or establish deployment superiority.

## Methods

### Panel

Each condition contains:

- three Fastify lifecycle-v0 sessions;
- three Beets lifecycle-v0 sessions;
- three Terraform lifecycle-v0 sessions;
- replicates `r0`, `r1`, and `r2` for every sequence;
- feature implementation, behavior-preserving refactor, and code-review correction in one persistent Codex thread per session.

Repository, agent home, tool state, caches, and temporary state were fresh before each session and persisted across the three tasks within that session. Prompts were disclosed sequentially. Concealed acceptance assets remained controller-only until final verification.

### Compound conditions

| Condition ID | Model | Reasoning effort | Role |
|---|---|---:|---|
| `codex-openai-gpt-5-6-luna-xhigh` | `gpt-5.6-luna` | `xhigh` | retained active-default baseline |
| `codex-openai-gpt-5-6-sol-high` | `gpt-5.6-sol` | `high` | active model-comparison baseline |

The conditions must not be pooled as one baseline identity. The Sol condition has its own frozen protocols and baseline-pool fingerprints.

### Accounting

Total provider tokens equal Codex-reported input tokens plus output tokens. Fresh input is input minus cached input. Reasoning tokens are a reported subset of output tokens and are not added again.

### Nuisance-control audit

All 18 sessions used:

- Codex CLI 0.144.0;
- bare-Codex control profile with no MCP, global instructions, hooks, skills, plugins, warm indexes, or token-saving tools;
- Docker image `sha256:6f86d01f2c63f5029c6bb874d8f3694c24d5cd567e3d09413eccc956ba3feafe`;
- identical sequence-specific rendered prompt hashes;
- the same sequence and replicate labels.

A material caveat remains: Luna `r0` and `r1` froze fixture-runner hash `6b8058…`, while Luna `r2` and all Sol sessions froze `eea63c…`. The intervening runner changes expanded qualification, integration, and compact-evidence machinery. Six of nine condition pairs therefore differ in a controller implementation identity even though model-facing prompts, image, CLI, profile, and sequence are equal. Only the three `r2` pairs match every audited nuisance-control field. The full panel is useful descriptively but is not a fully blocked causal model comparison.

## Evidence inventory and integrity

| Condition | Sessions | Tasks passed | Final verifiers | Operational retries | Manifest files checked |
|---|---:|---:|---:|---:|---:|
| Luna/`xhigh` | 9 | 27/27 | 9/9 | 0 | 27/27 |
| Sol/`high` | 9 | 27/27 | 9/9 | 0 | 27/27 |

All sessions were marked valid and token-accounting eligible. All tool-isolation and verifier-integrity checks passed, and no external-retrieval hits were recorded.

Checksum validity is not the same as nested format validity. A recursive audit parsed 368 embedded JSON, JSONL, and TOML artifacts. Thirty-four Codex event JSONL artifacts contained 2,228 raw-stderr or non-object physical lines: 2,012 in the Luna bundles and 216 in the Sol bundles. The count includes duplication between aggregate and per-task event streams. Structured `provider-usage.json` records and their three usage blocks per session parsed and reconciled to every retained total, so the token accounting remains usable; strict event-level diagnostics are degraded and event-line parse failures are not compared as model behavior.

## Provider-token results

### Replicate-level totals

| Replicate | Condition | Fastify | Beets | Terraform | Three-lane total | Sol change vs Luna |
|---:|---|---:|---:|---:|---:|---:|
| r0 | Luna/`xhigh` | 12,950,066 | 25,369,525 | 33,564,150 | 71,883,741 | — |
| r0 | Sol/`high` | 8,387,234 | 14,219,882 | 31,471,786 | 54,078,902 | -24.77% |
| r1 | Luna/`xhigh` | 13,077,552 | 17,423,571 | 43,392,324 | 73,893,447 | — |
| r1 | Sol/`high` | 8,097,854 | 10,350,366 | 20,018,683 | 38,466,903 | -47.94% |
| r2 | Luna/`xhigh` | 7,642,570 | 17,612,278 | 37,499,193 | 62,754,041 | — |
| r2 | Sol/`high` | 7,106,525 | 11,376,116 | 19,357,302 | 37,839,943 | -39.70% |

All nine sequence/replicate ratios favored lower token volume under Sol/`high`:

- Fastify: -35.23%, -38.08%, and -7.01%; paired geometric mean -28.02%.
- Beets: -43.95%, -40.60%, and -35.41%; paired geometric mean -40.09%.
- Terraform: -6.23%, -53.87%, and -48.38%; paired geometric mean -39.33%.

Because six pairs differ in fixture-runner identity, these ratios are descriptive condition contrasts rather than fully matched causal estimates.

### Run-to-run dispersion

| Sequence/portfolio | Luna mean | Luna CV | Luna log SD | Sol mean | Sol CV | Sol log SD | Mean change |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fastify | 11,223,396 | 27.64% | 0.307 | 7,863,871 | 8.54% | 0.087 | -29.93% |
| Beets | 20,135,125 | 22.52% | 0.214 | 11,982,121 | 16.73% | 0.163 | -40.49% |
| Terraform | 38,151,889 | 12.97% | 0.129 | 23,615,924 | 28.84% | 0.271 | -38.10% |
| Three-lane total | 69,510,410 | 8.54% | 0.087 | 43,461,916 | 21.17% | 0.202 | -37.47% |

The variance result is mixed. Sol/`high` was more stable on Fastify and Beets but less stable on Terraform and on the aggregate portfolio. With only three replicates, each coefficient of variation is highly sensitive to one trajectory.

### Token components

| Component | Luna/`xhigh` | Sol/`high` | Sol change |
|---|---:|---:|---:|
| Fresh input | 6,740,374 | 3,936,941 | -41.59% |
| Cached input | 200,846,080 | 125,838,080 | -37.35% |
| Output | 944,775 | 610,727 | -35.36% |
| Reasoning subset | 453,720 | 246,443 | -45.68% |
| Total provider tokens | 208,531,229 | 130,385,748 | -37.47% |

Cached input dominated both conditions: 96.31% of Luna total and 96.51% of Sol total. The observed reduction therefore primarily reflects shorter or fewer accumulated-context replays, not merely shorter final answers. Sol also used fewer fresh-input, output, and reasoning tokens.

### Task-class totals

Mean provider tokens per task across nine observations per class:

| Task class | Luna/`xhigh` mean | Sol/`high` mean | Sol change |
|---|---:|---:|---:|
| Feature implementation | 3,599,076 | 1,933,358 | -46.28% |
| Behavior-preserving refactor | 8,364,733 | 4,967,801 | -40.61% |
| Code-review correction | 11,206,327 | 7,586,146 | -32.30% |

Later persistent tasks remained more expensive because they replayed more accumulated context. Sol/`high` reduced the observed mean in every task class, but the relative reduction narrowed by the final review task.

## Trajectory diagnostics

| Diagnostic across nine sessions | Luna/`xhigh` | Sol/`high` | Sol change |
|---|---:|---:|---:|
| Provider events | 1,987 | 1,289 | -35.13% |
| Native command executions | 743 | 446 | -39.97% |
| Native command failures | 87 | 67 | -22.99% |
| File-change items | 103 | 75 | -27.18% |
| Agent-message items | 152 | 154 | +1.32% |
| Provider tool calls observed | 0 | 0 | — |

“Provider tool calls observed” is the extractor's dedicated tool-call field. These bare-Codex runs instead expose shell/edit activity as native `command_execution` and `file_change` items, so zero dedicated tool calls does not mean no agent actions.

The lower command and event counts are consistent with fewer model round trips and less context replay under Sol/`high`, but they are post-treatment mechanisms. The screen does not establish that command count caused the token reduction. Non-JSON event-line counts are omitted from comparison because the controller runner and event-capture implementation changed between Luna `r0`/`r1` and the later sessions.

## Correctness and quality boundary

All 18 sessions passed their structured task and final verifiers. That supports functional correctness on the frozen acceptance suites. Independent source-review fields remain `not-reviewed`, so this report does not claim equivalent maintainability, design quality, or merge readiness.

No sample was rerun because of its token direction, tool behavior, or verifier result. Replicate 0's initial matrix exit was a post-merge controller validation defect: all three provider lanes had already completed and their first samples were retained. The protected test and generated runbook were repaired without rerunning or modifying those sessions.

## Interpretation

### Supported

- In this panel, Sol/`high` used substantially fewer total provider tokens than Luna/`xhigh` in every sequence/replicate cell.
- The reduction affected cached input, fresh input, output, and reasoning components.
- Sol/`high` produced fewer native command and provider-event items while still passing all structured verifiers.
- Fastify and Beets showed lower descriptive run-to-run dispersion under Sol/`high`.

### Not supported

- A general claim that Sol/`high` reduces variance. Terraform and portfolio dispersion increased.
- Attribution to model identity alone. Reasoning effort changed from `xhigh` to `high`.
- A fully matched causal estimate across all replicates. Six pairs differ in fixture-runner identity and collection date.
- Quality equivalence beyond the frozen functional verifiers.
- A deployment recommendation from three replicates.

## Decision use

The result is strong enough to justify treating Sol/`high` as a lower-token replication candidate for persistent coding workflows. It is not strong enough to conclude that the condition stabilizes run-to-run consumption.

A confirmatory follow-up should freeze one runner commit and image, block or randomize collection time, compare Luna and Sol at the same reasoning effort, and use more than three replicates. A small factorial design separating model from effort would distinguish a Sol effect from the `xhigh`→`high` effort reduction.

## Claim-evidence audit

| Claim | Evidence | Disposition |
|---|---|---|
| Nine Sol/`high` sessions completed validly | Session registry, compact bundles, manifests, matrix receipts | Supported |
| Sol/`high` used fewer tokens in every observed cell | 9 sequence/replicate ratios | Supported descriptively |
| Sol/`high` reduced total token volume by about 37% | Pooled total -37.47%; portfolio paired geometric mean -38.19% | Supported for this panel |
| Sol/`high` reduced variance | Mixed sequence and portfolio CV/log-SD results | Not supported |
| Sol is independently responsible | Model and effort changed together; runner/date mismatch | Not supported |
| Functional correctness was preserved | 27/27 task verifiers and 9/9 final verifiers per condition | Supported on frozen suites only |

## Reproducibility map

- Machine-readable analysis: [`../../sources/evaluations/audits/gpt-5-6-sol-high-baseline-variance-20260718.json`](../../sources/evaluations/audits/gpt-5-6-sol-high-baseline-variance-20260718.json)
- Analysis script: [`../../scripts/analyze_model_condition_baselines.py`](../../scripts/analyze_model_condition_baselines.py)
- Session registry: [`../../data/workflow-sessions.json`](../../data/workflow-sessions.json)
- Runtime/model registry: [`../../data/evaluation-agent-runtimes.json`](../../data/evaluation-agent-runtimes.json)
- Frozen protocols: [`../../sources/evaluations/protocols/`](../../sources/evaluations/protocols/)
- Compact session evidence: [`../../sources/evaluations/workflow-sessions/`](../../sources/evaluations/workflow-sessions/)

Reproduce the analysis with:

```bash
python3 scripts/analyze_model_condition_baselines.py
python3 scripts/validate_repository.py
```

## Conclusion

Sol/`high` completed all nine requested persistent baseline sessions with valid accounting and functional verification. It used markedly fewer provider tokens than the retained Luna/`xhigh` panel, with a portfolio-level descriptive reduction around 38%. The experiment does not support the original variance-reduction hypothesis: dispersion improved on two workflows but worsened on Terraform and in the aggregate. The correct takeaway is **lower observed token volume with mixed variance**, subject to the compound-condition and runner-version limitations above.
