# Research roadmap

## Current state

The repository is in Phase 3 stack token-evidence collection. Fastify, Beets, and Terraform each have two retained operationally valid baselines. Sixteen natural-use `r1` individual-tool screens—Caveman, RTK, Serena, Ponytail, Token Savior, Graphify, CodeGraph, jcodemunch MCP, SigMap, LeanCTX, Snip, TokenJuice, default Headroom, Cartog, CodeScope, and SwarmVault—are complete across all three lanes. Headroom also has a compatible proxy-only component ablation. The first stack profile, `stack-tokenjuice-jcodemunch-mcp`, is frozen for the unchanged lifecycle-v0 lanes; it assigns terminal-output ownership to TokenJuice and retrieval-context ownership to jcodemunch MCP. Verifier and review results remain diagnostic rather than eligibility gates.

## Production entry evidence

1. Every start patch independently applies to its pinned snapshot.
2. Feature and review starts fail behavioral acceptance for the intended reason.
3. Refactor starts pass behavior acceptance and fail the disclosed structural gate.
4. All three start patches compose without conflicts.
5. Fixed snapshots pass every verifier.
6. Qualification evidence and frozen v0 execution contracts match registry fingerprints.
7. Repository validation and contract tests pass.

## Next production step

Run only the new `stack-tokenjuice-jcodemunch-mcp` `r1` profile across the three existing lifecycle-v0 lanes. Reuse the retained compatible baseline, TokenJuice, and jcodemunch MCP samples; do not rerun those profiles. Report the stack against baseline, against each component, against the better component, and with the descriptive interaction contrast `stack - TokenJuice - jcodemunch + baseline`. Preserve the first valid stack samples and report verifier diagnostics separately without forced invocation or outcome-selected reruns.
