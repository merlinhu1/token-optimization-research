# Discovery Summary — 2026-06-25

- Seed catalog GitHub repositories extracted: 56
- Repository records after GitHub/search expansion: 79

## Counts by kind

- `adjacent`: 3
- `agent-runtime-or-routing`: 6
- `benchmark`: 2
- `bundle`: 8
- `catalog`: 3
- `measurement`: 5
- `primitive`: 4
- `research`: 4
- `technique-implementation`: 44

## Counts by technique mapping

- `T01-terminal-tool-output-compression`: 11
- `T02-targeted-code-retrieval`: 22
- `T04-execution-offload-code-mode`: 2
- `T05-prompt-history-context-compression`: 10
- `T06-persistent-memory-reinjection`: 6
- `T07-behavioral-output-compression`: 6
- `T08-artifact-code-minimization`: 3
- `T09-model-routing-cache-economics`: 8
- `T10-repository-packing-digests`: 2
- `T11-measurement-observability`: 5
- `T12-benchmark-evaluation-frameworks`: 5

## Internet/community search notes

- Direct Reddit JSON access was blocked with HTTP 403 from this environment.
- DuckDuckGo via `r.jina.ai` returned Reddit search-result leads; these are saved in `sources/discovery/reddit-duckduckgo-leads.json` for later manual/thread-level review.
- GitHub metadata search results are saved in `sources/discovery/github-search-results.json`.

## New non-seed leads added

- [zilliztech/claude-context](https://github.com/zilliztech/claude-context) — `technique-implementation`, tentative `T02-targeted-code-retrieval`: Code search MCP for Claude Code; makes the entire codebase searchable context for coding agents.
- [jgravelle/jcodemunch-mcp](https://github.com/jgravelle/jcodemunch-mcp) — `technique-implementation`, tentative `T02-targeted-code-retrieval`: Tree-sitter MCP for precise symbol-level GitHub code retrieval; advertises 95%+ code-exploration token cost cuts.
- [zdk/lowfat](https://github.com/zdk/lowfat) — `technique-implementation`, tentative `T01-terminal-tool-output-compression`: CLI that slims command output by stripping noise to save tokens.
- [edouard-claude/snip](https://github.com/edouard-claude/snip) — `technique-implementation`, tentative `T01-terminal-tool-output-compression`: Go CLI proxy with declarative YAML filters for Claude Code/Cursor/Copilot/Gemini command-output reduction.
- [ppgranger/token-saver](https://github.com/ppgranger/token-saver) — `technique-implementation`, tentative `T05-prompt-history-context-compression`: Content-aware output compression for AI coding assistants with structural summaries for code and schema extraction.
- [open-compress/claw-compactor](https://github.com/open-compress/claw-compactor) — `technique-implementation`, tentative `T05-prompt-history-context-compression`: Multi-stage reversible/context-aware token compression with AST-aware code analysis and routing.
- [manojmallick/sigmap](https://github.com/manojmallick/sigmap) — `technique-implementation`, tentative `T02-targeted-code-retrieval`: MCP/code-analysis tool advertising large token reduction for AI coding sessions across many languages.
- [Context-Engine-AI/Context-Engine](https://github.com/Context-Engine-AI/Context-Engine) — `technique-implementation`, tentative `T05-prompt-history-context-compression`: MCP agentic context-compression suite.
- [borhen68/TokenTamer](https://github.com/borhen68/TokenTamer) — `technique-implementation`, tentative `T05-prompt-history-context-compression`: Drop-in proxy that compresses bloated code context in real time.
- [fajarhide/omni](https://github.com/fajarhide/omni) — `technique-implementation`, tentative `T06-persistent-memory-reinjection`: Noise-canceling context and long-term memory for AI agents; targets terminal/context noise.
- [juyterman1000/entroly](https://github.com/juyterman1000/entroly) — `agent-runtime-or-routing`, tentative `T09-model-routing-cache-economics`: Local proxy that compresses context, keeps provider caches hot, and verifies LLM output.
- [FreePeak/LeanKG](https://github.com/FreePeak/LeanKG) — `technique-implementation`, tentative `T02-targeted-code-retrieval`: Knowledge-graph/code-structure system marketed as lean coding context for agents.
- [tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph) — `technique-implementation`, tentative `T02-targeted-code-retrieval`: Local-first code intelligence graph for MCP/CLI with benchmarked context reductions on review tasks.
- [mex-memory/mex](https://github.com/mex-memory/mex) — `technique-implementation`, tentative `T06-persistent-memory-reinjection`: Persistent project memory for AI coding agents with structured scaffold and drift detection.
- [NickCirv/engram](https://github.com/NickCirv/engram) — `technique-implementation`, tentative `T06-persistent-memory-reinjection`: Context spine for AI coding sessions across IDEs and agents.
- [lokikill123/codex-token-skills](https://github.com/lokikill123/codex-token-skills) — `bundle`, tentative `T09-model-routing-cache-economics`: Codex CLI token-saver and memory skills with prefix-cache optimization.
- [0xhimanshu/governor](https://github.com/0xhimanshu/governor) — `bundle`, tentative `T01-terminal-tool-output-compression`: Claude Code usage governor with compact output, context slimming, tool-output filtering, telemetry, drift guardrails.
- [gglucass/headroom-desktop](https://github.com/gglucass/headroom-desktop) — `adjacent`, tentative `T05-prompt-history-context-compression`: Desktop product around Headroom-style compression for Claude Code and Codex usage.
- [decolua/9router](https://github.com/decolua/9router) — `bundle`, tentative `T09-model-routing-cache-economics`: Gateway/router stack for Claude Code/Codex/Cursor/Cline/Copilot/Antigravity with RTK token-saving claims.
- [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute) — `bundle`, tentative `T09-model-routing-cache-economics`: Gateway/router for AI coding tools with RTK and Caveman stacked compression claims.
- [hashgraph-online/awesome-ai-plugins](https://github.com/hashgraph-online/awesome-ai-plugins) — `catalog`, tentative `T12-benchmark-evaluation-frameworks`: Curated plugin list for AI assistants including Claude Code and Codex; source for token-saving plugin leads.
- [hashgraph-online/awesome-codex-plugins](https://github.com/hashgraph-online/awesome-codex-plugins) — `catalog`, tentative `T12-benchmark-evaluation-frameworks`: Curated OpenAI Codex plugin/skill/resource list; includes token-saving and context plugins.
- [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) — `catalog`, tentative `T12-benchmark-evaluation-frameworks`: Large Claude Code toolkit catalog containing many token/cost/context-management entries.
