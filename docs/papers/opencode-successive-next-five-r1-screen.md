# Successive OpenCode r1 screen: jCodemunch, LeanCTX, SigMap, Caveman, and LowFat

## Abstract

This single-replicate screen evaluated five additional token-optimization products in OpenCode 1.18.9 with GPT-5.6 Sol at `high` reasoning effort. Each treatment ran the same persistent Fastify, Beets, and Terraform lifecycle-v0 workflows against one accepted fresh bare-OpenCode control per workflow. Provider-reported tokens were the primary outcome; task and final verifiers were degradation diagnostics.

None of the five treatments reduced aggregate weighted usage relative to fresh bare OpenCode. Caveman was closest at **+1.10% weighted**, followed by SigMap at **+13.26%**, LowFat at **+18.99%**, LeanCTX at **+62.83%**, and jCodemunch at **+111.91%**. LeanCTX was the only treatment whose product tools were selected by the model, with seven calls, but it also retained two task-verifier failures and one final-verifier failure in Fastify.

## Design

The screen used:

- OpenCode 1.18.9;
- OpenAI GPT-5.6 Sol with `high` reasoning effort;
- replicate 1;
- one persistent session for each treatment × workflow assignment;
- Fastify, Beets, and Terraform lifecycle-v0 sequences;
- provider-only model network access, with web tools, subagents, and undeclared integrations disabled;
- exact source, binary, adapter, plugin, guidance, protocol, and installation identities;
- provider-free setup, parity, native-activation, isolation, and verifier gates before paid execution;
- the weighted formula `fresh input + 0.1 × cached input + 6 × output`, with reasoning treated as a subset of output rather than added again.

jCodemunch and SigMap were explicit host-agnostic MCP arms. LeanCTX used its OpenCode initializer, active guidance, and MCP server. Caveman and LowFat used official native OpenCode plugins. Ponytail was considered before the freeze but was excluded because both the pinned 4.8.3 snapshot and release 4.8.4 failed to load their native plugin under OpenCode 1.18.9; LowFat was the next eligible product.

## Results

The shared fresh bare-OpenCode control retained **122,994 raw provider tokens** and **66,744.2 weighted units** across the three workflows.

| Treatment | Raw provider tokens | Raw delta | Weighted tokens | Weighted delta | Task verifiers | Final verifiers | Model-issued product calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Caveman | 129,483 | +5.28% | 67,478.6 | +1.10% | 9/9 | 3/3 | 0 |
| SigMap | 155,421 | +26.36% | 75,596.2 | +13.26% | 9/9 | 3/3 | 0 |
| LowFat | 124,145 | +0.94% | 79,419.4 | +18.99% | 9/9 | 3/3 | 0 |
| LeanCTX | 240,487 | +95.53% | 108,682.0 | +62.83% | 7/9 | 2/3 | 7 |
| jCodemunch | 449,030 | +265.08% | 141,439.2 | +111.91% | 9/9 | 3/3 | 0 |

The 15 treatment sessions retained **1,098,566 raw provider tokens** and **472,615.4 weighted units**. They produced 43/45 passing task-verifier outcomes and 14/15 passing final-verifier outcomes.

LeanCTX issued three `lean-ctx_ctx_shell` calls and four `lean-ctx_ctx_call` calls. The model issued only ordinary bash calls in the other four treatments. For Caveman and LowFat, zero model-issued product calls does not imply failed activation because their native plugins operate automatically at command or prompt hooks; retained installation and runtime-preflight receipts prove that the assigned plugin loaded. jCodemunch and SigMap exposed their MCP tools but received zero natural uptake in these prescribed workflows.

## Integrity and limitations

All 15 compact manifests passed. The final cumulative `turn.completed` usage event in every persistent session reconciled exactly to the retained registry totals, and each cumulative series was monotonic. The screen retains 15 matched baseline/treatment comparison records and 840 treatment evidence members.

This is a single-run screening result, not a population estimate or stable ranking. The tasks were deliberately bounded and mechanical, which limits opportunities for retrieval products to help. Provider tokens remain the primary outcome. LeanCTX's verifier failures are reported as degradation rather than used to erase its measured provider usage. Automatic-plugin activation and natural product uptake are distinct: activation was required, while zero uptake remained a valid observed result.

## Evidence

- Machine-readable results: `sources/evaluations/audits/opencode-next-five-batch2-results-20260730.json`
- Selection audit: `sources/evaluations/audits/opencode-successive-native-tool-selection-20260730-batch2.json`
- Qualification and retry receipts: `sources/evaluations/audits/opencode-next-five-batch2-qualification-and-retry-receipts-20260730.json`
- Accepted registry: `data/workflow-sessions.json`
- Compact bundles and matched comparisons: `sources/evaluations/workflow-sessions/`
