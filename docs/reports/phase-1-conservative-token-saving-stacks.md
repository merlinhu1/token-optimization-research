# Phase 1 Report: Conservative Token-Saving Stack Candidates for AI Coding Agents

**Date:** 2026-06-25  
**Repository:** `token-optimization-research`  
**Scope:** Candidate combinations of token-saving tools for Claude Code, Codex CLI, Gemini CLI, OpenCode, Cursor/Cline-style coding agents, and similar terminal/MCP agent workflows.

## Executive summary

This report was revised after applying a stricter compatibility criterion:

> A stack only qualifies as conservative if its tools work together **out of the box**, without custom glue, careful routing policies, prompt-discipline workflows, or “use X only when Y” behavior to avoid conflicts.

Under that stricter criterion, **no stack in the current research set is flawless or fully validated yet**. The earlier report over-recommended plausible combinations by proving only “different intervention surfaces,” not true out-of-box co-operation.

The strongest current conclusion is therefore:

- **Claude Code candidate core:** `RTK + CodeGraph`
- **Codex CLI candidate core:** `RTK + CodeGraph`, with `AGENTS.md` as optional native configuration, not counted as a tool
- **Swift/Xcode candidate:** `xcsift` as a single specialized output parser
- **Large-output/offload candidate:** `Context-Mode` as a single specialized offload layer

Tools like Ponytail, Caveman, Serena, Context-Mode+retriever pairings, and xcsift+retriever pairings remain important research candidates, but they should be treated as **marginal additions to validate**, not proven stack members.

## Evidence basis and limits

This report uses:

- the seed catalog in `sources/seed-catalogs/AI-Coding-Token-Savers-Catalog-Revised.md`;
- expanded GitHub discovery in `sources/discovery/github-search-results.json`;
- current GitHub metadata retrieved into `sources/discovery/phase-1-stack-candidate-metadata.json`;
- compatibility categories in `data/techniques.json`;
- repository records in `data/repositories.json`.

GitHub stars are used only as a **reputation signal**, not proof of effect. Reddit direct API/search access was blocked from this environment; DuckDuckGo-discovered Reddit leads are saved in `sources/discovery/reddit-duckduckgo-leads.json`, but they are not treated as recommendation counts until individual threads are reviewed.

## Reputation snapshot for candidate tools

Live GitHub metadata retrieved on 2026-06-25:

| Tool | Stars | Primary technique | Current evidence summary |
|---|---:|---|---|
| `JuliusBrussee/caveman` | 76,923 | Behavioral output compression | High-reputation Claude Code skill. Maintainer reports large output-token reductions, but external evidence says output savings do not always reduce total task tokens. |
| `rtk-ai/rtk` | 66,114 | Terminal/tool-output compression | High-reputation command-output compactor. Maintainer reports 60–90% command-output reduction; external pilot found touched commands were a small part of total spend. |
| `DietrichGebert/ponytail` | 57,944 | Artifact/code minimization | High-reputation Claude Code skill. Maintainer benchmark reports fewer added lines and lower total tokens on over-build-trap tasks. |
| `colbymchenry/codegraph` | 54,566 | Targeted code retrieval | High-reputation graph/retrieval candidate. Maintainer benchmark reports fewer total tokens/tool calls on architecture-question workloads. |
| `chopratejas/headroom` / `headroomlabs-ai/headroom` | 50,965 | Prompt/history/context compression | Strong compression claims; external pilot cautions that extra turns can erase provider-billed savings. Not included in conservative cores because it is a broad compression layer. |
| `oraios/serena` | 25,790 | Targeted code retrieval/editing | Very reputable semantic IDE/MCP toolkit; no single token-saving benchmark reviewed in current repo data. Candidate alternative to CodeGraph, not something to stack with it. |
| `mksglu/context-mode` | 18,176 | Execution offload/code-mode | Strong worked examples for offloading large outputs; generated analysis code/routing is a correctness boundary. Candidate single-purpose offload layer. |
| `zilliztech/claude-context` | 11,962 | Targeted code retrieval | Popular code-search MCP lead; needs deeper review before replacing CodeGraph in a conservative candidate. |
| `yvgude/lean-ctx` | 2,932 | Multi-surface context layer | Powerful multi-surface system; treat as a full-stack alternative, not a component to add on top of other tools. |
| `jgravelle/jcodemunch-mcp` | 1,941 | Targeted code retrieval | Focused tree-sitter symbol-level retrieval lead; needs deeper review. |

## Qualification gate for an out-of-box conservative stack

A stack is **recommended** only if all of these are true:

| Gate | Requirement |
|---|---|
| Concrete target agent | Claude Code, Codex CLI, Gemini CLI, etc.; no generic assumption that one agent’s skill/plugin works in another. |
| Concrete tools | No `or` alternatives inside the stack. Alternatives must be split into separate candidates. |
| Out-of-box integration | One install/config path; tools discover each other or can be used together without custom glue. |
| No routing policy | The stack must not require “use this tool only for X and that tool only for Y” to avoid conflicts. |
| No prompt-discipline dependency | The stack must not rely on the agent remembering a principled workflow to make separate tools cooperate. |
| Positive marginal contribution | Each included tool must plausibly reduce total task cost or quality-preserving context burden in that stack. |
| Built-in raw fallback | Compressed/indexed/offloaded views must have documented access to raw logs/source/artifacts. |
| Stack-level smoke test | At minimum, run one task that exercises the full stack and records whether tools conflict, duplicate context, or hide diagnostics. |

Current state: **no candidate has passed this full gate yet**.

## Candidate cores and downgraded stacks

### Candidate A — Claude Code evaluation priority

**Candidate core:**

```text
RTK + CodeGraph
```

| Component | Tool | Status | Role |
|---|---|---|---|
| Terminal-output compactor | `rtk-ai/rtk` | Candidate core | Compress noisy shell/test/build/Git output. |
| Code-retrieval authority | `colbymchenry/codegraph` | Candidate core | Provide graph/symbol context without broad source reads. |

**Why this is the strongest Claude candidate:**

- Both tools have high reputation signals.
- They target different surfaces: shell output and code retrieval.
- The combination is simpler than the earlier `RTK + CodeGraph + Ponytail + Caveman Lite` stack.

**Not included in the core:**

| Tool | Why not counted as core yet |
|---|---|
| `DietrichGebert/ponytail` | Claude Code-specific behavioral/minimalism layer. Plausible positive contribution, but should be validated as a marginal addition rather than assumed. |
| `JuliusBrussee/caveman` | High reputation, but evidence is mixed for total-session savings. Treat as optional output-style experiment, not conservative default. |

**Status:** candidate, not validated default.

**Required validation:** install/use RTK and CodeGraph together in Claude Code, run a coding task that requires shell output and code retrieval, confirm CodeGraph is adopted without manual prompting, confirm RTK raw-output recovery, then test Ponytail and Caveman as one-at-a-time additions.

---

### Candidate B — Codex CLI evaluation priority

**Candidate core:**

```text
RTK + CodeGraph
```

| Component | Tool | Status | Role |
|---|---|---|---|
| Terminal-output compactor | `rtk-ai/rtk` | Candidate core | Compress noisy shell/test/build/Git output for terminal-heavy Codex sessions. |
| Code-retrieval authority | `colbymchenry/codegraph` | Candidate core, pending Codex integration proof | Provide repo graph/symbol context without broad source reads. |

**Optional native configuration, not counted as a tool:**

```text
AGENTS.md minimalism/output rules
```

`AGENTS.md` is Codex’s native project-instruction surface. It may improve behavior, but it is not an independent token-saving tool and depends on model instruction-following. It should not be counted as a stack component under the out-of-box tool criterion.

**Not included:**

| Tool | Why not counted yet |
|---|---|
| Caveman / Ponytail | Claude Code skills; not assumed to work out of the box in Codex CLI. |
| `lokikill123/codex-token-skills` | Relevant Codex-specific lead, but current reputation/evidence is too thin for a conservative default. |
| `ripgrep + ast-grep + qmd` | Useful primitives, but not an integrated out-of-box token-saving system. They require disciplined agent workflow. |

**Status:** candidate, not validated default.

**Required validation:** verify CodeGraph discovery/use from Codex CLI without custom prompt choreography, verify RTK does not hide diagnostics, then compare with and without `AGENTS.md` rules as a policy experiment.

---

### Candidate C — Large-repo retrieval evaluation, not a stack

Earlier Stack C combined CodeGraph, RTK, fallback primitives, and Ponytail. Under the out-of-box criterion, that was not a distinct stack.

**Correct framing:** evaluate one retrieval authority at a time:

| Candidate retrieval authority | Why evaluate |
|---|---|
| `colbymchenry/codegraph` | Highest reputation among current retrieval-specific candidates. |
| `oraios/serena` | Very high-reputation semantic IDE/MCP toolkit. |
| `zilliztech/claude-context` | Popular Claude Code code-search MCP lead. |
| `jgravelle/jcodemunch-mcp` | Focused tree-sitter symbol-level GitHub code retrieval. |
| `manojmallick/sigmap` | MCP/code-analysis token-reduction lead. |

**Important:** `ripgrep`, `qmd`, and normal file reads are safety/fallback mechanisms, not counted stack components. They are useful for exact verification, but their value depends on agent workflow discipline.

**Status:** evaluation scenario only.

---

### Candidate D — Large-output/offload evaluation, not a stack

Earlier Stack D combined Context-Mode, either CodeGraph or Serena, and Caveman Lite. Under the out-of-box criterion, that fails because it contains alternatives and likely routing assumptions.

**Correct framing:** evaluate concrete candidates separately:

| Candidate | Status | Why |
|---|---|---|
| `mksglu/context-mode` alone | Single-tool offload candidate | Best fit when huge intermediate artifacts dominate and only selected results should return to context. |
| `Context-Mode + CodeGraph` | Pairing candidate | Only valid if out-of-box coexistence is verified. |
| `Context-Mode + Serena` | Pairing candidate | Only valid if out-of-box coexistence is verified. |

**Not included:** Caveman Lite. It may compress final summaries, but its positive marginal effect in an offload-heavy workflow has not been shown.

**Status:** evaluation backlog only.

---

### Candidate E — Swift/Xcode output evaluation, not a full stack

Earlier Stack E combined xcsift, either Serena or CodeGraph, and Ponytail. Under the out-of-box criterion, that fails because it contains alternatives and agent-specific behavioral assumptions.

**Correct framing:**

```text
xcsift
```

as a specialized single-tool candidate for Swift/Xcode/SPM output.

Potential pairings to test separately:

| Candidate | Status | Why |
|---|---|---|
| `xcsift + CodeGraph` | Pairing candidate | Could combine Xcode output reduction with code retrieval, but needs integration/smoke test. |
| `xcsift + Serena` | Pairing candidate | Could combine Xcode output reduction with semantic IDE retrieval, but needs integration/smoke test. |
| `xcsift + Ponytail` | Claude Code-only candidate | Only relevant when the agent is Claude Code and Ponytail is installed as a skill. |

**Status:** specialized evaluation backlog only.

## Tools deliberately excluded from conservative cores

These tools remain research candidates, but are not in the conservative cores because they duplicate a surface, are bundles, depend on prompt discipline, or need deeper evaluation.

| Tool/class | Why excluded from conservative cores |
|---|---|
| Headroom / Kompact / TokenTamer / broad context compressors | Broad compression may rewrite code, schemas, logs, or retrieved context that another tool already selected. External pilot evidence also shows request-level compression can be erased by extra turns. |
| LeanCTX / token-savior / CornMCP-style integrated systems | They span multiple surfaces: retrieval, shell output, memory, graph, and routing. Treat as full-stack alternatives, not components to add on top of RTK+CodeGraph. |
| Repomix / Gitingest | Useful for one-shot handoffs, but default repository packing can conflict with targeted retrieval by increasing context. |
| Tokless / tokenwar / OmniRoute / 9router | Bundles/gateways. Useful references, but not atomic techniques. Decompose into components before evaluation. |
| ccusage / Splitrail / tokentop / abtop | Measurement and observability only. Valuable sidecars for research, but they do not directly save tokens unless they change behavior. |
| Multiple terse-output skills | Caveman, concise, scrooge-mode, kevin-mode, and oafish target similar output-style surfaces. Pick one per target agent if evaluated. |
| Multiple code indexes | CodeGraph, Serena, claude-context, jcodemunch, LeanKG, sigmap, and lean-ctx retrieval should be evaluated against each other, not used simultaneously as primary retrieval authorities. |
| `ripgrep + ast-grep + qmd` as a stack | Useful individual primitives, but not an out-of-box integrated token-saving stack. They require agent discipline. |

## Evaluation backlog

To move from candidate hypotheses to validated stacks, evaluate in this order:

1. **Claude core smoke test:** RTK alone vs RTK + CodeGraph in Claude Code on a terminal-heavy coding task.
2. **Codex core smoke test:** RTK alone vs RTK + CodeGraph in Codex CLI; confirm CodeGraph is actually adopted without custom choreography.
3. **Claude add-on tests:** RTK + CodeGraph vs plus Ponytail, then plus Caveman Lite, one addition at a time.
4. **Retrieval comparison:** CodeGraph vs Serena vs claude-context vs jcodemunch as alternative single retrieval authorities.
5. **Offload comparison:** Context-Mode alone vs Context-Mode + one retrieval authority on huge-log / many-intermediate-artifact workflows.
6. **Swift/Xcode comparison:** xcsift vs RTK on Xcode/SPM output; then test xcsift + exactly one retrieval authority.
7. **Raw fallback audit:** For every output/retrieval/offload component, document whether raw logs/source/artifacts are recoverable out of the box.

## Provisional guidance

For practical research, start with the smallest candidate cores, not full stacks:

### Claude Code

```text
RTK + CodeGraph
```

Then evaluate, one at a time:

```text
+ Ponytail
+ Caveman Lite
```

### Codex CLI

```text
RTK + CodeGraph
```

Optional configuration, not counted as a tool:

```text
AGENTS.md minimalism/output rules
```

### Swift/Xcode

```text
xcsift
```

### Large-output/offload workflows

```text
Context-Mode
```

The core research rule is now stricter than “stack across surfaces.” The real rule is:

> A conservative stack must be both surface-compatible **and** verified to work together out of the box with positive marginal contribution from every included tool.
