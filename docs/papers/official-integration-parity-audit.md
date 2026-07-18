# Official integration parity audit

**Date:** 2026-07-18

**Scope:** every historical lifecycle-v0 individual-tool profile, plus the Phase 3 TokenJuice+jcodemunch stack

**Machine-readable audit:** [`sources/evaluations/audits/official-integration-parity-20260718.json`](../../sources/evaluations/audits/official-integration-parity-20260718.json)

**Deletion receipts:** [`invalid-treatment-result-deletions-20260718.json`](../../sources/evaluations/audits/invalid-treatment-result-deletions-20260718.json) and [`unproven-treatment-result-deletions-20260718.json`](../../sources/evaluations/audits/unproven-treatment-result-deletions-20260718.json)

**Corrected-contract qualification:** [`corrected-integration-qualification-20260718.json`](../../sources/evaluations/audits/corrected-integration-qualification-20260718.json)

## Decision

The historical screening results were over-accepted. Only 12 of 54 treatment sessions retain objective eligibility, and those support four narrowly stated conditions rather than a broad portfolio ranking. The other 42 treatment sessions were corrupted as tool-effect evidence: 24 used configurations that failed official integration parity and 18 lacked positive operational proof that their MCP treatment was assigned.

At the experiment owner's direction, the 42 corrupted session records, comparisons, compact bundles, and occupied frozen protocols were deleted from the active corpus. They were **not** relabelled as baseline. The deletion receipts retain identities, root causes, deleted paths, and the recovery commit without retaining the corrupted outcomes as active results.

The audit used two independent gates:

1. **Official integration parity:** the profile must materialize the normal Codex integration documented by the exact pinned product source—hooks, wrappers, MCP launcher, warm state, product-authored instructions, and freshness behavior as applicable.
2. **Operational assignment proof:** an MCP treatment must retain a successful `initialize` plus `tools/list` receipt or a completed model-issued MCP call. A configured `[mcp_servers.*]` table, `codex mcp list`, or server count is not proof of a working stdio connection.

## Historical disposition

| Profile | Historical sessions | Disposition | Reason |
|---|---:|---|---|
| `headroom-default-codex` | 3 | Retained eligible product treatment | Codex ran through the pinned `headroom wrap codex` wrapper. |
| `terminal-headroom` | 3 | Retained eligible proxy-only ablation | The wrapper ran with the declared context/MCP/token-save surfaces disabled. |
| `behavior-caveman` | 3 | Retained narrower instruction policy | The exact pinned Caveman instructions were injected each task. |
| `artifact-ponytail` | 3 | Retained narrower instruction policy | The pinned full-mode fallback instructions were injected each task. |
| `terminal-tokenjuice` | 3 | Deleted invalid configuration | The official Codex hook was omitted and hooks were disabled. |
| `terminal-rtk` | 3 | Deleted invalid configuration | `rtk init --global --codex` and its AGENTS/RTK instruction files were absent. |
| `terminal-snip` | 3 | Deleted invalid configuration | Neither the pinned Codex hook nor prompt integration was installed. |
| `retrieval-jcodemunch-mcp` | 3 | Deleted invalid configuration | It used an on-demand launcher, lacked a handshake, and blurred neutral MCP availability with product guidance. |
| `stack-tokenjuice-jcodemunch-mcp` | 3 | Deleted invalid configuration | Both component assignments were defective. |
| `retrieval-leanctx` | 3 | Deleted invalid configuration | The official hybrid initializer, rules, and shell integration were omitted. |
| `retrieval-codegraph` | 3 | Deleted invalid configuration | Official install/instructions and live watch were omitted. |
| `retrieval-graphify` | 3 | Deleted invalid configuration | The Codex skill, AGENTS rules, hook, multi-agent feature, and full graph were omitted. |
| `retrieval-cartog` | 3 | Deleted unproven assignment | Index/serve setup existed but no operational MCP proof survived. |
| `codescope-owner` | 3 | Deleted partial and unproven assignment | A custom adapter stripped mandatory product instructions and retained no handshake. |
| `swarmvault-owner` | 3 | Deleted partial and unproven assignment | Product agent rules were omitted and no handshake survived. |
| `retrieval-serena` | 3 | Deleted bounded and unproven assignment | Onboarding/memories were disabled and no MCP operation was proven. |
| `retrieval-sigmap` | 3 | Deleted manual and unproven assignment | The pinned installer defect was bypassed, but freshness and handshake proof were absent. |
| `integrated-token-savior` | 3 | Deleted bounded and unproven assignment | The MCP shape matched, but no handshake or completed MCP call proved operation. |

The active registry therefore contains 18 provider-backed records: six bare-Codex controls and the 12 retained treatments above. It contains no invalid/excluded treatment records.

## Versioned corrected contracts

Every deleted historical individual condition now has a versioned replacement. The stack has no replacement because its components must first produce valid individual evidence.

| Corrected profile | Corrected treatment contract |
|---|---|
| `terminal-tokenjuice-codex-hook-v1` | Official `tokenjuice install codex`, enabled hooks, doctor, generated hook proof. |
| `retrieval-jcodemunch-mcp-direct-v1` | Direct pinned MCP binary, warm index, neutral availability policy, mandatory handshake. |
| `terminal-rtk-codex-instructions-v1` | Official global Codex initializer and generated `AGENTS.md`/`RTK.md`. |
| `terminal-snip-codex-hook-v1` | Pinned source-default Codex hook in lane-private home with hook audit. |
| `retrieval-graphify-codex-skill-v1` | Full graph, Codex skill, project AGENTS policy, hook, and multi-agent feature. |
| `retrieval-codegraph-codex-mcp-v1` | Official Codex installer, initialized full graph, product instructions, live watch, handshake. |
| `integrated-leanctx-codex-hybrid-v1` | Official Codex hybrid initializer, instructions, shell layer, warm index, handshake. |
| `retrieval-cartog-mcp-v1` | Pinned index/serve path with mandatory handshake. |
| `codescope-codex-product-v1` | Official server start and `init --agent codex`, product initialize instructions, handshake. |
| `swarmvault-codex-product-v1` | Compiled vault plus official Codex rules/hook with generated-artifact proof. |
| `retrieval-serena-codex-mcp-v1` | Official `serena setup codex` and Codex context with mandatory handshake. |
| `retrieval-sigmap-codex-live-v1` | Compatibility-safe manual TOML for the pinned installer defect, AGENTS policy, live watcher, handshake. |
| `integrated-token-savior-mcp-v1` | Bounded official Codex MCP arm with explicit client identity and handshake. |

Each replacement has three fixture-specific frozen protocols, for 39 corrected protocols total. All 39 passed provider-free fixture preparation, host-integration, warm-state, and applicable MCP initialize plus tools/list gates. Product-authored guidance is included only when normal pinned setup installs it. Evaluator-authored tool steering remains forbidden.

## Consequences for prior findings

- The Phase 2 aggregate tool ranking is withdrawn. Its historical report remains for provenance, but its deleted outcomes are not active evidence.
- The Phase 3 TokenJuice+jcodemunch stack decision is withdrawn; no active stack result remains.
- No corrupted treatment was converted into a control observation.
- Bare-Codex baselines remain eligible and reusable for future versioned corrected runs under compatible lifecycle-v0 contracts.
- No corrected provider-backed treatment has run. All 39 corrected protocols passed provider-free setup/handshake qualification, which does not estimate product effect.

## Limits

This audit determines whether the intended treatment was installed and positively assigned. It does not estimate corrected product effects. Any provider-backed corrected sample requires explicit authorization and the first-valid-run policy. Another stack may be preregistered only after both corrected component profiles have valid individual evidence.
