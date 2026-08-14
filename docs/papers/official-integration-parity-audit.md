# Official integration parity audit

> **Retired evidence.** This report describes Lifecycle V0 results. V0 was retired on
> 2026-08-14 under [`lifecycle-v0-framework-retired-20260814.json`](../../sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json);
> its sessions, artifacts, and protocols were deleted from the active corpus, so the
> numbers below are no longer reproducible from this repository. The report is retained
> because negative findings and exclusions are part of the research record.

**Date:** 2026-07-18

**Scope:** every historical lifecycle-v0 individual-tool profile, plus the Phase 3 TokenJuice+jcodemunch stack

**Machine-readable audit:** [`sources/evaluations/audits/official-integration-parity-20260718.json`](../../sources/evaluations/audits/official-integration-parity-20260718.json)

**Deletion receipts:** [`invalid-treatment-result-deletions-20260718.json`](../../sources/evaluations/audits/invalid-treatment-result-deletions-20260718.json), [`unproven-treatment-result-deletions-20260718.json`](../../sources/evaluations/audits/unproven-treatment-result-deletions-20260718.json), [`invalid-codegraph-v1-result-deletion-20260719.json`](../../sources/evaluations/audits/invalid-codegraph-v1-result-deletion-20260719.json), [`invalid-jcodemunch-direct-v1-result-deletion-20260719.json`](../../sources/evaluations/audits/invalid-jcodemunch-direct-v1-result-deletion-20260719.json), [`invalid-ponytail-caveman-result-deletion-20260719.json`](../../sources/evaluations/audits/invalid-ponytail-caveman-result-deletion-20260719.json), and [`invalid-cartog-result-deletions-20260720.json`](../../sources/evaluations/audits/invalid-cartog-result-deletions-20260720.json)

**Corrected-contract qualification:** historical [`corrected-integration-qualification-20260718.json`](../../sources/evaluations/audits/corrected-integration-qualification-20260718.json); current shared-runner receipts are linked in the versioned-contract section below, including [`corrected-integration-qualification-jcodemunch-codex-mcp-v2-20260719.json`](../../sources/evaluations/audits/corrected-integration-qualification-jcodemunch-codex-mcp-v2-20260719.json) and [`corrected-integration-qualification-cartog-codex-product-v2-20260720.json`](../../sources/evaluations/audits/corrected-integration-qualification-cartog-codex-product-v2-20260720.json).

## Decision

The historical screening results were over-accepted. After the 2026-07-19 Ponytail and Caveman correction, only 6 of the 54 original treatment sessions retain objective eligibility, supporting two Headroom conditions rather than a broad portfolio ranking. The other 48 original treatment sessions were corrupted as tool-effect evidence: 30 used configurations that failed official integration parity and 18 lacked positive operational proof that their MCP treatment was assigned.

At the experiment owner's direction, the 48 corrupted original session records, comparisons, compact bundles, and occupied frozen protocols were deleted from the active corpus. They were **not** relabelled as baseline. Separate receipts also delete later invalid corrected-profile results. The deletion receipts retain identities, root causes, deleted paths, and the recovery commit without retaining corrupted outcomes as active results.

The audit used two independent gates:

1. **Official integration parity:** the profile must materialize the normal Codex integration documented by the exact pinned product source—hooks, wrappers, MCP launcher, warm state, product-authored instructions, and freshness behavior as applicable.
2. **Operational assignment proof:** an MCP treatment must retain a successful `initialize` plus `tools/list` receipt or a completed model-issued MCP call. A configured `[mcp_servers.*]` table, `codex mcp list`, or server count is not proof of a working stdio connection.

## Historical disposition

| Profile | Historical sessions | Disposition | Reason |
|---|---:|---|---|
| `headroom-default-codex` | 3 | Retained eligible product treatment | Codex ran through the pinned `headroom wrap codex` wrapper. |
| `terminal-headroom` | 3 | Retained eligible proxy-only ablation | The wrapper ran with the declared context/MCP/token-save surfaces disabled. |
| `behavior-caveman` | 3 | Deleted invalid incomplete installation | The runner injected the skill body into evaluator prompts but did not run the native Codex skill installer or documented `/caveman` session activation. |
| `artifact-ponytail` | 3 | Deleted invalid incomplete installation | The runner injected fallback instructions but did not install the official Codex plugin or trust its product lifecycle hooks. |
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

The active registry therefore contains 69 provider-backed records: 18 controls and 51 retained individual-tool treatments. It contains no invalid/excluded treatment records.

## Versioned corrected contracts

The 2026-07-18 audit created versioned replacements for the profiles deleted at that time. Subsequent runtime and installation-guide review invalidated two of those replacements: the original CodeGraph v1 generation and jcodemunch direct v1. By owner direction, corrected CodeGraph reuses the canonical v1 profile ID with new frozen hashes and fresh qualification. jcodemunch direct v1 remains deleted and is superseded by the separately versioned, guide-faithful `retrieval-jcodemunch-codex-mcp-v2` treatment.

| Current or subsequently adjudicated profile | Treatment contract or disposition |
|---|---|
| `terminal-tokenjuice-codex-hook-v1` | Official `tokenjuice install codex`, enabled hooks, doctor, generated hook proof. |
| `retrieval-jcodemunch-mcp-direct-v1` | **Deleted invalid treatment.** It installed the direct MCP binary and warm index but deliberately omitted the tool-author-provided Codex guidance layer. |
| `retrieval-jcodemunch-codex-mcp-v2` | Pinned 1.108.114 pre-installed binary with no MCP arguments, product-native warm index, verbatim product-authored Codex guidance excerpts, and mandatory initialize plus non-empty `tools/list`; retained provider-backed sample. |
| `terminal-rtk-codex-instructions-v1` | Official global Codex initializer and generated `AGENTS.md`/`RTK.md`. |
| `terminal-snip-codex-hook-v1` | Pinned source-default Codex hook in lane-private home with hook audit. |
| `retrieval-graphify-codex-skill-v1` | Full graph, Codex skill, project AGENTS policy, hook, and multi-agent feature. |
| `retrieval-codegraph-codex-mcp-v1` | Official Codex installer, lane-private executable on model PATH, project-local full graph, product instructions, live watch, and handshake. |
| `artifact-ponytail-codex-plugin-v1` | Exact pinned source mirrored into a local marketplace, official `codex plugin` install, and all reviewed plugin lifecycle hooks trusted through Codex app-server. |
| `behavior-caveman-codex-skill-v1` | Author-recommended `npx skills add ... -a codex`, all seven native skills materialized, and documented `/caveman` activation in the first persistent-session prompt. |
| `integrated-leanctx-codex-hybrid-v1` | Official Codex hybrid initializer, instructions, shell layer, warm index, handshake. |
| `retrieval-cartog-mcp-v1` | **Deleted invalid treatment.** Direct MCP registration omitted product-authored Codex routing, the official Codex installer, model-runtime CLI exposure, and live watch. |
| `retrieval-cartog-codex-product-v2` | Pinned official `cartog ide --client codex --yes`, verbatim product `AGENTS.md` routing snippet, lane-private executable, structural index, `serve --watch`, and mandatory handshake. |
| `codescope-codex-product-v1` | Official server start and `init --agent codex`, product initialize instructions, handshake. |
| `swarmvault-codex-product-v1` | Compiled vault plus official Codex rules/hook with generated-artifact proof. |
| `retrieval-serena-codex-mcp-v1` | Official `serena setup codex` and Codex context with mandatory handshake. |
| `retrieval-sigmap-codex-live-v1` | Compatibility-safe manual TOML for the pinned installer defect, AGENTS policy, live watcher, handshake. |
| `integrated-token-savior-mcp-v1` | Bounded official Codex MCP arm with explicit client identity and handshake. |

The original replacement set produced provider-free qualification evidence only for its exact historical hashes; it does not rescue subsequently invalid treatments. The final shared-runner refresh binds all 45 current selectable lanes across 15 profiles to current protocol hashes through the current candidate, CodeGraph, Ponytail/Caveman, jcodemunch v2, Token Savior product-v2, and Cartog product-v2 receipts. All 45 have matching zero-provider qualification evidence. Product-authored guidance is part of normal installation whenever the pinned guide recommends it. Evaluator-authored steering remains forbidden.

### 2026-07-19 CodeGraph correction

The table above is preserved as the 2026-07-18 audit decision. Subsequent retained provider events proved that `retrieval-codegraph-codex-mcp-v1` was not usable from the actual model runtime: the official installer generated a bare `codegraph` command, but v1 did not put that command on the model container PATH, and all three attempted `codegraph explore` commands exited 127. The experiment owner directed deletion of its sessions, comparisons, bundles, and occupied protocols rather than relabelling them.

By owner direction, the corrected candidate reuses the canonical `retrieval-codegraph-codex-mcp-v1` profile ID after the invalid result was deleted. The deletion receipt binds the rejected generation to its three deleted protocol paths; the corrected generation is distinguished by new frozen protocol hashes and fresh provider-free qualification. It uses the same pinned source and official `--target codex` installer but exposes a lane-private `codegraph` command on the model PATH, executes project-local `init`, and requires a container-level `command -v codegraph && codegraph --version` probe plus MCP initialize/tools-list before provider access. The retained corrected sample used 31,680,860 provider tokens, passed 9/9 task verifiers, and produced 23 successful model-issued `codegraph explore` commands across all nine tasks.

### 2026-07-19 jcodemunch installation-guide correction

The direct-v1 lanes correctly installed a pinned binary, registered it in Codex, warmed the repository index, and retained successful `initialize` plus `tools/list` receipts. They nevertheless violated the canonical product-installation contract by deliberately omitting the tool-author-provided Codex guidance layer. The pinned guide explicitly states that wiring makes the tools callable but does not make the agent use them, and directs Codex users to install persistent guidance through project rules or `AGENTS.md`.

The experiment owner classified that omission as a broken and incomplete installation. All three direct-v1 sessions, comparisons, compact bundles, occupied protocols, and external result roots were deleted under [`invalid-jcodemunch-direct-v1-result-deletion-20260719.json`](../../sources/evaluations/audits/invalid-jcodemunch-direct-v1-result-deletion-20260719.json). No totals or task outcomes are preserved in the deletion receipt.

The clean successor is `retrieval-jcodemunch-codex-mcp-v2`. It pins source commit `fbc14e40c7057ebc6d718fb48083d30522afe15f` and wheel 1.108.114, installs that wheel into a lane-private venv, registers the resolved binary directly with no MCP arguments, builds the product-native index, and materializes only verbatim product-authored policy and universal-guide excerpts into lane-private Codex `AGENTS.md`. Its provider-free receipt requires the guidance provenance files, successful warmup, successful initialize, a non-empty 89-tool `tools/list`, and exposure of `jcodemunch_guide` on all three fixtures. The retained provider-backed successor sample used 31,552,424 tokens and passed 8/9 task verifiers; the Fastify feature task failed only its hidden TypeScript `mediaType` diagnostic.

The policy is now explicit: canonical product treatments include every author-recommended integration surface, including product-authored guidance, rules, skills, and hooks. Evaluator-authored steering remains forbidden, but evaluator neutrality may not remove or contradict the product's own instructions. Reduced surfaces are separate named ablations only.

### 2026-07-19 Ponytail and Caveman installation-guide correction

The historical `artifact-ponytail` lane was a prompt-only emulation: it injected fallback policy text while omitting the author's official Codex plugin, commands, skills, and trusted `SessionStart`, `UserPromptSubmit`, and `SubagentStart` hooks. The historical `behavior-caveman` lane similarly rendered skill prose into evaluator prompts without using the author's Codex skill installer or documented `/caveman` session activation. The owner directed deletion of all six results and their dependent artifacts under [`invalid-ponytail-caveman-result-deletion-20260719.json`](../../sources/evaluations/audits/invalid-ponytail-caveman-result-deletion-20260719.json).

The clean successors are `artifact-ponytail-codex-plugin-v1` and `behavior-caveman-codex-skill-v1`. Ponytail is installed through Codex's native marketplace/plugin commands from a source-pinned local mirror, after which every discovered plugin hook is reviewed and trusted at its current hash. Caveman uses the author-recommended `npx skills add ... -a codex` path against the exact pinned checkout and places `/caveman` in the first prompt of each persistent session. Their retained first-valid provider samples used 26,087,938 and 39,731,333 tokens respectively, each with 9/9 task verifiers.

### 2026-07-20 Cartog product-integration correction

The direct-MCP v1 profile initialized successfully and advertised 16 tools, but that transport proof did not establish a canonical Cartog product treatment. The pinned Cartog documentation says to copy its routing snippet into `AGENTS.md` because agents otherwise default to grep, and its official Codex path runs `cartog ide --client codex --yes` to register `serve --watch`. V1 omitted those surfaces and did not expose Cartog's CLI to the model runtime. At owner direction, all six v1 provider sessions, six comparisons, six compact bundles, and nine occupied or stale protocols were deleted under the Cartog receipt without changing any baseline session.

The fresh `retrieval-cartog-codex-product-v2` identity copies the pinned binary into lane-private executable storage, runs the official Codex installer, preserves the product-authored project guidance verbatim, builds the structural index, and requires initialize plus non-empty `tools/list`. All three provider-free fixture lanes passed with 16 tools and zero provider calls. No provider-backed Cartog product-v2 result exists yet.

### 2026-07-20 corrected-campaign closure

After deleting Cartog v1, the 10 eligible corrected Luna/`xhigh` assignments retain 30 sessions and 338,007,248 provider tokens against 314,337,460 corrected tokens across the corresponding baseline assignments, a descriptive 7.53% increase. The earlier 46.53% reduction was an accounting error: the campaign summary copied legacy baseline registry totals that summed cumulative thread snapshots, while treatment totals were already final-snapshot-correct. All eligible sessions remain accepted for the token objective and all compact manifests verify; task diagnostics passed 89/90. The corrected aggregate receipt is [`corrected-luna-xhigh-r2-campaign-20260720.json`](../../sources/evaluations/audits/corrected-luna-xhigh-r2-campaign-20260720.json), the full corrected Phase 2 analysis is [`phase-2-corrected-analysis-20260720.json`](../../sources/evaluations/audits/phase-2-corrected-analysis-20260720.json), and the CodeGraph actual-use proof is [`codegraph-provider-actual-use-20260720.json`](../../sources/evaluations/audits/codegraph-provider-actual-use-20260720.json).

## Future fail-closed prevention

A treatment profile is no longer runnable merely because it exists in the registry or produces a frozen protocol. The repository validator and the direct provider-launch path require all of the following for the complete non-baseline candidate set:

1. explicit membership in the parity audit's `approved_profile_ids` set;
2. exactly one current frozen protocol per active fixture, bound to the profile, runner, validator, product configuration, source identity, and probe hashes;
3. an exact protocol-path and SHA-256 match in a provider-free qualification receipt;
4. successful fixture preparation, concealment, composite seed delivery, product warmup, and host-integration checks; and
5. for every MCP-enabled profile, successful `initialize`, successful `tools/list`, and a non-empty advertised-tool list with no probe errors.

The parity-approved set must exactly equal the fixture registry's non-baseline candidates. Any runner, validator, product configuration, source identity, or probe change makes the prior protocol/receipt binding stale and blocks provider launch until new never-run protocols are generated and the complete provider-free matrix passes again. Configuration visibility, executable presence, `codex mcp list`, and server counts remain explicitly insufficient as assignment proof.

## Consequences for prior findings

- The Phase 2 aggregate tool ranking is withdrawn. Its historical report remains for provenance, but its deleted outcomes are not active evidence.
- The Phase 3 TokenJuice+jcodemunch stack decision is withdrawn; no active stack result remains.
- No corrupted treatment was converted into a control observation.
- Bare-Codex baselines remain eligible and reusable for future versioned corrected runs under compatible lifecycle-v0 contracts.
- Subsequent provider-backed corrected treatments exist for TokenJuice, RTK, Snip, and Graphify. jcodemunch direct v1 and CodeGraph v1 were later deleted as invalid; consult current findings rather than the original 39-lane qualification count.

## Limits

This audit determines whether the intended treatment was installed and positively assigned. Corrected product-effect observations are synthesized in the current Phase 2 report rather than inferred from setup evidence. Any additional provider-backed sample requires explicit authorization and prospective replicate indexing under the first-valid-run policy. Another stack requires separate preregistration and a new stack identity even though valid individual evidence now exists.
