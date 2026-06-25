# Compatibility-Based Taxonomy

This taxonomy groups techniques by the buffer, decision point, or workflow surface they control. Techniques in the same group are often alternatives or need careful ordering. Techniques in different groups are candidates for stacking.

## Category model

| ID | Category | Intervention surface | Compatibility rule | Example implementations |
|---|---|---|---|---|
| T01 | Terminal/tool-output compression | Shell stdout/stderr before model context | Competing command proxies/compactors should not double-wrap the same command stream. | RTK, TRS, TokenJuice, skim compactors |
| T02 | Targeted code retrieval and representation | Source-code reads, symbol queries, repo maps, AST outlines | Multiple indexes can coexist, but the agent should choose one primary retrieval path per task to avoid duplicated context. | codegraph, lean-ctx, Serena, tokToken, ast-bro |
| T03 | MCP/API response shaping | Tool JSON schemas and MCP responses | Competing schema/field trimmers can remove required fields if layered blindly. | mcp-trim, GCF-style encodings |
| T04 | Execution offload / code-mode sandboxing | Multi-step tool workflows executed outside the main context | Stackable with retrieval/output tools, but generated analysis code becomes a trust boundary. | pctx Code Mode, context-mode |
| T05 | Prompt/history/context compression | Conversation history, retrieved prose, logs, long prompts | Learned compressors and deterministic memory summaries should not both rewrite the same facts without raw fallback. | LLMLingua, Headroom, memory summarizers |
| T06 | Persistent memory and reinjection | Cross-session facts, observations, task state | Multiple memories can conflict or duplicate unless one source is authoritative. | cavemem, claude-mem, lean-ctx memory |
| T07 | Behavioral output compression | Model response style and narration | Multiple terse-mode prompts can stack into unreadability; choose one style controller. | Caveman, concise, scrooge-mode |
| T08 | Artifact/code minimization | Generated code/docs size, dependency choices | Usually stackable with input savings; conflicts with feature-completeness or readability only by policy. | Ponytail, Whippet, Bonsai |
| T09 | Model routing and cache economics | Which model/provider handles which task and how prompts align to caches | Saves premium tokens/cost, not always total tokens; conflicts with quality and privacy policies. | local-model routing, provider proxies |
| T10 | Repository packing/digests | Whole-repo prompt packs and generated context bundles | Can conflict with targeted retrieval by encouraging over-ingestion; use only when task requires broad context. | Repomix, Gitingest |
| T11 | Measurement and observability | Usage logs, dashboards, accounting | Not a saving technique unless it changes routing or prompts. Stackable as instrumentation. | ccusage, Splitrail, Tokentop |
| T12 | Benchmark/evaluation frameworks | Test harnesses, token counters, quality gates | Not a saving technique; used to compare techniques. | tokbench, agentic-token-bench |

## Bundle handling

Bundled solutions are cataloged as repositories with `kind: bundle`. They should reference component repositories and technique IDs, but they should not create new technique IDs unless they introduce a distinct atomic mechanism.

## Classification questions

For each repository or paper:

1. What exact buffer or decision point is reduced?
2. Is the reduction deterministic, learned, or agent-behavior-dependent?
3. What raw fallback exists?
4. Which quality risk is most likely: missing evidence, broken schema, wrong code, lost diagnostics, or extra turns?
5. Which other techniques would conflict with it?
6. Which orthogonal techniques can be stacked with it?
