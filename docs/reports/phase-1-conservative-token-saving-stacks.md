# Phase 1 Report: Conservative Token-Saving Stacks for AI Coding Agents

**Date:** 2026-06-25  
**Repository:** `token-optimization-research`  
**Scope:** Conservative combinations of token-saving tools for Claude Code, Codex CLI, Gemini CLI, OpenCode, Cursor/Cline-style coding agents, and similar terminal/MCP agent workflows.

## Executive summary

The safest high-yield strategy is **not** to stack every popular tool. It is to choose **one owner per intervention surface**:

1. one terminal/tool-output compactor;
2. one code-retrieval/index authority;
3. optionally one output-style controller;
4. optionally one artifact/code-minimization discipline;
5. optionally one execution-offload layer for large, multi-step tool workflows.

The strongest conservative default from the current evidence is:

> **RTK + CodeGraph + Ponytail + Caveman Lite**

This stack is compatible because each component owns a different surface:

| Tool | Surface | Why it does not fight the others |
|---|---|---|
| RTK | terminal stdout/stderr compaction | Only touches shell/tool output before it enters context. |
| CodeGraph | code retrieval / repository graph | Replaces broad source reads with graph/symbol queries. |
| Ponytail | artifact/code minimization policy | Changes what code the agent chooses to write, not how command output or source retrieval is compressed. |
| Caveman Lite | final/chat output compression | Reduces narration and summaries; use Lite rather than Ultra to avoid losing important warnings. |

Do **not** add broad context-compression proxies, repository packers, multiple code indexes, or multiple terse-output skills to this default stack unless a specific workload proves positive contribution. Those additions are the most likely to fight existing surfaces or hide evidence.

## Evidence basis and limits

This report uses:

- the seed catalog in `sources/seed-catalogs/AI-Coding-Token-Savers-Catalog-Revised.md`;
- expanded GitHub discovery in `sources/discovery/github-search-results.json`;
- current GitHub metadata retrieved into `sources/discovery/phase-1-stack-candidate-metadata.json`;
- compatibility categories in `data/techniques.json`;
- repository records in `data/repositories.json`.

GitHub stars are used only as a **reputation signal**, not as proof of effect. Reddit direct API/search access was blocked from this environment; DuckDuckGo-discovered Reddit leads are saved in `sources/discovery/reddit-duckduckgo-leads.json`, but they are not treated as recommendation counts until individual threads can be reviewed.

## Reputation snapshot for candidate tools

Live GitHub metadata retrieved on 2026-06-25:

| Tool | Stars | Primary technique | Current evidence summary |
|---|---:|---|---|
| `JuliusBrussee/caveman` | 76,923 | Behavioral output compression | Maintainer reports large output-token reductions; external evidence says output savings do not always reduce total task tokens. |
| `rtk-ai/rtk` | 66,114 | Terminal/tool-output compression | Maintainer reports 60–90% command-output reduction; external pilot found touched commands were a small part of total spend. |
| `DietrichGebert/ponytail` | 57,944 | Artifact/code minimization | Maintainer benchmark reports fewer added lines and lower total tokens on over-build-trap tasks. |
| `colbymchenry/codegraph` | 54,566 | Targeted code retrieval | Maintainer benchmark reports fewer total tokens/tool calls on architecture-question workloads. |
| `chopratejas/headroom` / `headroomlabs-ai/headroom` | 50,965 | Prompt/history/context compression | Strong compression claims; external pilot cautions that extra turns can erase provider-billed savings. |
| `oraios/serena` | 25,790 | Targeted code retrieval/editing | Very reputable semantic IDE/MCP toolkit; no single token-saving benchmark reviewed in current repo data. |
| `mksglu/context-mode` | 18,176 | Execution offload/code-mode | Strong worked examples for offloading large outputs; generated analysis code is a trust boundary. |
| `zilliztech/claude-context` | 11,962 | Targeted code retrieval | Popular code-search MCP lead; needs deeper review before replacing CodeGraph in a conservative stack. |
| `yvgude/lean-ctx` | 2,932 | Multi-surface context layer | Powerful multi-surface system; less suitable as a component in a conservative stack because it spans several surfaces. |
| `jgravelle/jcodemunch-mcp` | 1,941 | Targeted code retrieval | Strong focused lead for tree-sitter symbol-level retrieval; needs deeper review. |

## Conservative stack design rules

A stack qualifies as conservative only if all of these are true:

1. **One tool per surface.** No two tools both own terminal output, code retrieval, MCP schema trimming, memory injection, output style, or model routing.
2. **Raw fallback exists.** The agent can inspect original output/source when compressed output is insufficient.
3. **No default whole-repo ingestion.** Repository packers are not used as a default when targeted retrieval can answer the task.
4. **No hidden learned compression in the critical path unless evaluated.** Learned or broad prompt compression is useful research material but not default-safe for exact code/debugging work.
5. **Behavioral tools are bounded.** Terse-output and minimal-code tools must preserve warnings, test results, security constraints, and exact commands.
6. **Bundles are decomposed.** Bundles such as Tokless, OmniRoute, tokenwar, and LeanCTX are references; they are not added on top of their components.

## Recommended conservative stacks

### Stack A — Conservative default for general coding work

**Use when:** general software-engineering tasks in Claude Code/Codex/Gemini/OpenCode-style agents: code search, edits, tests, debugging, Git operations.

| Component | Tool | Technique | Role |
|---|---|---|---|
| Terminal-output compactor | `rtk-ai/rtk` | T01 | Compress noisy shell/test/build/Git output. |
| Code-retrieval authority | `colbymchenry/codegraph` | T02 | Answer codebase-structure questions without broad file reads. |
| Artifact minimization policy | `DietrichGebert/ponytail` | T08 | Prevent overbuilt code, unnecessary dependencies, and bloated generated artifacts. |
| Output-style controller | `JuliusBrussee/caveman` in **Lite** mode | T07 | Cut filler narration while keeping technical substance. |

**Why this is compatible:**

- RTK owns shell output only.
- CodeGraph owns repository navigation and code context selection.
- Ponytail owns implementation policy, not source retrieval or shell output.
- Caveman Lite owns final prose style, not code retrieval or terminal output.

**Why no other tools are included:**

- Adding Headroom/Kompact would introduce a second broad context-compression layer and may hide exact diagnostics.
- Adding Repomix/Gitingest by default would conflict with CodeGraph’s targeted-retrieval premise.
- Adding LeanCTX/token-savior on top would duplicate several surfaces already owned by RTK/CodeGraph/memory features.
- Adding ccusage/Splitrail/tokentop measures usage but does not directly save tokens.

**Expected token-saving profile:** high practical savings on terminal-heavy and large-repo coding sessions, with relatively low quality sacrifice if raw RTK output can be retrieved and Caveman is kept in Lite mode.

**Main caveat:** Caveman’s effect is output-side; if the workload is dominated by repeated input/context, it may not materially reduce provider-billed totals. Keep it because it is high-reputation and low-conflict, not because it solves input-token growth.

---

### Stack B — Zero-infrastructure portable CLI stack

**Use when:** you cannot install MCP servers or agent hooks, or you want a transparent shell-first workflow that any coding agent can follow.

| Component | Tool | Technique | Role |
|---|---|---|---|
| File/path discovery | `BurntSushi/ripgrep` | T02 primitive | Return relevant paths/lines instead of reading directories or full files. |
| Structural search/rewrite | `ast-grep/ast-grep` | T02 primitive | Find syntax-aware matches without broad full-file reads. |
| Exact line/range extraction | `tobi/qmd` | T02 primitive | Retrieve exact passages by range after locating the target. |
| Terminal-output compactor | `rtk-ai/rtk` | T01 | Compress noisy shell/test/build/Git output. |

**Why this is compatible:**

- `ripgrep`, `ast-grep`, and `qmd` are not simultaneous owners of the same output stream. They form a pipeline: locate → structurally refine → extract exact range.
- RTK handles command-output compaction after the command runs.
- No persistent memory, no broad prompt compression, and no model-output rewriting are introduced.

**Why no other tools are included:**

- No CodeGraph/Serena here because this stack is for low-infrastructure portability.
- No Caveman/Ponytail because this stack intentionally avoids behavioral prompt changes.
- No repository packer because exact search/range retrieval is the point.

**Expected token-saving profile:** very low quality sacrifice, excellent determinism, and high savings on search/read-heavy workflows. This is likely the safest baseline for evaluation because every step is inspectable and reversible.

**Main caveat:** savings depend on the agent actually using targeted commands instead of falling back to full-file reads.

---

### Stack C — Large-repo semantic retrieval stack

**Use when:** large codebases where repeated file scanning is the dominant cost and a semantic/symbol graph is acceptable.

| Component | Tool | Technique | Role |
|---|---|---|---|
| Code-retrieval authority | `colbymchenry/codegraph` | T02 | Primary graph/symbol/relation index. |
| Terminal-output compactor | `rtk-ai/rtk` | T01 | Compress build/test/Git output. |
| Exact fallback | `ripgrep` + normal file reads or `qmd` | T02 primitive | Verify exact source before editing. |
| Artifact minimization policy | `DietrichGebert/ponytail` | T08 | Keep generated changes small after retrieval identifies the target. |

**Why this is compatible:**

- CodeGraph is the primary code-navigation authority.
- `ripgrep`/`qmd` are fallback verification tools, not competing semantic indexes.
- RTK only sees shell output.
- Ponytail only constrains generated artifacts.

**Why no other code index is included:**

Do not combine CodeGraph with Serena, claude-context, jcodemunch, LeanKG, or lean-ctx as simultaneous primary retrieval authorities. They can be compared in evaluation, but stacking several indexes encourages duplicate context and inconsistent answers.

**Expected token-saving profile:** strongest for architecture questions, impact analysis, and large-repo orientation.

**Main caveat:** graph/index accuracy and freshness must be checked. Exact source inspection is still required before edits.

---

### Stack D — Large-output workflow offload stack

**Use when:** workflows repeatedly create huge intermediate artifacts: logs, web/API payloads, many file reads, multi-step MCP calls, or exploratory analysis where only final selected results matter.

| Component | Tool | Technique | Role |
|---|---|---|---|
| Execution offload | `mksglu/context-mode` | T04 | Run heavy analysis outside the main model context and return selected results. |
| Code-retrieval authority | `colbymchenry/codegraph` **or** `oraios/serena`, not both | T02 | Retrieve code context selectively before/after offloaded analysis. |
| Output-style controller | `JuliusBrussee/caveman` in Lite mode | T07 | Keep final summaries compact. |

**Why this is compatible:**

- Context-Mode owns multi-step offloaded execution.
- One code-retrieval authority owns code lookup.
- Caveman Lite only reduces final narration.

**Why RTK is not included by default:**

Context-Mode and RTK can be compatible with a careful routing policy, but this report keeps Stack D conservative: if Context-Mode owns the heavy-output path, do not add a second output-compaction hook unless evaluation shows positive marginal benefit.

**Expected token-saving profile:** high savings when intermediate artifacts are huge and only a small selected result is needed.

**Main caveat:** generated or sandboxed analysis becomes a correctness boundary. This is safe only when the raw artifacts remain retrievable.

---

### Stack E — Swift/Xcode conservative stack

**Use when:** Swift Package Manager or Xcode build/test output is the main token sink.

| Component | Tool | Technique | Role |
|---|---|---|---|
| Xcode/SPM output parser | `ldomaradzki/xcsift` | T01 | Convert Xcode/SPM output to concise JSON/TOON/GitHub Actions formats. |
| Code-retrieval authority | `oraios/serena` or `colbymchenry/codegraph`, not both | T02 | Navigate symbols/references without reading broad source. |
| Artifact minimization policy | `DietrichGebert/ponytail` | T08 | Avoid overbuilt implementation changes. |

**Why this is compatible:**

- xcsift owns the Swift/Xcode build-output surface.
- One retrieval tool owns code lookup.
- Ponytail owns generated-change minimalism.

**Why RTK is not included:**

For Xcode/SPM logs, xcsift is the specialized parser. RTK would be a competing output reducer for the same command stream and should not be layered by default.

**Expected token-saving profile:** best for Apple-platform projects where build logs dominate context.

**Main caveat:** specialized to Swift/Xcode workflows.

## Tools deliberately excluded from conservative stacks

These tools remain important research candidates, but they are not in the conservative stacks above because they either duplicate a surface, are bundles, or need deeper evaluation first.

| Tool/class | Why excluded from default conservative stacks |
|---|---|
| Headroom / Kompact / TokenTamer / broad context compressors | Can be powerful, but broad compression may rewrite code, schemas, logs, or retrieved context that another tool already selected. External pilot evidence also shows request-level compression can be erased by extra turns. |
| LeanCTX / token-savior / CornMCP-style integrated systems | They span multiple surfaces: retrieval, shell output, memory, graph, and routing. Treat as full-stack alternatives, not components to add on top of RTK+CodeGraph. |
| Repomix / Gitingest | Useful for one-shot handoffs, but default repository packing can conflict with targeted retrieval by increasing context. |
| Tokless / tokenwar / OmniRoute / 9router | Bundles/gateways. Useful references, but not atomic techniques. Decompose into components before evaluation. |
| ccusage / Splitrail / tokentop / abtop | Measurement and observability only. Valuable sidecars for research, but they do not directly save tokens unless they change behavior. |
| Multiple terse-output skills | Caveman, concise, scrooge-mode, kevin-mode, and oafish all target similar output-style surfaces. Pick one; do not stack them. |
| Multiple code indexes | CodeGraph, Serena, claude-context, jcodemunch, LeanKG, sigmap, and lean-ctx retrieval should be evaluated against each other, not used simultaneously as primary retrieval authorities. |

## Evaluation backlog implied by this report

To move from conservative hypothesis to evidence, evaluate these pairings first:

1. **RTK alone vs RTK + CodeGraph** on a terminal-heavy coding task.
2. **CodeGraph vs Serena vs claude-context vs jcodemunch** as alternative single code-retrieval authorities.
3. **RTK + CodeGraph vs RTK + CodeGraph + Ponytail** on over-build-trap feature tasks.
4. **RTK + CodeGraph + Ponytail vs plus Caveman Lite** to see whether output savings reduce total-session cost or only visible prose.
5. **Context-Mode vs RTK** on huge-log / many-intermediate-artifact workflows to determine when offload beats compaction.
6. **xcsift vs RTK** on Xcode/SPM output to confirm specialized parser superiority in Swift workflows.

## Final recommendation

For practical use today, start with **Stack A**:

```text
RTK + CodeGraph + Ponytail + Caveman Lite
```

If exactness and portability matter more than automation, use **Stack B**:

```text
ripgrep + ast-grep + qmd + RTK
```

If very large intermediate artifacts dominate the workload, evaluate **Stack D** separately rather than adding Context-Mode to Stack A by default.

The core rule is simple: **stack across surfaces, never within the same surface.**
