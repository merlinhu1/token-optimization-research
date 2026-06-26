# Phase 1 Report: Qualified Out-of-Box Token-Saving Stacks for AI Coding Agents

**Date:** 2026-06-25  
**Repository:** `token-optimization-research`  
**Scope:** Conservative token-saving stacks for AI coding agents where the stack works out of the box, not by manual tool choreography.

## Executive summary

This report has been reworked from scratch around Merlin's stricter criterion:

> A stack only belongs here if its parts are already packaged or wired together out of the box. No custom glue, no careful routing policy, no “use tool A for X and tool B for Y” workflow discipline, and no loose collection of unrelated CLI primitives.

That removes the earlier hand-built stacks such as `RTK + CodeGraph + Ponytail + Caveman` and `ripgrep + ast-grep + qmd`. Those can be useful ingredients, but they do not satisfy the out-of-box stack criterion by themselves.

The qualified stacks below are therefore **deployable integrated stacks**: either one tool that internally combines several token-saving mechanisms, or one installer/gateway that wires a fixed set of tools together.

## Selection rules

A stack is included only if it passes all of these gates:

| Gate | Requirement |
|---|---|
| Out-of-box integration | One install/config path wires the stack; no manual composition required. |
| No conflicting owners | The stack itself decides routing/ownership, or the bundled tools target clearly separated waste sources. |
| Positive token-saving contribution | Every named component contributes to token reduction or context reduction in the stack's documented design. |
| Conservative quality posture | The stack avoids blind truncation as its core value proposition, or keeps raw/source access available. |
| Reputation signal | Preference for GitHub stars, benchmark artifacts, published docs, and/or included high-reputation components. |
| No redundant add-ons | Do not add another retrieval engine, output compressor, memory system, or router on top unless the stack vendor explicitly supports it. |

## Qualified stack 1 — Token Savior MCP Stack

**Best for:** Claude Code or any MCP-compatible coding agent where code navigation, memory, and command-output compaction should be one integrated server.

**Deployable stack:**

```text
Token Savior MCP profile
```

**Tool set inside the stack:**

| Internal component | Token-saving role |
|---|---|
| Structural code navigation | Avoids broad file reads by exposing symbol/code-navigation tools. |
| Persistent memory | Reduces repeated rediscovery across turns/sessions. |
| Bash output compaction | Compacts common Git/test/build/package-manager outputs. |
| Compact MCP profile/manifests | Reduces tool-description/context overhead. |

**Why it satisfies the criteria:**

- It is one MCP server/profile rather than a manually assembled set of separate tools.
- The components are designed to work together in one token-saving surface.
- It explicitly combines retrieval, memory, and shell-output reduction without asking the user to pick routing rules.
- It publishes a task benchmark rather than only per-command examples.

**Reputation/evidence:**

- GitHub: `Mibayy/token-savior`, ~1,015 stars at retrieval time.
- README reports Claude Opus 4.7 on 96 coding tasks: active tokens/task `17,221 → 3,395` (-80%) and score `141/180 → 188/192`.
- Repo record notes the result is maintainer-run and profile-dependent, but it is still stronger stack-level evidence than most discovered tools.

**Do not combine with:** RTK, CodeGraph, LeanCTX, Caveman memory/output stacks, or other broad MCP code-retrieval/memory layers. Those duplicate surfaces already owned by Token Savior.

## Qualified stack 2 — Tokless Managed Multi-Tool Stack

**Best for:** users who specifically want a prewired multi-tool stack for Claude Code, OpenCode, Codex, or Antigravity with minimal setup.

**Deployable stack:**

```text
tokless
```

**Tool set wired by the stack:**

| Bundled tool | Token-saving role |
|---|---|
| RTK | Trims noisy Bash/tool output. |
| Caveman | Reduces verbose agent prose/output. |
| CodeGraph | Reduces whole-file reads through code-graph queries. |
| Context-Mode | Runs heavy work in a sandbox and returns only selected results. |

**Why it satisfies the criteria:**

- Tokless is explicitly an installer/lifecycle manager for this stack, not an ad hoc recommendation to install four tools manually.
- It supports `tokless`, `tokless update`, `tokless doctor`, and `tokless uninstall`.
- It wires agents according to their own config specs and supports `--agents claude,opencode,codex,antigravity`.
- Its README states the bundled tools target different waste sources and are intended to be non-overlapping.

**Reputation/evidence:**

- GitHub: `HoangP8/tokless`, ~65 stars at retrieval time.
- Component reputation is high: Caveman ~76k stars, RTK ~66k, CodeGraph ~54k, Context-Mode ~18k.
- Evidence is mainly component-level, but Tokless is the clearest discovered example of a real out-of-box multi-tool stack.

**Conservative use rule:** use Tokless as a whole stack and do not add extra compression/retrieval/memory tools on top. If one bundled tool harms a workload, switch to another qualified stack instead of manually rebalancing Tokless into a custom stack.

## Qualified stack 3 — LeanCTX Integrated Context Stack

**Best for:** local-first users who want one binary to own code reads, shell compaction, memory, budgets, and savings accounting across agents.

**Deployable stack:**

```text
LeanCTX
```

**Tool set inside the stack:**

| Internal component | Token-saving role |
|---|---|
| Cached and AST-aware file reads | Reduces repeated file/context reads. |
| Shell-output compression | Compacts noisy terminal output. |
| Persistent memory | Avoids repeated rediscovery. |
| Code graph / routing | Selects narrower context views. |
| Budgets and savings ledger | Keeps token use visible and auditable. |
| Optional proxy | Compresses request/context surfaces when enabled. |

**Why it satisfies the criteria:**

- It is one local Rust context-intelligence layer, not a hand-built combination.
- Its features are internally coordinated by the same product.
- It exposes budget/savings accounting, which makes hidden negative contribution easier to detect.
- It is local-first, reducing privacy and operational risk compared with remote compression gateways.

**Reputation/evidence:**

- GitHub: `yvgude/lean-ctx`, ~2,935 stars at retrieval time.
- README claims 60–90% fewer tokens for reads and shell output and cached rereads near 13 tokens.
- Existing external pilot evidence in this repo is mixed for end-to-end provider-billed totals, so LeanCTX belongs here as an integrated stack, but it should be used as the stack owner rather than layered with RTK/CodeGraph/extra memory systems.

**Do not combine with:** RTK, CodeGraph, Token Savior, Tokless, separate memory systems, or broad prompt compressors. LeanCTX already spans those surfaces.

## Qualified stack 4 — Headroom Compression Stack

**Best for:** teams whose dominant cost is large tool outputs, logs, files, RAG chunks, or conversation/history blobs and who want one compression layer with library/proxy/MCP deployment modes.

**Deployable stack:**

```text
Headroom
```

**Tool set inside the stack:**

| Internal component | Token-saving role |
|---|---|
| Specialized compressors | Route JSON, code, prose, logs, files, and history to suitable compression methods. |
| Library / proxy / MCP modes | Lets the same compression stack sit in different agent integration points. |
| Original-content cache / reversible path | Keeps raw content retrievable when compressed output is insufficient. |

**Why it satisfies the criteria:**

- It is one compression product with coordinated algorithms and deployment modes.
- It does not require combining independent compressors.
- It targets context before it reaches the model and is designed around preserving answer quality rather than blind truncation.
- It has the strongest GitHub reputation signal among discovered compression-layer tools.

**Reputation/evidence:**

- GitHub: `chopratejas/headroom` / `headroomlabs-ai/headroom`, ~51k stars at retrieval time.
- README claims 60–95% fewer tokens; repo data records maintainer benchmarks reporting 47–92% savings on several workloads.
- Existing repo notes an external N=1 pilot where request-level compression did not translate into lower provider-billed totals due to extra turns. That means Headroom should own the compression layer alone; do not stack it with other compressors.

**Do not combine with:** RTK, TokenTamer, Kompact, LeanCTX proxy compression, Tokless, or another broad context compressor.

## Qualified stack 5 — Context-Mode Offload Stack

**Best for:** workflows dominated by huge intermediate artifacts: long logs, many API/tool calls, large search results, multi-step MCP workflows, or exploratory analysis where only a selected final result should enter context.

**Deployable stack:**

```text
Context-Mode
```

**Tool set inside the stack:**

| Internal component | Token-saving role |
|---|---|
| MCP/tool offload layer | Runs multi-step tool workflows outside the main model context. |
| Sandbox execution | Keeps intermediate artifacts out of the chat context. |
| Result selection | Returns only selected outputs instead of every intermediate payload. |
| Hooks/routing enforcement | Applies the offload model across supported agent platforms. |

**Why it satisfies the criteria:**

- It is one offload stack, not a manual pairing with RTK or a retrieval engine.
- It directly attacks the large-intermediate-output problem that command compactors only partially address.
- It should be deployed alone for this surface; adding another output compactor creates routing conflict.

**Reputation/evidence:**

- GitHub: `mksglu/context-mode`, ~18k stars at retrieval time.
- README and repo data record worked examples such as 150k-to-2k or 700KB-to-3KB style reductions.
- It has Hacker News/community attention and claims multi-platform support through MCP/hooks.

**Do not combine with:** RTK, Headroom, pctx, or other offload/output-compression tools unless the combination is explicitly supported and smoke-tested by the stack itself.

## Qualified stack 6 — Caveman Code Replacement-Agent Stack

**Best for:** users willing to replace Codex/Claude-style terminal agent runtime with a token-lean agent rather than adding token-saving middleware to an existing agent.

**Deployable stack:**

```text
Caveman Code
```

**Tool set inside the stack:**

| Internal component | Token-saving role |
|---|---|
| Terse interaction style | Reduces assistant output that gets reread in later turns. |
| Per-tool output budgets | Caps or compresses tool outputs within the agent runtime. |
| Read deduplication | Avoids repeatedly paying for the same context. |
| Repository maps | Reduces exploratory file scanning. |
| Model-role splitting | Uses cheaper/smaller models where appropriate. |
| Persistent memory | Carries useful state without rereading everything. |
| Optional RTK integration | Adds shell-output compaction when enabled by the agent. |

**Why it satisfies the criteria:**

- It is a replacement coding agent whose token-saving mechanisms are integrated into one runtime.
- It does not require layering multiple independent Claude/Codex plugins.
- Its benchmark compares the full agent runtime against Codex rather than only showing single-command compression.

**Reputation/evidence:**

- GitHub: `JuliusBrussee/caveman-code`, ~598 stars at retrieval time.
- README reports a 25-task MicroBench using GPT-5.5 xhigh: 524k fresh tokens vs Codex 1.01M, with 14/25 tasks passing vs 15/25 for Codex.

**Do not combine with:** Claude Code skills, Codex plugins, Tokless, Token Savior, or another agent runtime. This is an agent replacement, not middleware.

## Not included

The following are excluded from the qualified stack list despite being useful research leads:

| Excluded item | Reason |
|---|---|
| `RTK + CodeGraph + Ponytail + Caveman` hand-built stack | High-reputation ingredients, but not itself an out-of-box integrated stack unless installed through Tokless. |
| `RTK + CodeGraph` hand-built stack | Plausible and simple, but still manually composed; no stack-level out-of-box integration artifact was reviewed. |
| `ripgrep + ast-grep + qmd` | Separate CLI primitives; requires disciplined workflow. |
| CodeGraph + Serena / multiple code indexes | Competing retrieval authorities. |
| RTK + Headroom / RTK + Context-Mode | Competing output/offload ownership unless the stack explicitly supports the combination. |
| Repomix / Gitingest default use | Repository packing can increase context and conflicts with targeted retrieval. |
| ccusage / Splitrail / tokentop / abtop | Measurement only; useful sidecars, but they do not directly save tokens. |
| OmniRoute / 9router | High-reputation gateways, but current repo evidence is discovery-level and their primary value is provider routing/free-tier aggregation rather than conservative quality-preserving token reduction. |
| Codex token-skills | Relevant but not enough evidence/reputation yet for this strict report. |

## Practical selection guide

| If your dominant waste source is... | Use this qualified stack | Do not add... |
|---|---|---|
| Claude/MCP coding with repeated code lookup, memory, and Bash noise | Token Savior | RTK, CodeGraph, extra memory systems |
| You want a one-command multi-tool setup across Claude/OpenCode/Codex/Antigravity | Tokless | Manual extra compressors/retrievers |
| You want one local-first owner for reads, shell, memory, budgets, and ledger | LeanCTX | RTK, CodeGraph, Headroom, separate memory |
| Huge logs/files/RAG/history blobs | Headroom | RTK, Kompact, TokenTamer, LeanCTX proxy |
| Huge intermediate tool workflows | Context-Mode | RTK, Headroom, pctx unless explicitly supported |
| You can replace the whole terminal coding agent | Caveman Code | Claude/Codex plugin stacks |

## Final recommendation

For the strict out-of-box criterion, the safest answer is **not** to compose independent popular tools manually. Pick one integrated stack owner:

1. **Token Savior** for MCP coding-agent workflows needing code navigation + memory + Bash compaction.
2. **Tokless** when you specifically want a prewired multi-tool stack using RTK, Caveman, CodeGraph, and Context-Mode.
3. **LeanCTX** when you want a local-first all-in-one context layer with accounting.
4. **Headroom** when broad compression of logs/files/RAG/history is the main waste source.
5. **Context-Mode** when intermediate artifacts are the main waste source.
6. **Caveman Code** when replacing the agent runtime is acceptable.

Do not combine these stacks with each other. Each should be treated as the owner of its covered surfaces.
