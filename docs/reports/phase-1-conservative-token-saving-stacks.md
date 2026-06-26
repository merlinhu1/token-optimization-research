# Phase 1 Report: Conservative Token-Saving Stacks for AI Coding Agents

**Date:** 2026-06-25  
**Repository:** `token-optimization-research`  
**Scope:** tool stacks that should work together out of the box using the tools' documented installers/plugins/hooks, with no custom glue and no workflow choreography required to keep them from fighting.

## Executive summary

This report now treats “out of the box” correctly:

- A stack does **not** need to have been pre-packaged by someone else.
- A stack **does** need documented install/config paths for each tool in the target agent.
- The tools must own different surfaces so they do not compete.
- The stack must not depend on the agent remembering a fragile workflow such as “use this search tool first, then this one, then this extractor.”
- If a tool does not make a positive contribution for the stack, it is not included.

The recommended conservative stacks from the current research are, ranked by current evidence and expected quality-preserving savings:

| Rank | Stack | Target agent/workflow | Why it is included |
|---:|---|---|---|
| 1 | **RTK + CodeGraph + Ponytail** | Claude Code | Highest-reputation balanced stack: shell-output compaction + semantic code retrieval + anti-overbuild discipline. |
| 2 | **RTK + CodeGraph + Ponytail** | Codex CLI | Same balanced surfaces, using each tool's documented Codex integration. |
| 3 | **Token Savior MCP Stack** | Claude/MCP agents | One integrated MCP stack: code navigation + memory + Bash compaction. Strongest stack-level benchmark claim. |
| 4 | **Headroom wrap / proxy stack** | Claude, Codex, Aider, OpenCode, Copilot, app/proxy workflows | One integrated compression layer with raw-cache retrieval and high reputation. |
| 5 | **Tokless managed stack** | Claude Code, OpenCode, Codex, Antigravity | One-command packaged stack wiring RTK, Caveman, CodeGraph, and Context-Mode. More aggressive than stacks 1–2. |
| 6 | **Context-Mode offload stack** | Large intermediate-output workflows | One integrated offload layer for huge tool/MCP workflows. |

The practical default is **Stack 1 for Claude Code** or **Stack 2 for Codex CLI** when anti-overbuild behavior is desired. If behavior-changing rules are undesirable, use the lower-intervention `RTK + CodeGraph` variant and measure.

## Evidence basis

This report uses:

- seed catalog: `sources/seed-catalogs/AI-Coding-Token-Savers-Catalog-Revised.md`;
- GitHub discovery: `sources/discovery/github-search-results.json`;
- current metadata: `sources/discovery/phase-1-stack-candidate-metadata.json`;
- repository records: `data/repositories.json`;
- direct README checks for RTK, CodeGraph, Ponytail, Caveman, Token Savior, Tokless, LeanCTX, Headroom, and Context-Mode.

GitHub stars are reputation signals, not proof. Benchmark claims are kept labeled as maintainer/external where known.

## Compatibility model

A valid stack can be analyst-constructed if every tool has a normal documented install path and the tools do not own the same surface.

| Surface | Only one owner per stack | Why |
|---|---|---|
| Terminal/tool output | RTK, Token Savior Bash compaction, Headroom output compression, LeanCTX shell compression, Context-Mode offload, etc. | Multiple output compressors can hide diagnostics or double-compress. |
| Code retrieval/index | CodeGraph, Serena, claude-context, jcodemunch, LeanCTX code graph, Token Savior navigation, etc. | Multiple retrieval authorities create duplicate context and inconsistent answers. |
| Behavioral output compression | Caveman, scrooge-mode, concise, etc. | Multiple terse/style controllers can fight over verbosity, clarity, and safety. |
| Artifact/code minimization | Ponytail, Bonsai, Whippet, etc. | Multiple YAGNI/minimal-code rulesets can duplicate or over-constrain implementation choices; choose one unless a combined stack is documented and tested. |
| Memory/reinjection | Token Savior memory, LeanCTX memory, Headroom memory, Cavemem, etc. | Multiple memories can duplicate or stale-inject facts. |
| Offloaded execution | Context-Mode, pctx, Headroom proxy modes, etc. | Offload/routing layers should not be stacked unless explicitly integrated. |

## Stack 1 — Claude Code balanced conservative stack

```text
RTK + CodeGraph + Ponytail
```

**Target:** Claude Code.

| Tool | Documented integration | Surface owned | Positive contribution |
|---|---|---|---|
| `rtk-ai/rtk` | `rtk init -g` for Claude Code / Copilot default; installs hook + RTK.md. | Bash/tool-output compaction. | Reduces noisy Git/test/build/package-manager output before it enters context. |
| `colbymchenry/codegraph` | `codegraph install`, then `codegraph init` per project; README says it auto-configures Claude Code and runs as MCP. | Semantic code retrieval / code graph. | Replaces broad file reads and exploratory scans with targeted graph/symbol queries. |
| `DietrichGebert/ponytail` | Claude Code plugin marketplace: `/plugin marketplace add DietrichGebert/ponytail`, then `/plugin install ponytail@ponytail`. | Artifact/code minimization behavior. | Reduces overbuilt code, unnecessary dependencies, and excessive implementation scope. |

### Why these work together out of the box

- RTK uses Claude Code shell/Bash hooks and commands.
- CodeGraph is an MCP code-intelligence server.
- Ponytail is a Claude Code plugin/skill/ruleset for implementation discipline.
- None is a second owner of the same surface: RTK does not index code, CodeGraph does not compress Bash output, and Ponytail does not intercept terminal output or provide a competing code index.

### Behavioral/artifact layer choice

Ponytail is selected as the default artifact-minimization layer, not because it is locally installed, but because it has the strongest currently reviewed evidence for total-task savings among minimal-code candidates.

| Candidate | Surface | Evidence summary | Conservative-stack conclusion |
|---|---|---|---|
| Ponytail | Artifact/code minimization | Reproducible maintainer benchmark: 54% fewer added lines, 22% fewer total tokens, 20% lower cost; caveat: model/task-specific. | Best-evidenced default if adding an anti-overbuild layer. |
| Caveman | Behavioral output compression | High reputation and 65% output-token claim, but mixed total-session evidence; Ponytail benchmark found +7% total tokens on feature tasks. | Use instead when terse prose is the main goal; do not add by default without stack-level testing. |
| scrooge-mode | Behavioral output compression | Strong output-token reductions in maintainer benchmark, but output-only and low-reputation/new. | Promising alternative for terse output, not top conservative default. |
| concise | Behavioral output compression | Example-based 60–70% output-token claim; no task-level benchmark reviewed. | Insufficient evidence for top default. |
| Bonsai | Artifact/code minimization | Similar YAGNI mechanism; benchmark harness exists but no published paid benchmark numbers. | Closest Ponytail substitute, but weaker evidence. |
| Whippet | Artifact/code minimization | Maintainer evaluation did not demonstrate code-size/token savings on tested strong model. | Workflow-discipline candidate, not a savings default. |
| No behavioral/artifact layer | None | Avoids behavior-rule risk but gives up a documented savings source. | Valid lowest-risk variant: `RTK + CodeGraph`. |

### Why Caveman is not the default behavioral add-on

Caveman is high-reputation and may reduce visible assistant prose, but it is primarily a T07 output-style controller, while Ponytail is a T08 artifact/code-minimization controller. Those surfaces are not identical. The conservative reason not to include both is that both steer model behavior and no combined `RTK + CodeGraph + Ponytail + Caveman` stack benchmark was reviewed. Caveman's evidence is also mixed for total-session savings: metadata records strong output-token claims but also Ponytail benchmark counter-evidence where Caveman used 7% more total tokens on feature tasks. Use Caveman, scrooge-mode, or concise when terse prose is the main goal; use Ponytail when reducing overbuilt artifacts is the goal.

### Expected profile

This is the recommended balanced conservative Claude Code stack: high-reputation tools, low overlap, no custom glue, and each component targets a different major token-waste source. It is not a globally proven optimum; no reviewed benchmark tests the exact three-tool combination end to end.

**Lower-intervention variant:** `RTK + CodeGraph` only. This avoids behavior-changing rules and is the safest default when implementation completeness, explanation clarity, or target-model interaction with Ponytail is uncertain. It also gives up Ponytail's documented anti-overbuild savings, so it should be treated as lower-risk but potentially lower-savings.

## Stack 2 — Codex CLI balanced conservative stack

```text
RTK + CodeGraph + Ponytail
```

**Target:** Codex CLI.

| Tool | Documented integration | Surface owned | Positive contribution |
|---|---|---|---|
| `rtk-ai/rtk` | `rtk init -g --codex`. | Bash/tool-output compaction. | Reduces noisy command output in terminal-heavy Codex sessions. |
| `colbymchenry/codegraph` | `codegraph install`; README lists Codex as a supported agent and says it wires CodeGraph MCP into each supported agent. | Semantic code retrieval / code graph. | Reduces broad code reads and repeated repository exploration. |
| `DietrichGebert/ponytail` | `codex plugin marketplace add DietrichGebert/ponytail`, then install via `/plugins` and trust hooks. | Artifact/code minimization behavior. | Keeps Codex from overbuilding, adding unnecessary dependencies, or generating bloated artifacts. |

### Why these work together out of the box

- Each tool has a documented Codex integration path.
- RTK owns shell-output compaction.
- CodeGraph owns code retrieval.
- Ponytail owns implementation minimalism.
- The stack does not require a custom router or a “remember to use X before Y” search workflow.

### Why AGENTS.md alone is not counted

Codex-native `AGENTS.md` rules are useful, but they are configuration, not a tool. Ponytail is included instead because direct README review found a documented Codex plugin path and lifecycle hooks. Keep this contingent on the current Ponytail README/plugin marketplace; the summarized metadata is less explicit about Codex than the README text.

### Expected profile

This is the recommended balanced Codex-optimized conservative stack currently found: it uses the same surface separation as Stack 1, but with Codex-specific installation paths. It is not a globally proven optimum; no reviewed benchmark tests the exact three-tool combination end to end.

**Lower-intervention variant:** `RTK + CodeGraph` only. This avoids behavior-changing rules and is the safest default when implementation completeness, explanation clarity, or target-model interaction with Ponytail is uncertain. It also gives up Ponytail's documented anti-overbuild savings, so it should be treated as lower-risk but potentially lower-savings.

## Stack 3 — Token Savior MCP integrated stack

```text
Token Savior MCP profile
```

**Target:** Claude Code and other MCP-compatible coding agents.

| Internal component | Surface owned | Positive contribution |
|---|---|---|
| Structural code navigation | Code retrieval. | Avoids broad file reads through symbol/code-navigation tools. |
| Persistent memory | Memory/reinjection. | Reduces repeated rediscovery across turns/sessions. |
| Bash output compaction | Terminal/tool output. | Compacts common Git/test/build/package-manager outputs. |
| Compact MCP profile/manifests | Tool-context overhead. | Reduces the cost of exposing tools. |

### Why it works out of the box

Token Savior is one MCP server/profile. Its README documents `pip install "token-savior-recall[mcp]"`, `uvx token-savior-recall`, and agent init paths such as `ts init --agent {claude,cursor,gemini,codex}`. It deep-merges supported agent hook settings, backs up configs, dedups hooks, and exposes one coordinated tool surface.

### Reputation/evidence

- GitHub: `Mibayy/token-savior`, ~1k stars at retrieval time.
- README reports Claude Opus 4.7 on 96 coding tasks: active tokens/task `17,221 → 3,395` (-80%) and score `141/180 → 188/192`.
- This is maintainer-run and profile-dependent, but it is stack-level evidence rather than only per-command compression.

### Do not add

Do not add RTK, CodeGraph, LeanCTX, Cavemem, or another MCP memory/retrieval/output layer. Token Savior already owns those surfaces.

## Stack 4 — Headroom integrated compression stack

```text
Headroom wrap / proxy / MCP mode
```

**Target:** Claude, Codex, Aider, OpenCode, Copilot CLI, app/proxy workflows, or any workflow dominated by large logs/files/RAG/history/tool outputs.

| Internal component | Surface owned | Positive contribution |
|---|---|---|
| Content router + specialized compressors | Broad context compression. | Routes JSON, code, prose, logs, files, and history to appropriate compressors. |
| Agent wrap / proxy / MCP modes | Integration surface. | Provides one coordinated deployment path instead of several independent compressors. |
| Original-content cache / retrieval | Raw fallback. | Keeps raw content retrievable when compressed output is insufficient. |
| Optional memory/code-graph modes | Memory/retrieval when enabled by Headroom itself. | Keeps those features under one stack owner instead of external add-ons. |

### Why it works out of the box

Headroom documents `pip install "headroom-ai[all]"`, `npm install headroom-ai`, `headroom wrap claude|codex|aider|copilot|opencode`, proxy mode, and MCP mode. The README lists agent compatibility and says originals are cached/retrievable.

### Reputation/evidence

- GitHub: `chopratejas/headroom` / `headroomlabs-ai/headroom`, ~51k stars at retrieval time.
- Maintainer claims 60–95% fewer tokens; repo data records 47–92% savings in maintainer benchmarks.
- External N=1 evidence in this repo found request-level compression did not necessarily lower provider-billed totals due to extra turns, so Headroom should own the compression layer alone and be measured end-to-end.

### Do not add

Do not add RTK, Kompact, TokenTamer, LeanCTX proxy compression, or another output/context compressor. If using Headroom memory/code-graph options, do not add external memory or retrieval systems.

## Stack 5 — Tokless managed multi-tool stack

```text
tokless
```

**Target:** users who want a one-command multi-tool setup for Claude Code, OpenCode, Codex, or Antigravity.

| Bundled tool | Surface owned | Positive contribution |
|---|---|---|
| RTK | Terminal/tool output. | Trims noisy Bash/tool output. |
| Caveman | Output style. | Reduces verbose agent prose. |
| CodeGraph | Code retrieval. | Reduces whole-file reads through code-graph queries. |
| Context-Mode | Offloaded execution. | Runs heavy work in a sandbox and returns only selected results. |

### Why it works out of the box

Tokless is an installer/lifecycle manager for exactly this combination. Its README says “one command, pick your agent, restart,” supports `tokless`, `tokless update`, `tokless doctor`, `tokless uninstall`, and supports `--agents claude,opencode,codex,antigravity`. It explicitly describes the four tools as targeting different waste sources.

### Reputation/evidence

- GitHub: `HoangP8/tokless`, ~65 stars at retrieval time.
- Component reputation is high: Caveman ~76k, RTK ~66k, CodeGraph ~54k, Context-Mode ~18k.
- Evidence is mostly component-level, but Tokless is a genuine out-of-box stack artifact.

### Quality caveat

Tokless is more aggressive than Stacks 1–2 because it includes both Caveman and Context-Mode. Use it when maximum token reduction matters more than preserving the normal agent interaction style.

## Stack 6 — Context-Mode offload stack

```text
Context-Mode
```

**Target:** workflows dominated by huge intermediate artifacts: long logs, large API/tool outputs, many MCP calls, web/API payloads, or exploratory analysis where only a selected result should enter context.

| Internal component | Surface owned | Positive contribution |
|---|---|---|
| MCP/tool offload layer | Offloaded execution. | Runs multi-step tool workflows outside the main context. |
| Sandbox execution | Intermediate artifact isolation. | Keeps large raw payloads out of the chat context. |
| Result selection | Output reduction. | Returns only selected outputs. |
| Hooks/routing enforcement | Agent integration. | Applies the offload model automatically on supported platforms. |

### Why it works out of the box

Context-Mode documents platform-specific plugin/MCP installs, including Claude Code plugin marketplace install, MCP-only install, Copilot CLI plugin bundle, and other agent integrations. Hook-capable platforms get automatic routing enforcement; non-hook platforms get documented setup.

### Reputation/evidence

- GitHub: `mksglu/context-mode`, ~18k stars at retrieval time.
- README and repo data record large worked reductions such as 150k-to-2k and 700KB-to-3KB examples.
- It has public community attention and multi-platform documentation.

### Do not add

Do not add RTK, Headroom, pctx, or another offload/output-compression tool unless the combination is explicitly supported and smoke-tested. Context-Mode owns the large-intermediate-output surface.

## Stack 7 — Caveman Code replacement-agent stack

```text
Caveman Code
```

**Target:** users willing to replace Codex/Claude-style terminal agent runtime with a token-lean agent rather than adding middleware.

| Internal component | Surface owned | Positive contribution |
|---|---|---|
| Terse interaction style | Output style. | Reduces assistant output that is reread in later turns. |
| Per-tool output budgets | Tool output. | Caps/compresses outputs inside the runtime. |
| Read deduplication | Context reuse. | Avoids paying repeatedly for the same context. |
| Repository maps | Retrieval/orientation. | Reduces exploratory file scanning. |
| Model-role splitting | Model routing. | Uses smaller/cheaper models where appropriate. |
| Persistent memory | Memory. | Carries useful state without rereading everything. |
| Optional RTK integration | Shell output. | Adds compaction through the agent runtime when enabled. |

### Why it works out of the box

Caveman Code is a replacement coding agent. Its token-saving surfaces are part of one runtime rather than several independent plugins. README installation is a normal package install (`npm install -g @juliusbrussee/caveman-code`).

### Reputation/evidence

- GitHub: `JuliusBrussee/caveman-code`, ~598 stars at retrieval time.
- README reports a 25-task MicroBench using GPT-5.5 xhigh: 524k fresh tokens vs Codex 1.01M, with 14/25 tasks passing vs 15/25 for Codex.

### Do not add

Do not add Claude Code skills, Codex plugins, Tokless, Token Savior, or another agent runtime. This is an agent replacement.

## Exclusions with actual reasons

| Excluded combination | Actual reason |
|---|---|
| `RTK + CodeGraph + Ponytail + Caveman` | Ponytail and Caveman are not identical surfaces: Ponytail is artifact/code minimization, while Caveman is behavioral output compression. The conservative exclusion reason is that both steer model behavior and no combined stack benchmark was reviewed; use only when deliberately accepting a more aggressive behavior-changing stack. |
| `ripgrep + ast-grep + qmd` | These are separate CLI primitives, not an out-of-box integrated stack. They rely on agent workflow discipline. |
| CodeGraph + Serena / multiple retrieval engines | Competing code-retrieval authorities. Pick one retrieval owner. |
| RTK + Headroom | Competing output/context compression owners. Pick one compression owner. |
| RTK + Context-Mode | Competing output/offload owners for large tool results unless an integration explicitly supports the pairing. |
| Repomix / Gitingest as defaults | Repository packing can increase context and conflicts with targeted retrieval. Useful only for one-shot handoffs. |
| ccusage / Splitrail / tokentop / abtop | Measurement only. Useful sidecars, but not token-saving stack components. |
| OmniRoute / 9router | Strong gateway/reputation signals, but current evidence emphasizes provider routing/free-tier aggregation more than conservative quality-preserving token reduction. |

## Practical selection guide

| Situation | Use this stack |
|---|---|
| Claude Code, recommended balance when anti-overbuild behavior is desired | Stack 1: RTK + CodeGraph + Ponytail; lower-intervention variant: RTK + CodeGraph |
| Codex CLI, recommended balance when anti-overbuild behavior is desired | Stack 2: RTK + CodeGraph + Ponytail; lower-intervention variant: RTK + CodeGraph |
| MCP coding agent where one server should own retrieval, memory, and Bash compaction | Stack 3: Token Savior |
| Large logs/files/RAG/history/tool-output compression | Stack 4: Headroom |
| One-command multi-tool setup across Claude/OpenCode/Codex/Antigravity | Stack 5: Tokless |
| Huge intermediate tool/MCP workflows | Stack 6: Context-Mode |
| Willing to replace the terminal coding agent | Stack 7: Caveman Code |

## Final recommendation

For Merlin's criterion — conservative, out-of-box, compatible, positive contribution only — the recommended balanced defaults are:

1. **Claude Code:** `RTK + CodeGraph + Ponytail`
2. **Codex CLI:** `RTK + CodeGraph + Ponytail`
3. **Integrated MCP alternative:** `Token Savior`
4. **Broad compression alternative:** `Headroom`

The important shift is that analyst-constructed stacks are allowed when the tools have documented native installs and separate surfaces. They do not need to be pre-packaged by a third party. What is not allowed is a loose bundle of primitives that only works if the agent follows a hand-authored workflow.

These are not proven globally best stacks. They are the best-supported balanced candidates under current reviewed evidence. The main uncertainty is behavioral-layer transferability: Ponytail's evidence is maintainer-run and task/model-specific, and no combined `RTK + CodeGraph + Ponytail` benchmark has been reviewed.
