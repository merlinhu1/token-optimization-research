---
status: active
truth_kind: engineering-behavior
last_reviewed: 2026-07-22
---

# Current Findings

## Purpose

Record the repository's current decision-bearing evaluation state without overstating qualification or baseline evidence.

## Scope

This document covers the active lifecycle-v0 portfolio, retained production baseline evidence, accepted corrected treatment sessions, and explicit treatment deletions. Token claims require retained provider-backed sessions; setup qualification alone is not effectiveness evidence.

## Current Implementation Behavior

- The runnable portfolio contains exactly three lifecycle-v0 sequences—Fastify, Beets, and Terraform—under the active low-complexity Baseline V3 task generation.
- Every sequence contains feature implementation, behavior-preserving refactor, and code review/correction in that order.
- Each lane uses a composite preseeded start, sequential prompt disclosure, persistent agent/tool state, complete model-visible focused acceptance, and final-only cumulative verification that repeats only disclosed behavior.
- Codex 0.144.0 emits cumulative `ThreadTokenUsage.total` snapshots in every resumed `turn.completed.usage` event. The legacy extractor summed those snapshots, so the original 30 retained persistent sessions carry inflated legacy totals in their immutable compact summaries and registry records. The source-backed correction audit supplies authoritative final-per-thread totals for those records; later sessions were recorded with corrected accounting at ingestion.
- Fastify contributes three retained Luna/`xhigh` active-default baseline token samples after correction: 6,420,074 tokens at `r0`, 6,712,770 at `r1`, and 4,617,123 at `r2`. All passed 3/3 verifier tasks; review fields remain diagnostic.
- Invalid fixture records and stale protocols were removed at the experiment owner's explicit direction.
- Beets contributes three corrected retained Luna/`xhigh` samples: 12,244,729 tokens at `r0`, 8,728,732 at `r1`, and 9,238,446 at `r2`. All passed 3/3 verifier tasks; full-suite and review findings remain diagnostic.
- The historical assisted-v1 Terraform review verifier exercised policy-summary pagination; that renderer task is not active in Baseline V3.
- Terraform contributes three corrected retained Luna/`xhigh` samples: 15,863,828 tokens at `r0`, 19,453,066 at `r1`, and 17,578,177 at `r2`. All passed 3/3 verifier tasks; no source review is required for token eligibility.
- The nine corrected Luna/`xhigh` active-default baseline samples contain 100,856,945 provider tokens in total. The `r2` matrix contributed 31,433,746 tokens.
- A separate GPT-5.6 Sol/`high` model-comparison panel contributes nine valid baseline sessions and 68,275,315 corrected provider tokens. Every session passed 3/3 tasks and final verification with zero operational retries; all compact-artifact manifests passed. A recursive diagnostics audit nevertheless found raw stderr/non-object lines in retained Codex event JSONL streams, so checksum integrity must not be read as strict nested parseability.
- Sol/`high` used 32.30% fewer pooled corrected provider tokens than the retained Luna/`xhigh` panel, and every sequence/replicate cell was lower. This is a descriptive compound-condition contrast, not a model-only causal estimate: effort changed from `xhigh` to `high`, and six of nine pairs froze a different fixture-runner hash.
- The corrected Sol variance result is mixed: Fastify CV decreased from 19.18% to 6.86% and Beets from 18.87% to 14.98%, while Terraform increased from 10.18% to 21.70% and the three-lane portfolio increased from 5.66% to 16.29%. Terraform Sol/`high` r0 is a valid 15,526,000-token high-trajectory sample; its legacy 31,471,786 value was cumulative-snapshot double counting.
- The assisted-v1 Sol/`high` baseline remains immutable evidence for its exact contract: Fastify retained 941,885 tokens, Beets 1,244,325, and Terraform 5,532,259, for 7,718,469 total provider tokens. All nine task verifiers passed, but post-run trajectory/source audit found corrected implementation mistakes and one surviving Terraform empty-set rendering regression that the narrowed verifier omitted. The family is rejected for future treatment comparison because its difficulty adds nuisance variance.
- Baseline V3 is the active low-complexity design. Its nine tasks each supply one exact mechanical edit command over one or two production files, expose complete focused acceptance to the model, bind Beets to its locked project environment, and export Terraform's pinned Go toolchain path. All literal prompt commands and focused verifiers pass provider-free. V3 has distinct qualification, protocol, and unoccupied pilot-audit identities and has made no provider call. The failed Baseline V2 attempt remains immutable: it spent 808,169 tokens, published nothing, and left the registry unchanged at 90 sessions. Treatment execution remains blocked.
- The official-integration parity audit covers the historical treatment surfaces. At the experiment owner's direction, corrupted sessions and their active comparisons, compact bundles, and occupied protocols were deleted under receipt rather than relabelled as baseline. After the six incomplete Cartog direct-MCP sessions were also deleted, the active registry contains 90 accepted records: 24 controls and 66 eligible individual-tool treatments.
- Two three-lane historical conditions retain objective eligibility: default Headroom as the pinned Codex wrapper treatment and the Headroom proxy-only ablation.
- Default Headroom used 38,075,992 corrected tokens (+9.12%) with 8/9 verifier tasks; its proxy-only ablation used 36,062,796 (+3.35%) with 8/9 verifier tasks. The ablation is not a separate full-product ranking entry.
- TokenJuice, RTK, snip, Graphify, CodeGraph v1, Lean Context, Ponytail prompt-only, and Caveman prompt-emulated lanes were invalid historical product treatments because the runner omitted required Codex hook/rules/skill/index/hybrid surfaces or otherwise materially changed the product setup.
- The historical jcodemunch arm was invalid because it used an on-demand launcher, retained no successful MCP handshake, and did not identify whether it represented neutral MCP availability or the separate product-guidance layer.
- The earliest Cartog, CodeScope, SwarmVault, Serena, SigMap, and Token Savior assignments were operationally unproven and deleted under the same no-baseline-relabel policy. Cartog's first versioned direct-MCP successor was also deleted on 2026-07-20 because it omitted the product-authored Codex `AGENTS.md` routing snippet, official `cartog ide --client codex --yes` install path, model-runtime CLI, and `serve --watch` surface.
- The historical TokenJuice+jcodemunch stack was deleted because both component assignments were defective or unverified; its prior “does not advance” decision is withdrawn. Valid individual evidence now exists for both intended successors, but no corrected stack contract exists without separate preregistration and a new stack identity.
- The invalid CodeGraph result was deleted on 2026-07-19 because the official installer generated a bare `codegraph` command that the model container could not resolve; all three attempted `codegraph explore` commands exited 127. The corrected canonical-v1 generation is bound to new frozen protocol hashes and retained 31,680,860 provider tokens with 9/9 task verifiers. Its derived audit proves MCP initialization and 23 successful model-issued `codegraph explore` commands across all nine tasks. jcodemunch direct v1 was separately deleted because omitting the product-authored Codex guidance layer made that installation incomplete; guide-faithful `retrieval-jcodemunch-codex-mcp-v2` retained 31,552,424 tokens with 8/9 verifier tasks.
- Ponytail and Caveman's six historical results were deleted on 2026-07-19 because they measured evaluator-injected prompt emulations rather than the authors' documented Codex products. Their clean successors are `artifact-ponytail-codex-plugin-v1` (official Codex plugin plus reviewed trusted lifecycle hooks) and `behavior-caveman-codex-skill-v1` (native skill installation plus documented `/caveman` session activation). Their first valid provider samples retained 26,087,938 and 39,731,333 tokens respectively, each with 9/9 task verifiers.
- Corrected provider-backed sessions are retained for TokenJuice (24,429,098 tokens), RTK (30,835,034), Snip (32,129,378), and Graphify (51,520,635). Each profile passed 9/9 task verifiers. Deleted invalid results are not incorporated into product-effect claims.
- The corrected eligible 10-profile Luna/`xhigh` r2 campaign retained 338,007,248 provider tokens against a corrected 10-assignment baseline total of 314,337,460, a descriptive 7.53% increase. The campaign passed 89/90 task verifiers; the only quality diagnostic was jcodemunch Fastify feature task's `FastifyRequest.mediaType` type mismatch. Quality remains diagnostic and did not trigger pass selection or provider reruns.
- Across all 16 eligible individual-tool conditions, the corrected first natural-use screen retained 551,060,181 treatment tokens against 509,861,580 repeated matched-baseline tokens, a descriptive 8.08% increase, with 141/144 task verifiers. Four conditions were lower in aggregate; only TokenJuice (-22.28%) and SigMap (-9.60%) were lower on every evaluated lane. These are one-sample screening observations, not stable rankings.
- A prospective r3 natural-use replication retains three fresh bare-Codex baselines and 18 eligible treatment sessions across TokenJuice, SigMap, Ponytail, RTK, CodeGraph, and jcodemunch-mcp v2. The six profiles used 216,039,299 provider tokens against 202,598,376 repeated matched-baseline tokens (+6.63%) with 53/54 treatment verifiers. jcodemunch-mcp v2 (-9.93%) and Ponytail (-1.29%) were below baseline; the other four profiles ranged from +0.32% to +29.29%.
- Four of six eligible profile-level directions changed between the preceding screen and r3. No stable product ranking is supported.
- Assisted-v1 and Baseline V2 evidence remain historical for their exact hashes. Baseline V3 has distinct prompt, seed, verifier, qualification, baseline-pool, and pilot-audit fingerprints; all three provider-free sequences and all nine literal prompt-command rehearsals pass. No accepted Baseline V2 or V3 session exists.
- Historical qualification receipts remain evidence only for their exact protocol hashes and do not rescue subsequently invalid treatments. The final shared-runner refresh covers all 45 current selectable natural-use lanes across 15 profiles with protocol-hash-bound provider-free preparation, host integration, warm state, concealment, and required MCP handshake gates. All 45 have matching zero-provider qualification receipts.

## Evidence Boundary

Qualification proves fixture mechanics and discriminative diagnostics, not model effectiveness. Product-effect eligibility additionally requires parity with the pinned tool-author installation guide and positive treatment-assignment evidence. Product-authored guidance is part of the treatment whenever the guide recommends it; stripping that layer is an incomplete canonical installation, not evaluator neutrality. For MCP profiles, configuration/listing alone is not a substitute for the complete documented integration or for retained protocol evidence appropriate to that integration. Immutable compact bundles and legacy registry totals remain provenance; current token claims must use the cumulative-usage correction audit. The experiment-owner-authorized treatment repair remains a separate explicit exception, with corrupted active records deleted under machine-readable receipts rather than converted into controls.

A prior Headroom proxy-only attempt was excluded as a controller-audit false positive because the audit interpreted the wrapper's explicit disabled-component startup notices as active tool exposure. The corrected first valid ablation is the only retained sample and no tokens from the excluded attempt are included in comparisons.

A prior artifact-packaging audit found that the now-deleted historical Graphify bundles had included generated `graphify-out` indexes and one deleted CodeScope bundle had included embedding-cache state. That packaging repair remains historical provenance only; the later treatment-deletion receipts supersede those bundle identities in the active corpus.

## Product Truth Links

- None. This is an engineering research evidence surface.

## Maintenance Notes

- Update this document when a treatment, comparison, exclusion, or accepted baseline changes the current evidence state.
- Keep replay provenance and excluded fixture-failure records explicit.
- Never aggregate both an original provider execution and its replay as separate token spend.

## Source References

- ../../../../data/workflow-task-sequences.json
- ../../../../data/repository-fixtures.json
- ../../../../data/workflow-sessions.json
- ../../../../sources/evaluations/audits/official-integration-parity-20260718.json
- ../../../../sources/evaluations/audits/invalid-treatment-result-deletions-20260718.json
- ../../../../sources/evaluations/audits/unproven-treatment-result-deletions-20260718.json
- ../../../../sources/evaluations/audits/corrected-integration-qualification-20260718.json
- ../../../../sources/evaluations/audits/invalid-codegraph-v1-result-deletion-20260719.json
- ../../../../sources/evaluations/audits/corrected-integration-qualification-codegraph-20260719.json
- ../../../../sources/evaluations/audits/codegraph-provider-actual-use-20260720.json
- ../../../../sources/evaluations/audits/corrected-luna-xhigh-r2-campaign-20260720.json
- ../../../../sources/evaluations/audits/phase-2-corrected-analysis-20260720.json
- ../../../../sources/evaluations/audits/luna-xhigh-r3-replication-screen-20260720.json
- ../../../../sources/evaluations/audits/assisted-v1-protocol-qualification-20260720.json
- ../../../../sources/evaluations/audits/assisted-v1-sol-high-baseline-r0-20260720.json
- ../../../../sources/evaluations/audits/baseline-v3-task-family-qualification-20260722.json
- ../../../../sources/evaluations/audits/baseline-v2-pilot-zero-mistake.json
- ../../../../sources/evaluations/audits/invalid-cartog-result-deletions-20260720.json
- ../../../../sources/evaluations/audits/corrected-integration-qualification-cartog-codex-product-v2-20260720.json
- ../../../../sources/evaluations/audits/invalid-jcodemunch-direct-v1-result-deletion-20260719.json
- ../../../../sources/evaluations/audits/corrected-integration-qualification-jcodemunch-codex-mcp-v2-20260719.json
- ../../../../sources/evaluations/audits/codex-cumulative-usage-accounting-20260718.json
- ../../../../sources/evaluations/audits/gpt-5-6-sol-high-baseline-variance-20260718.json
- ../../../../scripts/audit_codex_cumulative_usage.py
- ../../../../sources/evaluations/workflow-sessions/
- ../../../../docs/evaluations/operations/runbook.md
- ../../../../docs/papers/gpt-5-6-sol-high-baseline-variance-screen.md
- ../../../../docs/papers/phase-2-lifecycle-v0-natural-use-screening.md
- ../../../../docs/papers/luna-xhigh-r3-natural-use-replication-screen.md
- ../../../../docs/papers/phase-3-tokenjuice-jcodemunch-stack-screen.md
