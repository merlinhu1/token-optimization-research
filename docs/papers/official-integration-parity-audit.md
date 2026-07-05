# Official integration parity audit

**Date:** 2026-07-18

**Scope:** every retained lifecycle-v0 individual-tool profile, plus the Phase 3 TokenJuice+jcodemunch stack

**Machine-readable audit:** [`sources/evaluations/audits/official-integration-parity-20260718.json`](../../sources/evaluations/audits/official-integration-parity-20260718.json)

**Corrected-contract qualification:** [`sources/evaluations/audits/corrected-integration-qualification-20260718.json`](../../sources/evaluations/audits/corrected-integration-qualification-20260718.json)

## Decision

The historical screening results were over-accepted. Only 12 of 54 treatment sessions retain objective eligibility, and those support four narrowly stated conditions rather than a broad portfolio ranking. Forty-two treatment sessions remain valid provider-execution and token-accounting records but are excluded from product-effect, ranking, aggregate, and recommendation claims: 24 because their configurations failed official integration parity, and 18 because plausible bounded/manual MCP assignments lacked positive operational proof.

The audit used two independent gates:

1. **Official integration parity:** the historical profile had to materialize the normal Codex integration documented by the exact pinned product source—hooks, wrappers, MCP launcher, warm state, or product-authored instructions as applicable.
2. **Operational assignment proof:** an MCP treatment needed positive `initialize` plus `tools/list` evidence or a completed model-issued MCP call. A configured `[mcp_servers.*]` table, `codex mcp list`, and a server count in `codex doctor` show configuration, not a successful stdio handshake.

Provider execution and measured token totals are not deleted. Ineligible records are retained as forensic partial-intervention evidence with `accepted_for_execution: true` and `accepted_for_objective: false`.

## Disposition

| Profile | Historical sessions | Disposition | Reason |
|---|---:|---|---|
| `headroom-default-codex` | 3 | Eligible product treatment | Codex actually ran through the pinned `headroom wrap codex` wrapper. |
| `terminal-headroom` | 3 | Eligible proxy-only ablation | The pinned wrapper ran with the declared context/MCP/token-save surfaces disabled. It is not a full-product estimate. |
| `behavior-caveman` | 3 | Eligible narrower instruction policy | The exact pinned Caveman skill instructions were injected every task. This estimates always-on behavioral brevity, not installer lifecycle effects. |
| `artifact-ponytail` | 3 | Eligible narrower instruction policy | The pinned full-mode fallback instructions were injected every task. This estimates the always-on code-minimization policy, not the complete plugin UX. |
| `terminal-tokenjuice` | 3 | Invalid configuration | The official `tokenjuice install codex` hook was omitted; the runner also wrote `hooks = false` and passed `--disable hooks`. |
| `terminal-rtk` | 3 | Invalid configuration | Official Codex setup requires `rtk init --codex`/`--global --codex`, which writes `AGENTS.md` and `RTK.md`. The historical profile only exposed the binary on `PATH`. |
| `terminal-snip` | 3 | Invalid configuration | Pinned source defaults to an experimental Codex hook via `snip init --agent codex`; its safer `--mode prompt` fallback writes project `AGENTS.md`. The historical profile installed neither and explicitly disabled hooks. |
| `retrieval-jcodemunch-mcp` | 3 | Invalid configuration | It used an on-demand uv launcher instead of the pinned direct-binary Codex path, retained no handshake, and did not distinguish neutral MCP availability from the separate product-guidance layer. |
| `stack-tokenjuice-jcodemunch-mcp` | 3 | Invalid configuration | Both component assignments were defective, so the stack-effect interpretation is invalid. |
| `retrieval-leanctx` | 3 | Invalid configuration | The official hybrid `lean-ctx init --agent codex` treatment includes MCP, rules/guidance, and shell hooks; the historical condition exposed only a cold raw MCP entry and retained no handshake. |
| `retrieval-codegraph` | 3 | Invalid configuration | The historical condition skipped `codegraph init`, disabled watch, installed no Codex AGENTS block, and retained no handshake proving initialize guidance. |
| `retrieval-cartog` | 3 | Unverified assignment | Index and serve configuration existed; operational MCP connection was not positively proven. |
| `codescope-owner` | 3 | Unverified partial assignment | The custom adapter deliberately stripped mandatory uptake text, and no handshake/call proves the neutral server path worked. It is not a full-product condition. |
| `swarmvault-owner` | 3 | Unverified partial assignment | Init/ingest/compile/MCP were configured, but product agent rules were omitted and no handshake/call was retained. |
| `retrieval-serena` | 3 | Unverified bounded assignment | Core MCP/context/project setup matched, but onboarding and memories were disabled; no handshake/call proved the bounded server operational. |
| `retrieval-graphify` | 3 | Invalid configuration | The historical optional MCP-only condition used a reduced graph and omitted the official Codex skill, AGENTS rules, hook, and multi-agent setup; no handshake was retained. |
| `retrieval-sigmap` | 3 | Unverified manual-equivalent assignment | Manual TOML correctly bypassed a pinned upstream installer defect and generated warm Codex AGENTS state, but omitted freshness hooks and retained no handshake. |
| `integrated-token-savior` | 3 | Unverified bounded assignment | The optimized/thin historical setup materially matched the official bounded MCP-only arm, but no handshake or completed MCP call proved operation. |

## Corrected protocols

### TokenJuice

`terminal-tokenjuice-codex-hook-v1` now:

1. runs `tokenjuice install codex` against the lane-private `CODEX_HOME`;
2. requires the generated `hooks.json`;
3. enables Codex hooks and omits `--disable hooks`;
4. runs `tokenjuice doctor codex`;
5. retains host-integration evidence.

### jcodemunch MCP

`retrieval-jcodemunch-mcp-direct-v1` now:

1. installs the exact pinned wheel into a lane-private virtual environment;
2. configures Codex with the direct `jcodemunch-mcp` binary, with no on-demand launcher in the stdio path;
3. warms the repository index using that direct binary;
4. requires a provider-free `initialize` → `notifications/initialized` → `tools/list` probe;
5. supplies no evaluator-authored or product-guided routing instructions.

This corrected profile is explicitly a **neutral MCP-availability treatment**. The pinned product documentation treats MCP wiring and persistent usage guidance as separate layers and does not provide a first-class Codex guidance installer. A product-guided Codex condition therefore requires a separate versioned instruction-policy profile; it must not be silently folded into this technical-assignment correction.

A final no-provider Fastify smoke against the exact frozen corrected descriptors passed host integration, Codex preflight, warmup, and repository validation for both profiles. The jcodemunch handshake advertised 89 tools. Beets and Terraform corrected descriptors were generated and repository-validated but were not provider-executed.

## Consequences for prior findings

- The Phase 2 aggregate tool ranking is withdrawn. Its per-profile measured deltas remain in retained comparison files, but only 12 of its 48 treatment sessions remain objective-eligible.
- The Phase 3 TokenJuice+jcodemunch stack decision is withdrawn. The three stack records are forensic partial-intervention data, not a valid stack screen.
- No historical session was rerun or overwritten.
- Bare Codex baselines remain eligible and reusable when a corrected versioned profile is eventually run under an otherwise compatible lifecycle-v0 contract.
- RTK, snip, Graphify, CodeGraph, and Lean Context require new versioned setup-corrected profiles before provider spend. Cartog, CodeScope, SwarmVault, Serena, SigmaP, and Token Savior require versioned handshake-gated profiles, preserving each bounded/manual estimand. They were audited and invalidated here, not silently changed in place.

## Limits

This audit determines whether the intended treatment was installed and positively assigned. It does not estimate corrected product effects. The corrected TokenJuice and jcodemunch protocols are control-plane artifacts only until new first-valid-sample provider sessions are explicitly authorized and completed.
