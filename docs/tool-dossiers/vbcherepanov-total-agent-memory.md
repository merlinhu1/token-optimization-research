# Tool dossier: vbcherepanov/total-agent-memory

## Identity

- Repository: `vbcherepanov/total-agent-memory`
- URL: https://github.com/vbcherepanov/total-agent-memory
- Local clone inspected: `/tmp/token-leads-20260629/vbcherepanov__total-agent-memory`
- Version/ref inspected: local shallow clone `616d9a6f8b50`, 2026-06-29
- Snapshot status: pinned-commit
- Commit inspected: 616d9a6f8b50
- Commit URL: https://github.com/vbcherepanov/total-agent-memory/commit/616d9a6f8b50
- Source artifact path: `sources/discovery/2026-06-29-graph-leads-b-source-logic.json`
- Date inspected: 2026-06-29
- Evidence stage: source-logic (local shallow clone; representative package entrypoints, MCP server, lookup CLI, retrieval/save paths, installer, hooks, and tests inspected)

## Summary

Total Agent Memory is a persistent-memory MCP server and hook/CLI package. Source inspection confirms it stores records in SQLite plus optional ChromaDB/embedding indexes, exposes memory save/search/update/export/graph/history tools over MCP, includes progressive-disclosure recall modes, and installs Claude/Codex/IDE integrations plus lifecycle hooks. Its token-saving logic is primarily selective recall, compact/index modes, filtering before storage, and nudges to save reusable knowledge rather than replaying long context.

## Evidence inventory

| Evidence type | Files inspected | Notes |
|---|---|---|
| Manifest/entrypoints | `pyproject.toml`, `total_agent_memory/server.py`, `total_agent_memory/lookup.py` | Console scripts route to the packaged wrapper, full `src/server.py`, and a lightweight lookup CLI. |
| MCP/runtime source | `src/server.py`, `src/recall_modes.py` (identified via `memory_recall` transforms), `src/content_filter.py` (referenced by save path), `src/autofilter.py` (referenced by save path) | Main server file was inspected at startup, storage, tool schema, save, recall, and dispatcher regions. |
| State/retrieval implementation | `src/server.py`, `total_agent_memory/lookup.py` | SQLite WAL, FTS5/BM25, optional Chroma/embedding search, fuzzy/graph/HyDE/rerank branches, cache invalidation, and `tam-lookup` FTS/LIKE fallback inspected. |
| Installation/hooks | `install.sh`, `hooks/post-tool-use.sh`, `hooks/user-prompt-submit.sh`, `hooks/lib/memory-nudge.sh` (identified), `tests/test_install_linux.py`, `tests/test_install_macos_hooks.py`, `tests/test_memory_nudge_hook.py` | Installer and representative hook behavior inspected; tests confirm hooks/config creation paths. |
| Tests/benchmarks | `tests/test_no_llm_hot_path_v11.py`, `tests/test_lookup_cli.py`, `tests/test_integration_memory_save.py`, `tests/test_install_linux.py` (paths identified/partly inspected) | Tests indicate coverage areas. Benchmark-method review was not performed. |

## Installation and integration behavior

- `pyproject.toml` defines `total-agent-memory`, `tam`, `tam-lookup`, and compatibility aliases as console scripts; package data includes SQL/JSON/YAML/TXT sidecars.
- `total_agent_memory/server.py` is a thin wrapper that imports `src/server.py` from the installed package and fails with `server.py not found` if packaging is broken.
- `install.sh` supports multiple IDE targets (`claude-code`, `codex`, `cursor`, `cline`, `continue`, `aider`, `windsurf`, `gemini-cli`, `opencode`) and `--uninstall`; it resolves `TAM_MEMORY_DIR`/legacy directories, creates a venv, installs services, and registers MCP/hook config.
- Hook integration includes `SessionStart`, `SessionEnd`/`Stop`, `PostToolUse`, and `UserPromptSubmit` paths in shell/PowerShell form. Representative tests assert Linux/macOS hook registration and copy parity.

## Runtime behavior

- `src/server.py` starts an MCP stdio server via `mcp.server.Server`, initializes a `Store`, opens SQLite `memory.db` in WAL mode, creates sidecar directories, and optionally initializes Chroma collections per embedding space.
- MCP tools include `memory_recall`, `memory_save`, `memory_update`, `memory_stats`, `memory_consolidate`, `memory_export`, `memory_get`, history/delete/relation/tag search, session extraction, and many higher-level memory/evaluation tools.
- `memory_save` persists an outbox intent, redacts `<private>...</private>` and secret-like patterns, optionally auto-detects/uses content filters, normalizes tags, applies a quality gate, deduplicates, writes embeddings, and invalidates caches.
- `memory_recall` calls `recall.search`, then can apply enrichment/entity/intent filters, cognitive enrichment, optional graph expansion, structured-decision filtering, and progressive-disclosure transforms (`mode=index` or `mode=timeline`).
- Retrieval combines FTS5/BM25, optional binary/vector or Chroma search, fuzzy/graph tiers, RRF fusion, optional HyDE/query rewriting/reranking/MMR, and L1/query caches.
- `tam-lookup` is a dependency-light CLI that reads the same `memory.db`, searches FTS5 or falls back to `LIKE`, and can output JSON or compact bullets.
- `hooks/post-tool-use.sh` updates per-session edit/write/save counters and emits memory-save nudges; observation capture is opt-in via `MEMORY_POST_TOOL_CAPTURE=1`. `hooks/user-prompt-submit.sh` asynchronously saves submitted prompts as intents when the DB exists.

## Token-saving mechanism

- Main mechanism: replace repeated full-context replay with selective memory retrieval across durable records and graph/semantic indexes.
- Progressive disclosure: `memory_recall(mode='index')` emits compact metadata and pairs with `memory_get(ids=[...])` for chosen full records; `detail=compact|summary|full|auto` controls output size.
- Save-path reduction: content filters/autofilter shrink noisy command outputs before storage while retaining whitelisted evidence such as paths/URLs/code.
- Workflow nudging: hooks detect write/edit activity without matching `memory_save` calls and emit reminders to store reusable decisions/solutions before context is lost.
- Savings may not become provider-billed reductions if retrieval is overused, embeddings/rerankers add latency/calls, stale or low-quality memories cause correction turns, or another memory authority injects duplicate context.

## Benchmarks and claims

| Claim area | Source inspected | Reviewed method | Caveats |
|---|---|---|---|
| Recall quality and token-reduction claims appear in tool descriptions/comments. | `src/server.py` tool descriptions and code comments. | Not reviewed as benchmark-audit. | Treat as maintainer claims until benchmark harness, tasks, token accounting, and raw outputs are inspected. |
| Hot-path/no-LLM behavior is represented in tests and mode comments. | Test paths identified; mode resolver/import comments inspected. | Source-logic only. | No independent run or provider-billed accounting performed. |

## Compatibility notes

- This is a memory authority, retrieval authority for historical facts, hook owner, and optional background-service owner. Avoid pairing casually with other automatic memory injectors, hook nudgers, or context-recall systems unless one side is disabled.
- It does not replace code-graph tools for current source navigation; it may complement one if boundaries are explicit: code graph for current code, Total Agent Memory for durable decisions/history.
- Compatibility-safe stack design should avoid duplicate control over Claude Code hooks, memory state, prompt nudges, and automatic context surfaces.

## Failure modes and limits

- Startup/runtime depends on optional heavy dependencies (`chromadb`, `sentence-transformers`, `FlagEmbedding`, model downloads) unless configured for fast/no-LLM paths.
- `total_agent_memory/server.py` can fail if `src/server.py` is absent from the package; the manifest comments mention this prior packaging failure mode.
- Hook behavior is best-effort and often asynchronous; hook failures may be swallowed by design to avoid blocking user sessions.
- SQLite/Chroma state can grow, become stale, or contain sensitive data if redaction patterns miss a secret.
- Quality depends on saved memory granularity, deduplication, project/branch tagging, and whether agents actually call `memory_save`.

## Open questions

- Which tools are enabled by default under each IDE profile after installation?
- What are the storage growth, retention, and redaction guarantees under realistic multi-project use?
- How often do recall/index modes reduce provider-billed tokens after accounting for extra tool calls and correction turns?

## Next review tasks

- [ ] Audit installer end-to-end on one non-sensitive sandbox profile, including uninstall semantics.
- [ ] Inspect `recall_modes.py`, `quality_gate.py`, `content_filter.py`, and migration SQL in detail.
- [ ] Run benchmark-audit only if benchmark harness/tasks/raw outputs are available and tied to provider-billed accounting.
