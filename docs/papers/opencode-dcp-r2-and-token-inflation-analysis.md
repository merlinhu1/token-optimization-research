# OpenCode DCP r2 screen and Serena/jCodemunch token-inflation analysis

**Evaluation date:** 2026-07-30 to 2026-07-31
**Runtime:** OpenCode 1.18.9
**Model condition:** `opencode-openai-gpt-5-6-sol-high` (`gpt-5.6-sol`, reasoning effort `high`)
**Accounting:** provider tokens; weighted units = fresh input + 0.1 × cached input + 6 × output. Reasoning is an output subset and is not counted again.

## Summary

Dynamic Context Pruning (DCP) 3.1.14 loaded natively in all three OpenCode lanes and passed every quality and isolation gate. It did not reduce usage in this short-workflow screen:

- bare OpenCode r2: **123,172 raw tokens**, **71,796.0 weighted units**;
- DCP r2: **149,347 raw tokens**, **73,968.6 weighted units**;
- DCP delta: **+26,175 raw tokens (+21.25%)**, **+2,172.6 weighted units (+3.03%)**.

The model made no `compress` call, and no automatic pruning event was visible in retained evidence. All nine DCP task patches were byte-identical to their matched bare OpenCode patches. The screen therefore measured native plugin overhead under no natural compression uptake, not the value of DCP on long, repetitive conversations.

The Serena and jCodemunch outliers were also input-context effects, not longer answers:

- Serena exposed 22 MCP tools, made one `initial_instructions` call per lane, returned about 7.5k characters of instructions each time, and added one model step per workflow.
- jCodemunch exposed 89 MCP tools plus 6,156 characters of installed guidance. The model never called a jCodemunch tool; the observed fixed input increase is consistent with repeatedly processing the product-added catalog, guidance, and initialization context without retrieval value.

## Protocol

The screen used the established Fastify, Beets, and Terraform three-task lifecycle workflows. Execution was sequential with `--max-parallel 1`. Each DCP lane used the same sequence, fixture tree, OpenCode runtime, model, reasoning effort, replicate index, and controller verifier contract as its matched r2 bare OpenCode lane. Task-02 and task-03 rendered prompt hashes matched in all lanes; task-01 differed because the neutral treatment/isolation header differed, yielding 6/9 prompt-hash matches overall.

DCP was frozen as:

- repository: `Opencode-DCP/opencode-dynamic-context-pruning`;
- tag: `v3.1.14`;
- commit: `85b6f5ceba144fee9e65eb28dc36cab1b960e418`;
- package: `@tarquinen/opencode-dcp@3.1.14`;
- installed entrypoint SHA-256: `1e70b38527d6c604d9437bb447a67c857cd6f0cfe02f4fa69b69729e2ef57432`.

Source tests and build verification passed before evaluation. Provider-free OpenCode probes then confirmed native package loading under OpenCode 1.18.9 in all three workflows.

The r2 bare control is a new provider-backed replicate. Fastify retained the existing replacement-runtime comparison metadata; Beets and Terraform were retained as explicitly authorized standalone OpenCode controls. This metadata distinction does not change the OpenCode runtime, prompts, provider accounting, task tree, or DCP comparison contract.

## Fresh bare OpenCode r2

| Workflow | Fresh input | Cached input | Output | Raw | Weighted | Task verifiers | Final verifier |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fastify | 11,559 | 30,208 | 1,199 | 42,966 | 21,773.8 | 3/3 | pass |
| Beets | 16,289 | 22,528 | 913 | 39,730 | 24,019.8 | 3/3 | pass |
| Terraform | 17,996 | 21,504 | 976 | 40,476 | 26,002.4 | 3/3 | pass |
| **Total** | **45,844** | **74,240** | **3,088** | **123,172** | **71,796.0** | **9/9** | **3/3** |

Raw usage was stable across the three retained bare replicates: r2 was 0.14% above r1 and 0.66% above r0. Weighted r2 usage was 7.57% above r1 because more input landed in the expensive fresh-input bucket.

## DCP results

| Workflow | Bare raw | DCP raw | Raw Δ | Bare weighted | DCP weighted | Weighted Δ |
|---|---:|---:|---:|---:|---:|---:|
| Fastify | 42,966 | 51,612 | +20.12% | 21,773.8 | 31,912.2 | +46.56% |
| Beets | 39,730 | 48,852 | +22.96% | 24,019.8 | 22,176.8 | −7.67% |
| Terraform | 40,476 | 48,883 | +20.77% | 26,002.4 | 19,879.6 | −23.55% |
| **Total** | **123,172** | **149,347** | **+21.25%** | **71,796.0** | **73,968.6** | **+3.03%** |

Aggregate component changes were:

- fresh input: **−1,045**;
- cached input: **+27,136**;
- output: **+84**;
- raw total: **+26,175**.

The per-workflow weighted signs are not consistent because cache placement changed substantially. Raw usage increased by roughly 20–23% in every workflow, making the aggregate conclusion clearer than any individual weighted lane.

## DCP activation and quality

- Native plugin assignment: **3/3 loaded** as `@tarquinen/opencode-dcp@3.1.14`.
- Source artifact identities: **12/12 passed**.
- Post-install artifact identities: **9/9 passed**.
- Isolation audits: **3/3 passed**, zero violations.
- Task verifiers: **9/9 passed**.
- Final verifiers: **3/3 passed**.
- Model-visible DCP calls: **0**.
- Native bash calls: **9**, exactly one per task.
- Exact task-patch parity against bare r2: **9/9 byte-identical**.

The official installer generated and hash-matched the expected configuration. The evaluated adapter disabled project-config discovery and re-injected the exact pinned plugin through `OPENCODE_CONFIG_CONTENT`; this proves semantically equivalent frozen OpenCode wiring, not direct paid-process consumption of the generated installer config.

These workflows used six model steps per session, had no failed tool call, and made unique shell calls. That leaves little material for DCP's default deduplication and error-purge strategies, while the 50,000-token compression nudge threshold was not reached. The result is best described as a native zero-explicit-uptake screen: DCP loaded, no `compress` call occurred, and automatic hook activity was unobserved rather than proven absent.

## Why Serena used more tokens

| Aggregate | Fresh input | Cached input | Output | Raw | Weighted |
|---|---:|---:|---:|---:|---:|
| Matched bare r0 | 32,851 | 86,528 | 2,989 | 122,368 | 59,437.8 |
| Serena | 53,799 | 205,824 | 4,011 | 263,634 | 98,447.4 |
| Delta | +20,948 | +119,296 | +1,022 | +141,266 | +39,009.6 |

Serena's raw increase was **84.45% cached input**, **14.83% fresh input**, and **0.72% output**.

Retained runtime evidence explains the pattern:

1. Serena exposed **22 MCP tools** to OpenCode.
2. Each workflow made one `serena_initial_instructions` call, returning **7,553**, **7,545**, and **7,549** characters.
3. Each Serena session therefore had **seven provider steps**, versus six for bare OpenCode.
4. First-step input rose to roughly **9.7k tokens**, versus **5.3–5.6k** in the matched controls; subsequent cache reads were also substantially larger.
5. After loading Serena's instructions, the model still used ordinary bash for the code work. The three product calls did not produce symbolic retrieval uptake.

The fixed MCP catalog, the large instruction payload, and the extra turn account for the inflation. Output increased only modestly.

## Why jCodemunch used more tokens

| Aggregate | Fresh input | Cached input | Output | Raw | Weighted |
|---|---:|---:|---:|---:|---:|
| Matched bare r1 | 39,995 | 79,872 | 3,127 | 122,994 | 66,744.2 |
| jCodemunch | 87,032 | 358,912 | 3,086 | 449,030 | 141,439.2 |
| Delta | +47,037 | +279,040 | −41 | +326,036 | +74,695.0 |

jCodemunch's raw increase was effectively all input context: **85.59% cached input** and **14.43% fresh input**, while output was 41 tokens lower than bare.

Retained evidence shows:

1. jCodemunch exposed **89 MCP tools**.
2. Its native guide-faithful integration installed **6,156 characters** of product guidance.
3. The model made **zero jCodemunch calls**; each session still had the same six provider steps and three bash calls as bare OpenCode.
4. First-step input was about **23.6k tokens**, versus **5.3–5.6k** for bare OpenCode.
5. Subsequent cache reads stayed around **23–25k tokens**. Positive cache reads in bare were about **4.6–7.7k**, with one later Fastify bare step recording a cache miss.

This is a clean fixed-context-overhead result. The 89-tool catalog, installed guidance, and MCP initialization context are the most likely constituents, while natural behavior did not invoke `plan_turn` or any retrieval tool. Because raw provider request payloads were not retained, the exact schema-versus-guidance allocation is not separately identifiable.

## Interpretation and limitations

- DCP, Serena, and jCodemunch results are single-replicate screening observations, not population estimates or stable rankings.
- DCP's absence of natural activation on short workflows does not test long-session compression effectiveness.
- Weighted accounting is sensitive to cache placement. Raw provider tokens are the clearer DCP result because every lane increased by a similar percentage.
- Serena and jCodemunch attribution is observational but strongly localized: input context explains nearly all raw inflation, and retained step traces identify the catalog, guidance, instruction payload, and additional-turn mechanisms.
- All treatment quality outcomes are diagnostic. No pass/fail result was selected using token usage.

## Evidence

- `sources/evaluations/audits/opencode-dcp-qualification-and-r2-authorization-20260730.json`
- `sources/evaluations/audits/opencode-bare-sol-high-r2-results-20260730.json`
- `sources/evaluations/audits/opencode-dcp-r2-results-20260731.json`
- `sources/evaluations/audits/opencode-serena-jcodemunch-token-inflation-analysis-20260730.json`
- `sources/evaluations/workflow-sessions/dcp-opencode-v1-*-20260731-p-*-r2/`
- `sources/evaluations/workflow-sessions/opencode-*-20260730-p-*-r2/`
