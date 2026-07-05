# Phase 2 report: lifecycle-v0 natural-use screening of token-saving tools for Codex workflows

> **Report status:** production screening report. Results are valid scoped reproduction evidence, not population estimates, a universal tool ranking, or deployment recommendations.

**Report date:** 2026-07-18

**Evidence collection:** 2026-07-16 to 2026-07-17

**Evidence stage:** `reproduction`

**Runtime/model condition:** Codex CLI, OpenAI GPT-5.6 Luna, `xhigh` reasoning

**Primary metric:** cumulative provider-reported tokens per complete persistent workflow session

## Abstract

This report evaluates sixteen token-saving tools or bounded tool profiles, plus one required Headroom component ablation, on three frozen software-engineering lifecycle workflows. Each workflow contains feature implementation, behavior-preserving refactoring, and code review/correction in one persistent Codex session. Treatments were installed through their frozen declared integration surfaces and made available without evaluator-authored instructions to invoke, prefer, or quota them. The comparison therefore estimates assignment to the named treatment configuration, not treatment-on-the-treated behavior or an unevaluated broader product surface.

The evidence contains 57 operationally valid provider runs: six bare-Codex baselines and 51 treatment sessions. Every run has provider-reported token components, three structured final-state verifier outcomes, frozen execution identity, isolation evidence, and a checksum-verified compact artifact bundle. Across 171 task outcomes, 164 passed and seven failed. All 57 tool-isolation and verifier-integrity audits passed, no prohibited external-retrieval event was recorded, and all 171 manifest entries independently matched their recorded SHA-256 hashes.

In the matched `r1` screen, the three-lane bare baseline used 73.893 million provider tokens. Descriptively ordered aggregate treatment changes ranged from TokenJuice at -28.54% to CodeScope at +15.63%. TokenJuice combined the largest aggregate reduction with 9/9 verifier passes, but increased tokens on Beets. jcodemunch MCP and Serena were the only treatments with both 9/9 verifier passes and reductions on all three lanes; their aggregate changes were -17.58% and -3.27%, respectively. Cartog reduced all three lanes by an aggregate -18.62% but passed 8/9 tasks. SigMap and CodeScope increased aggregate tokens by 11.69% and 15.63%. Effects were strongly repository-dependent, and the Terraform lane contributed 58.72% of the matched baseline total.

These are first valid assignment samples—one treatment replicate per repository. Baseline replicate changes ranged from -31.32% to +29.28% by lane, independent quality review exists for only two of 57 sessions, and provider totals were dominated by cached input. The results support a preregistered replication program; they do not support stable effect sizes, a universal winner, or deployment-grade recommendations.

## 1. Research question and claim boundary

The primary question is:

> Under a frozen normal-user treatment configuration, how does cumulative provider-reported token use change relative to a compatible retained bare-Codex baseline on the same persistent lifecycle workflow?

The primary estimand is **availability/natural use**. A treatment can operate through a CLI wrapper, MCP server, warm index, proxy, host integration, or product-authored instruction layer. The evaluator installs and validates that integration but does not add instructions requiring or preferring use. Explicit model-issued command counts are therefore not a universal uptake measure, and zero visible calls do not invalidate a treatment assignment.

The report permits the following claims:

- observed provider-token totals and component values for the frozen sessions;
- observed paired changes against the compatible `r1` baseline;
- structured verifier outcomes for every task;
- integration, isolation, and artifact-integrity facts recorded by the controller;
- descriptive cross-lane consistency and post-screening replication priorities.

It does **not** permit:

- population-average token-saving percentages;
- statistical significance or stable treatment rankings from one treatment replicate;
- cross-model, cross-runtime, or cross-workload generalization;
- attribution of an assignment-level change to one internal mechanism without complete mechanism instrumentation;
- software-quality superiority from verifier outcomes alone;
- monetary-cost or latency claims.

## 2. Relationship to Phase 1

[Phase 1](phase-1-compatibility-safe-token-saving-stacks.md) mapped source-inspected mechanisms and compatibility boundaries. It established hypotheses, not measured winners. Phase 2 narrows that portfolio into isolated atomic treatment screens so each run has one declared surface owner or one explicitly bounded integrated owner.

The treatment set spans four practical mechanism groups:

- **terminal/tool-output owners:** RTK, Snip, and TokenJuice;
- **retrieval/context owners:** Serena, Graphify, CodeGraph, jcodemunch MCP, SigMap, LeanCTX, and Cartog;
- **broad or integrated owners:** Token Savior, default Headroom, CodeScope, and SwarmVault;
- **instruction/policy treatments:** Caveman and Ponytail.

Headroom also has a proxy-only component ablation. It is reported separately and is not counted as a seventeenth full-tool screen.

This report does not evaluate the multi-tool stacks proposed in Phase 1. A positive atomic screen is evidence for replication of that treatment assignment, not validation of a future stack containing it.

## 3. Methods

### 3.1 Workflow unit

One replicate is one complete three-task workflow session—not one task. Each lane starts from one qualified composite repository state, discloses prompts sequentially, preserves repository and agent/tool state, and runs all concealed verifiers after the final prompt.

| Lane | Pinned repository role | Ordered lifecycle tasks |
|---|---|---|
| Fastify | medium JavaScript/TypeScript framework | request media-type feature; Content-Type representation refactor; review/correction of an `onMaxParamLength` status-code change |
| Beets | medium Python application | multivalue modify feature; lazy model-storage refactor; review/correction of an `ftintitle` metadata-hook change |
| Terraform | large Go application | deferred policy-callback feature; state-store provider parsing refactor; review/correction of cloud policy-summary rendering |

The task contracts are defined in `data/workflow-task-sequences.json`; generated qualification evidence lives beside each fixture under `sources/evaluations/fixtures/`.

### 3.2 Baseline and treatment conditions

The baseline is `baseline-bare-codex`: Codex native shell, editing, plain file operations, Git, and verifier commands are allowed; MCP servers, token-saving add-ons, global instructions, hooks, plugins, skills, and warm indexes are disabled.

Every treatment session uses the same model condition, fixture, prompts, verifier bytes, runtime image, isolation policy, and baseline-pool fingerprint as its paired baseline. Treatment-specific configuration is frozen in the profile protocol and recorded in `tool_adapter_identity`.

All 57 sessions used:

- Codex CLI with OpenAI GPT-5.6 Luna and `xhigh` reasoning;
- Docker image `sha256:6f86d01f2c63f5029c6bb874d8f3694c24d5cd567e3d09413eccc956ba3feafe`;
- fresh lane-specific runtime homes and tool state as declared by the profile;
- disabled Codex web search and model-shell network denial;
- final-only controller verification.

Several profiles intentionally bound claims to less than every surface offered by the upstream product:

- Caveman is the instruction-layer behavior-policy arm; MCP-description compression, plugin hooks, and persistent mode state are inactive.
- Token Savior uses its integrated MCP surface with external host hooks and automatic memory injection disabled.
- CodeGraph and LeanCTX are cold optional retrieval conditions; no controller-built index is provided.
- CodeScope retains its official MCP tools and cold auto-indexer but removes upstream mandatory-uptake wording so use remains natural; telemetry export and external embedding providers are inactive.
- SwarmVault uses an offline heuristic warm index with its product-native deterministic 500-file cap; cloud/local model providers, hooks, agent-rule installation, and graph viewer are inactive.
- Default Headroom is the primary wrapper condition. The separately reported `terminal-headroom` profile disables several default Headroom-managed surfaces and is explicitly proxy-only.

Claims in this report apply to these frozen profiles, not to disabled product surfaces.

### 3.3 Treatment validity and use

A treatment is valid when its frozen normal-user integration is present, configured, and isolated. Invocation is not an eligibility gate. Controller preflight is installation evidence, not causal model use. Mechanism claims are made only when the declared integration provides complete relevant instrumentation.

This distinction is material for instruction layers, wrappers, proxies, hooks, and MCP servers. For example, no explicit model-issued CodeScope or SwarmVault MCP call was observed, but their valid availability samples are retained rather than rerun or steered. Their token comparisons remain assignment-level observations.

### 3.4 Token accounting

The primary measure is `workflow_session_total`: cumulative provider-reported usage across all three model turns, including any provider-consuming retry. Every record preserves:

- fresh input tokens;
- cached input tokens;
- output tokens;
- reasoning tokens when exposed;
- total provider tokens;
- accounting source and basis.

For these Codex records:

```text
total_provider_tokens = fresh_input_tokens + cached_input_tokens + output_tokens
```

Reasoning tokens are provider-exposed diagnostic detail and are not added again. Cache-write tokens were not separately exposed. Local indexing, setup time, wall-clock latency, and money are outside the primary metric.

For treatment `T` and matched baseline `B`:

```text
paired_delta = T.total_provider_tokens - B.total_provider_tokens
paired_delta_percent = paired_delta / B.total_provider_tokens × 100
```

All treatment comparisons use the compatible `r1` baseline. The extra `r0` baselines quantify observed baseline variability but are not averaged into the treatment denominator.

### 3.5 Correctness and quality diagnostics

Every task emits its own structured final-state outcome. Missing or duplicate outcomes fail closed. Verifier results and optional independent source review describe model behavior but do not select which operationally valid token samples count.

Independent source-quality review is available for two baseline sessions; 55 sessions remain `not-reviewed`. Consequently, this report can make verifier-correctness claims but does not claim comprehensive merge-quality equivalence across treatments.

### 3.6 Isolation and artifact integrity

The controller records verifier integrity, external-retrieval audit results, runtime and tool identities, treatment configuration, and compact evidence locations. Each session directory contains exactly:

- `run.json`;
- `changes.diff`;
- `evidence.jsonl.gz`;
- `manifest.sha256`.

The decision index is `data/workflow-sessions.json`. Compatible pair summaries are stored under `sources/evaluations/workflow-sessions/*-vs-*.json`.

A packaging audit found that generated Graphify indexes had been included in three cumulative source diffs and a generated CodeScope embedding cache had been included in one. The four bundles were repaired under `source-diff-generated-state-exclusion-v1`. Their `run.json` records preserve the original hashes, sizes, and removed-section counts. Source changes, provider events and usage, verifier output, comparisons, and interpretation were unchanged.

## 4. Evidence inventory and integrity

| Evidence class | Count | Result |
|---|---:|---|
| Bare baseline sessions | 6 | two per lane (`r0`, `r1`) |
| Full-tool treatment sessions | 48 | sixteen treatments × three lanes |
| Headroom proxy-only ablation sessions | 3 | one per lane |
| Total workflow sessions | 57 | all operationally valid and token-accounting eligible |
| Matched treatment comparisons | 51 | 48 full-tool + 3 ablation |
| Structured task outcomes | 171 | 164 pass; 7 fail |
| Tool-isolation audits | 57 | 57 pass |
| Verifier-integrity audits | 57 | 57 pass |
| Records with prohibited external-retrieval hits | 0 | none observed |
| Operational retries | 0 | none recorded |
| Manifest entries checked | 171 | 171 SHA-256 matches |
| Artifact packaging repairs | 4 | generated treatment state removed from source-diff checkpoints; receipts retained |
| Independent source-quality reviews | 2 | 55 sessions not reviewed |

Repository-level checks at finalization passed: the generated workflow runbook was current, repository validation passed, 104 contract tests passed, Truthmark reported no diagnostics, and `git diff --check` passed.

## 5. Baseline behavior

### Table 1. Baseline replicates and matched `r1` components

| Lane | `r0` total | `r1` total | `r1` vs `r0` | `r1` fresh | `r1` cached | `r1` output | `r1` reasoning | Verifier tasks (`r0`; `r1`) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Fastify | 12.950M | 13.078M | +0.98% | 0.471M | 12.510M | 96.9K | 52.5K | 3/3; 3/3 |
| Beets | 25.370M | 17.424M | -31.32% | 0.659M | 16.646M | 119.0K | 58.3K | 3/3; 3/3 |
| Terraform | 33.564M | 43.392M | +29.28% | 0.977M | 42.297M | 117.9K | 54.5K | 3/3; 3/3 |

The aggregate baseline moved from 71.884M at `r0` to 73.893M at `r1` (+2.80%), but that small aggregate difference hides substantial lane-level variation. Every paired treatment uses `r1`, so the comparisons are internally matched; the variation nevertheless demonstrates why one treatment replicate cannot establish a stable effect.

The `r1` portfolio was weighted 17.70% Fastify, 23.58% Beets, and 58.72% Terraform by provider tokens. Aggregate changes are therefore dominated by Terraform. Lane-level results must accompany every aggregate value.

Cached input comprised 71.453M of the 73.893M matched baseline total (96.70%). The primary metric intentionally includes cached provider volume, but this composition means most observed absolute differences are changes in repeated cached context rather than visible model output.

## 6. Treatment results

### Table 2. Descriptive matched screening results

Rows are ordered by aggregate provider-token change. Negative values mean fewer provider-reported tokens than the matched `r1` baseline. “Reduced lanes” is descriptive sign consistency, not a significance test.

| Treatment | Surface / state | Fastify Δ | Beets Δ | Terraform Δ | Treatment total | Aggregate Δ | Verifier tasks | Reduced lanes |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TokenJuice | terminal output; cold CLI | -34.37% | +4.13% | -39.91% | 52.801M | **-28.54%** | 9/9 | 2/3 |
| Snip | terminal output; cold CLI | -39.64% | +10.00% | -24.69% | 59.739M | **-19.16%** | 8/9 | 2/3 |
| Cartog | retrieval; warm index | -53.70% | -16.42% | -8.93% | 60.134M | **-18.62%** | 8/9 | 3/3 |
| jcodemunch MCP | retrieval; warm index | -48.78% | -0.60% | -14.99% | 60.902M | **-17.58%** | 9/9 | 3/3 |
| SwarmVault | broad context; warm index | +29.80% | -11.24% | -33.82% | 61.155M | **-17.24%** | 9/9 | 2/3 |
| CodeGraph | retrieval; cold | -36.08% | +8.30% | -21.66% | 61.223M | **-17.15%** | 9/9 | 2/3 |
| Graphify | retrieval; warm index | -33.42% | -1.08% | -17.39% | 61.788M | **-16.38%** | 8/9 | 3/3 |
| Token Savior | integrated MCP | -42.01% | -1.35% | -12.15% | 62.891M | **-14.89%** | 7/9 | 3/3 |
| Caveman | instruction-layer behavior policy | -49.05% | +11.78% | -13.88% | 63.510M | **-14.05%** | 9/9 | 2/3 |
| RTK | terminal output | -13.18% | +13.11% | -22.95% | 64.494M | **-12.72%** | 9/9 | 2/3 |
| LeanCTX | retrieval; cold | -13.55% | +34.65% | -18.55% | 70.107M | **-5.12%** | 9/9 | 2/3 |
| Serena | retrieval | -2.29% | -6.36% | -2.33% | 71.475M | **-3.27%** | 9/9 | 3/3 |
| Default Headroom | broad compression / wrapper | -17.86% | +48.85% | -19.75% | 71.498M | **-3.24%** | 8/9 | 2/3 |
| Ponytail | artifact-minimization policy | -0.63% | +32.76% | -15.03% | 72.996M | **-1.21%** | 9/9 | 2/3 |
| SigMap | retrieval; warm index | -19.17% | +11.07% | +21.24% | 82.532M | **+11.69%** | 9/9 | 1/3 |
| CodeScope | broad context; cold auto-index | -57.82% | -11.93% | +48.83% | 85.440M | **+15.63%** | 9/9 | 2/3 |
| Headroom proxy-only | component ablation | -24.02% | -5.53% | +18.76% | 77.932M | **+5.47%** | 8/9 | 2/3 |

The Headroom proxy-only row is an ablation and is intentionally excluded from the sixteen-tool descriptive ordering.

### 6.1 Main screening observations

1. **TokenJuice had the largest observed aggregate reduction.** It used 21.092M fewer provider tokens than the matched baseline (-28.54%) and passed 9/9 verifier tasks. Its Beets lane increased 4.13%, so the effect was not uniform.
2. **jcodemunch MCP paired all-lane reductions with 9/9 verifier passes.** Its three lane changes were -48.78%, -0.60%, and -14.99%, for -17.58% aggregate.
3. **Serena was directionally consistent but small.** It reduced every lane and passed 9/9 tasks, but its aggregate change was only -3.27%.
4. **Cartog, Graphify, and Token Savior reduced all three lanes but had verifier failures.** Their aggregate changes were -18.62%, -16.38%, and -14.89%, with 8/9, 8/9, and 7/9 verifier passes. The token samples remain eligible, but correctness differences must remain visible.
5. **Several large aggregate reductions were heterogeneous.** Snip, SwarmVault, CodeGraph, Caveman, and RTK each reduced aggregate tokens by more than 10% while increasing at least one lane.
6. **SigMap and CodeScope increased aggregate tokens.** SigMap used 11.69% more; CodeScope used 15.63% more because its +48.83% Terraform result outweighed medium-lane reductions.
7. **Headroom’s default and proxy-only conditions differed materially.** Default Headroom was -3.24% aggregate; proxy-only was +5.47%. This is one component-ablation sample, not a stable mechanism estimate.

### Table 3. Aggregate provider-token components

| Treatment | Fresh input | Cached input | Output | Reasoning | Total | Δ total |
|---|---:|---:|---:|---:|---:|---:|
| Bare Codex `r1` | 2.107M | 71.453M | 333.7K | 165.2K | 73.893M | — |
| TokenJuice | 1.717M | 50.767M | 317.1K | 156.4K | 52.801M | -28.54% |
| Snip | 1.760M | 57.681M | 296.8K | 146.9K | 59.739M | -19.16% |
| Cartog | 1.669M | 58.179M | 286.0K | 140.7K | 60.134M | -18.62% |
| jcodemunch MCP | 1.888M | 58.713M | 301.1K | 148.8K | 60.902M | -17.58% |
| SwarmVault | 2.107M | 58.755M | 293.0K | 143.5K | 61.155M | -17.24% |
| CodeGraph | 2.075M | 58.797M | 351.5K | 169.1K | 61.223M | -17.15% |
| Graphify | 2.007M | 59.450M | 330.9K | 148.8K | 61.788M | -16.38% |
| Token Savior | 2.020M | 60.570M | 300.5K | 136.0K | 62.891M | -14.89% |
| Caveman | 2.059M | 61.127M | 324.9K | 163.2K | 63.510M | -14.05% |
| RTK | 1.850M | 62.350M | 293.7K | 148.8K | 64.494M | -12.72% |
| LeanCTX | 2.308M | 67.482M | 317.4K | 130.0K | 70.107M | -5.12% |
| Serena | 1.946M | 69.210M | 319.1K | 147.8K | 71.475M | -3.27% |
| Default Headroom | 2.419M | 68.717M | 360.9K | 175.9K | 71.498M | -3.24% |
| Ponytail | 2.213M | 70.458M | 325.4K | 157.3K | 72.996M | -1.21% |
| SigMap | 2.122M | 80.075M | 335.5K | 162.3K | 82.532M | +11.69% |
| CodeScope | 2.228M | 82.889M | 322.9K | 153.5K | 85.440M | +15.63% |

The component table shows that aggregate ordering was driven chiefly by cached input volume. Output-token differences were much smaller than total differences. This is particularly important for Caveman: the evaluated arm is a behavioral-output policy, but its -14.05% aggregate observation cannot be interpreted as a measured output-only mechanism effect because provider total was dominated by cached context.

## 7. Correctness diagnostics

Seven of 171 structured task outcomes failed. Every failure occurred on the first, feature-implementation task; later refactor and review tasks passed their individual concealed verifiers on the final cumulative tree.

| Condition | Lane | Failed task | Treatment tasks passed |
|---|---|---|---:|
| Token Savior | Fastify | `fastify-lifecycle-feature-v0` | 2/3 |
| Token Savior | Beets | `beets-lifecycle-feature-v0` | 2/3 |
| Graphify | Fastify | `fastify-lifecycle-feature-v0` | 2/3 |
| Snip | Fastify | `fastify-lifecycle-feature-v0` | 2/3 |
| Default Headroom | Fastify | `fastify-lifecycle-feature-v0` | 2/3 |
| Cartog | Fastify | `fastify-lifecycle-feature-v0` | 2/3 |
| Headroom proxy-only | Fastify | `fastify-lifecycle-feature-v0` | 2/3 |

No causal claim is made that these tools caused the failures. With one treatment sample, each outcome combines treatment assignment and ordinary model stochasticity. The failures remain part of the evidence and are not removed to improve token results.

All six baseline runs passed 3/3 tasks. Among the full-tool treatments, 138 of 144 task outcomes passed. The Headroom ablation passed 8/9.

## 8. Interpretation by mechanism class

### 8.1 Terminal-output tools

TokenJuice, Snip, and RTK all reduced the weighted aggregate, but each increased Beets. The class therefore shows a promising aggregate signal with no uniform cross-repository effect. TokenJuice combines the largest observed aggregate reduction with complete verifier success and is a strong replication candidate. Snip’s larger reduction than RTK came with one Fastify failure. No operation-level compression percentage is substituted for the workflow totals.

### 8.2 Retrieval and context tools

Retrieval results ranged from jcodemunch MCP at -17.58% to SigMap at +11.69%. Tool category alone did not predict the sign. jcodemunch and Serena reduced all three lanes with 9/9 verifier passes; Cartog and Graphify reduced all three but each failed the Fastify feature task. CodeGraph had a substantial aggregate reduction and complete verifier success but increased Beets. LeanCTX’s -5.12% aggregate concealed a +34.65% Beets increase.

Warm-index profiles received their declared controller-side state preparation before model execution. The report measures provider tokens, not local indexing compute or latency. A warm-index treatment can therefore be token-efficient in this estimand while still carrying operational setup costs outside the measured boundary.

### 8.3 Broad and integrated owners

Token Savior reduced aggregate tokens by 14.89% but passed only 7/9 tasks. SwarmVault reduced aggregate tokens by 17.24% with 9/9 verifier passes, while varying from +29.80% on Fastify to -33.82% on Terraform. CodeScope produced the largest single-lane reduction (-57.82% on Fastify) and the largest full-tool aggregate increase (+15.63%) because Terraform rose 48.83%. Broad ownership did not create a stable direction in this first screen.

Default Headroom’s -3.24% result and proxy-only +5.47% ablation suggest that the frozen default-wrapper condition should not be represented by its proxy component alone. Replication is required before attributing the difference to a particular Headroom surface.

### 8.4 Instruction and policy treatments

Caveman reduced aggregate tokens by 14.05% with 9/9 verifier passes, but increased Beets by 11.78%. Ponytail was nearly neutral in aggregate (-1.21%) while ranging from +32.76% on Beets to -15.03% on Terraform. These conditions can alter model trajectory without explicit tool calls; their evidence remains assignment-level.

## 9. Threats to validity

### 9.1 Single treatment replicate

Each treatment has one complete workflow replicate per lane. There is no within-lane treatment variance estimate, confidence interval, or significance test. Descriptive ordering is not a population ranking.

### 9.2 Baseline variability

Bare-Codex `r0` to `r1` changes were +0.98% on Fastify, -31.32% on Beets, and +29.28% on Terraform. Compatible pairing controls protocol identity, but one baseline observation remains a noisy counterfactual for one treatment observation.

### 9.3 Aggregate weighting

Terraform contributed 58.72% of the matched baseline total. Large Terraform shifts can dominate reductions on both medium lanes, as CodeScope demonstrates. Every aggregate result must be read with its three lane values.

### 9.4 Cache-heavy accounting

Cached input represented 96.70% of the matched baseline. Provider total is the preregistered primary metric, but the mechanism behind a total change may be cache and trajectory behavior rather than direct output compression.

### 9.5 Limited workload population

The portfolio contains three open-source repositories, one lifecycle shape, one runtime, one model, and one reasoning setting. It does not represent all languages, agents, repository sizes, or task types.

### 9.6 Incomplete independent quality review

Only two sessions have independent source-quality reviews. Structured verifier outcomes exist for all sessions, but the report cannot establish equivalent maintainability, design quality, or merge readiness across 57 final trees.

### 9.7 Assignment versus mechanism use

The natural-use estimand is intentional, but it limits mechanism attribution. Some treatments act through wrappers, proxies, instruction layers, or generated context. Absence of a model-issued tool string does not prove inactivity; presence does not prove that observed token changes came from that call.

### 9.8 Setup boundary

Provider tokens include model-visible workflow execution but exclude local indexing compute, setup time, and latency. Results favor the declared token objective and should not be restated as total-resource efficiency.

### 9.9 No monetary inference

No price conversion is made. Provider-token change is not equivalent to financial savings when cache pricing, subscriptions, or provider policies differ.

## 10. Decision use and replication priorities

The current evidence supports **replication priorities**, not product recommendations.

### 10.1 High-information replication candidates

- **TokenJuice:** largest aggregate reduction, 9/9 verifier tasks, but one lane increased.
- **jcodemunch MCP:** reductions on all lanes and 9/9 verifier tasks.
- **Cartog:** reductions on all lanes and a large aggregate change, with one verifier failure requiring diagnostic attention.
- **CodeGraph and SwarmVault:** substantial aggregate reductions with 9/9 verifier tasks but mixed lane signs.
- **Snip:** large aggregate reduction with one verifier failure and a Beets increase.

These priorities are post-screening decisions. Any next replicate must be preregistered and compatible; it must not be selected or discarded based on whether a rerun reproduces the preferred sign.

### 10.2 Consistency and boundary controls

- **Serena** is useful as a low-magnitude, all-lane reduction reference.
- **SigMap and CodeScope** are important negative observations. Replication can determine whether their aggregate increases persist or were single-sample variation.
- **Default versus proxy-only Headroom** should remain an explicit component comparison rather than being collapsed into one result.

### 10.3 Required next-step rules

1. Preserve every first valid sample.
2. Preregister additional replicate indices before execution.
3. Reuse the same causal comparison identity; mint a new pool only for model-visible or causal contract changes.
4. Continue natural-use assignment without evaluator-authored uptake pressure.
5. Report every compatible replicate, including failures and sign reversals.
6. Add independent source review for finalists and material verifier failures if making software-quality or deployment claims.
7. Keep lane-level and token-component results alongside aggregates.
8. Add another model/runtime condition before claiming broad agent generality.

## 11. Claim-evidence audit

| Claim | Type | Evidence path | Status | Boundary |
|---|---|---|---|---|
| TokenJuice had the largest observed aggregate reduction in this screen | reproduction | matched comparison JSONs; session registry | supported | descriptive ordering of one `r1` sample per lane |
| jcodemunch and Serena reduced all three lanes with 9/9 verifier passes | reproduction | session records and structured outcomes | supported | no population or quality-superiority claim |
| Cartog reduced all three lanes | reproduction | three Cartog comparisons | supported | one Fastify verifier failure remains visible |
| SigMap and CodeScope increased aggregate provider tokens | reproduction | matched comparison JSONs | supported | one replicate; not stable harm estimates |
| Removing generated Graphify/CodeScope state from source-diff checkpoints did not alter treatment results | artifact integrity | repair receipts, corrected manifests, unchanged registry result fields | supported | artifact-packaging repair only |
| Normal-user tool availability caused the observed token deltas through one known mechanism | mechanism/causal | incomplete mechanism instrumentation | needs evidence | report only assignment-level comparisons |
| The descriptive ordering is a stable ranking | recommendation | no replication distribution | remove | preregister compatible replicates first |
| Any treatment is deployment-ready | recommendation | limited workloads and quality review | remove | requires broader replication and quality evidence |
| Provider-token reduction implies money or latency reduction | recommendation | outside measured boundary | remove | no monetary or latency conversion |

## 12. Reproducibility and evidence map

Primary machine-readable authorities:

- `data/workflow-task-sequences.json` — active lifecycle-v0 task contracts;
- `data/evaluation-profiles.json` — treatment definitions and normal-use integration policies;
- `data/workflow-sessions.json` — compact run index, token components, structured outcomes, and artifact paths;
- `sources/evaluations/protocols/` — immutable baseline and treatment execution contracts;
- `sources/evaluations/workflow-sessions/<session-id>/` — compact four-file run bundles;
- `sources/evaluations/workflow-sessions/*-vs-*.json` — matched comparison records;
- `docs/evaluations/design/token-and-quality-policy.md` — accounting and eligibility rules;
- `docs/evaluations/design/framework.md` — estimand and interpretation contract;
- `docs/evaluations/operations/runbook.md` — generated operational index.

Repository validation commands:

```bash
python3 scripts/update_workflow_runbook.py --check
python3 scripts/validate_repository.py
python3 scripts/test_workflow_evaluation_contract.py
truthmark check --json
truthmark index --json
git diff --check
```

## 13. Conclusion

The lifecycle-v0 screen establishes a credible production evidence base for scoped token research: 57 valid provider runs, 51 matched comparisons, complete provider accounting, 171 structured task outcomes, clean isolation, and checksum-verified artifacts. It also shows why operation-level claims and single aggregate percentages are insufficient. Tool effects varied sharply by repository; cached context dominated the accounting boundary; seven task failures remained visible; and baseline lane variability was large.

TokenJuice produced the largest observed aggregate reduction with complete verifier success, while jcodemunch MCP uniquely combined a substantial aggregate reduction with reductions on all three lanes and 9/9 verifier passes. Serena also reduced every lane with 9/9 passes, but by a much smaller aggregate amount. Cartog, Snip, SwarmVault, CodeGraph, Graphify, Token Savior, Caveman, and RTK produced screening signals worth further study under different correctness or consistency profiles. SigMap and CodeScope are important negative observations rather than inconvenient records to discard.

The scientifically defensible next step is preregistered compatible replication of a narrowed set, preserving every sample and keeping assignment, mechanism activity, correctness, and provider-token accounting separate. Until that evidence accumulates, this report should be read as a production-grade screening report—not a universal ranking or deployment recommendation.
