# Lowfat three-lane evaluation

Date: 2026-07-13

## Result

Lowfat did not improve the primary provider-token objective in any evaluated lane. It increased provider tokens with equal disclosed-task correctness in Fastify, Terraform, and Beets. Fastify is hard-lane evidence only because independent final-tree review rejected both conditions at quality 3/5; Terraform and Beets are objective-accepted at quality 4/5.

| Lane | Baseline session | Lowfat session | Verified tasks | Quality (B/T) | Baseline tokens | Lowfat tokens | Delta | Primary disposition |
|---|---|---|---:|---:|---:|---:|---:|---|
| Fastify | `baseline-fastify-20260713-p-6a8afd4b63ca-r0` | `lowfat-fastify-20260713-p-6a8afd4b63ca-r0` | 5/5 vs 5/5 | 3/3 | 60,671,087 | 76,395,931 | +15,724,844 (+25.92%) | Quality-rejected hard-lane evidence; no ranking claim |
| Terraform | `baseline-terraform-20260713-p-5b17c90c9943-r0` | `lowfat-terraform-20260713-p-5b17c90c9943-r0` | 3/3 vs 3/3 | 4/4 | 18,004,662 | 21,150,707 | +3,146,045 (+17.47%) | Accepted; Lowfat worse |
| Beets | `baseline-beets-20260713-p-7aaac4b8a309-r0` | `lowfat-beets-20260713-p-7aaac4b8a309-r0` | 3/3 vs 3/3 | 4/4 | 6,400,224 | 9,104,141 | +2,703,917 (+42.25%) | Accepted; Lowfat worse |

Across the two objective-accepted lanes, baseline usage is 24,404,886 provider tokens and Lowfat usage is 30,254,848: **+5,849,962 (+23.97%)**. Including Fastify hard-lane evidence, the three-lane totals are 85,075,973 versus 106,650,779: **+21,574,806 (+25.36%)**.

## Causal exposure

The initial optional-exposure Terraform and Beets attempts invoked Lowfat zero times and were excluded. The active treatment protocol uses preferred guidance and requires model-initiated use.

- Fastify: 139/139 audited completed shell commands used Lowfat; 406 syntactic command-position prefixes; at least 139 confirmed executions.
- Terraform: 34 Lowfat-bearing shell events and 115 individual Lowfat invocations.
- Beets: 51 unique Lowfat-bearing command events (47 successful, 4 nonzero), 134 syntactic prefixes, and at least 128 confirmed reached invocations. Controller preflight and router-rejected pre-start attempts are excluded. `provider-usage.json` incorrectly reports zero observed tool calls despite the raw command events; this is a telemetry-classification defect, not a causal-use failure.

These runs therefore establish genuine tool exposure, not merely tool availability.

## Correctness and quality

- Terraform and Beets pass their complete corrected concealed verifier suites and independent source review at quality 4/5.
- Beets explicitly restores and verifies required `MediaAttributes.popularity`.
- Fastify passes all five disclosed behavioral/type surfaces, but both bare and Lowfat final trees leave `kLogController` undefined. Controller state is consequently stored through the collision-prone public string key `"undefined"`. Both score 3/5 and are excluded from objective acceptance.

## Secondary cache-adjusted view

Fresh-input-plus-output tokens changed by -5.07% on Fastify, -11.88% on Terraform, and +28.83% on Beets. Across the two accepted lanes the secondary total worsened by 3.96%. Provider-reported total tokens remain the primary metric, so secondary reductions do not reverse the result.

## Interpretation

This is single-run screening evidence with no uncertainty estimate and is not sufficient for cross-tool ranking. Under the correctness-aware policy, Lowfat is not better in any lane: it never uses fewer primary provider tokens at no-worse accepted quality, and Fastify additionally fails the independent quality threshold.
