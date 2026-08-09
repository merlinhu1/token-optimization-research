# Tool dossier: repowise-dev/repowise

## Identity

- Repository: `repowise-dev/repowise`
- URL: https://github.com/repowise-dev/repowise
- Version/ref inspected: `0.39.0` at commit `a3b6714c5523dc7c45d6bce0522035339bcf3afd`
- Snapshot status: pinned-commit
- Commit inspected: `a3b6714c5523dc7c45d6bce0522035339bcf3afd`
- Commit URL: https://github.com/repowise-dev/repowise/commit/a3b6714c5523dc7c45d6bce0522035339bcf3afd
- License: AGPL-3.0-or-later
- Source artifact path: `sources/discovery/2026-08-09-repowise-source-logic.json`
- Date inspected: 2026-08-09
- Evidence stage: source-logic

## Summary

RepoWise precomputes a local codebase-intelligence index and exposes task-shaped retrieval through CLI and MCP. The inspected source combines structural parsing, dependency and call relationships, git-history signals, generated structural documentation, decisions, change risk, dead code, and code-health data. It also contains a separate command-output distillation subsystem.

## Evidence inventory

| Evidence | Inspected surface | Finding |
|---|---|---|
| Package and source snapshot | `pyproject.toml`; 3,606 tracked files at the pinned commit | Python 3.11+ package, version 0.39.0, AGPL-3.0-or-later; a pinned wheel was built for isolated evaluation. |
| Indexing | `pipeline/full_index.py`, `ingestion/parser.py` | Provider-free structural indexing persists the data used by later retrieval and analysis. |
| MCP retrieval | `mcp_server/_server.py`, `tool_context/context.py`, `tool_search.py` | The stdio server registers task-shaped context/search and related code-intelligence tools. |
| Output bounds | `mcp_server/_budget/budgeter.py`, MCP budget/context/search tests | MCP payloads have explicit budgeting and truncation logic with focused unit coverage. |
| Codex integration | `cli/mcp_config.py`, `editor_integrations/codex.py`, `docs/agent/CODEX.md` | Official setup writes project-local MCP configuration, hooks, and managed `AGENTS.md` guidance. |
| Output distillation | `core/distill/engine.py`, hook and CLI docs/tests | Supported command output can be compacted and omissions can be expanded, but automatic rewriting is opt-in. |

## Source-logic findings

- `repowise init --yes --no-prose` builds the graph, git, health, decision, and structural-wiki state without model calls.
- `repowise mcp` serves the local index over stdio. The default single-repository surface includes repository listing plus overview, context, symbol, search, risk, change-risk, health, why, dead-code, and answer-oriented tools.
- Context retrieval accepts task-oriented targets and selectable enrichment rather than requiring repeated raw-file reads.
- Search combines indexed documentation and code structures; semantic search requires a configured embedder, while the prepared provider-free profiles retain full-text and structural retrieval.
- MCP response budgeting and truncation bound returned material, while index freshness metadata warns when live `HEAD` diverges from indexed state.
- `repowise init --codex` creates project-local `.codex/config.toml`, `.codex/hooks.json`, and a managed `AGENTS.md`. The hooks supply lifecycle guidance and stale-index reminders.
- RepoWise documents generic stdio MCP compatibility. The OpenCode profile therefore uses the same pinned local server plus RepoWise-generated `AGENTS.md`; it does not claim an upstream OpenCode-specific installer.
- Command-output distillation is a second token surface. Because its automatic rewrite hook is opt-in, the prepared non-interactive Lifecycle V1 profiles do not force-enable it.

## Token-saving mechanism

RepoWise targets repeated exploration cost: it computes code relationships, repository summaries, risk signals, and documentation before the agent asks, then returns bounded task-shaped answers instead of repeated grep and whole-file reads. Its optional distill path targets terminal-output cost by retaining salient output and leaving reversible expansion markers.

Why it may perform well: Lifecycle tasks that require cross-file discovery, caller tracing, architectural orientation, or risk assessment can reuse the warm index and avoid redundant source reads. Generated product guidance and lifecycle hooks may also improve natural uptake in Codex.

Why it may not: small or obvious tasks may not repay indexing and MCP-call overhead; unsupported or partially resolved language relationships can mislead retrieval; stale indexes can require correction work; and OpenCode lacks the richer upstream Codex-specific hook installer. Provider-billed savings also depend on whether the model naturally uses the installed tools.

## Installation and integration behavior

- Canonical package: pinned wheel built from source commit `a3b6714c5523dc7c45d6bce0522035339bcf3afd`, SHA-256 `e7d3068856a45a3d0501b84e6f52db24521512803a07881cdf145da546d932b4`.
- Codex: official provider-free structural init with `--codex`, project-local MCP config, lifecycle hooks, generated `AGENTS.md`, warm index, runtime binary probe, and MCP initialize/tools-list proof.
- OpenCode: provider-free structural init, generated `AGENTS.md`, isolated host-agnostic stdio MCP registration, warm index, runtime binary probe, and MCP initialize/tools-list proof.
- Model-facing task assistance remains byte-compatible with the matched Lifecycle V1 control; tool use is natural and unforced.
- Generated `.repowise`, `.mcp.json`, `.codex`, and managed guidance are treatment state and excluded from task-source diffs.

## Runtime behavior

The prepared profiles build a warm provider-free index before the model session, probe the pinned executable, and prove the stdio MCP initialize and tools-list exchange. During a run, RepoWise serves bounded structural and full-text retrieval from lane-local SQLite state. Codex also receives the product-generated lifecycle hooks; OpenCode receives the generic MCP server and generated `AGENTS.md` guidance.

## Compatibility notes

RepoWise is a broad retrieval/context authority and overlaps with CodeGraph, jCodeMunch, Serena, SigMap, Graphify, Code Review Graph, CodeScope, and LeanCTX. Run it alone in the individual-tool screen. Its optional command rewriting also overlaps with RTK, Snip, LowFat, and TokenJuice and should not be combined without a separately declared stack protocol.

## Failure modes and limits

The pinned source is alpha-stage software with a large dependency set and local SQLite/index state. Initial indexing adds setup time and disk use. Structural and full-text modes do not require a provider, but model-written prose and semantic embeddings can introduce separate cost, network, and privacy boundaries and are disabled in these prepared runs.

## Evidence boundary

The maintainer reports token, tool-call, latency, and risk-prediction benchmark results in upstream documentation. Those claims remain maintainer evidence: this dossier does not promote them to benchmark-audit or reproduction. Lifecycle V1 protocols prepared here establish launch readiness only; they do not imply a token result.
