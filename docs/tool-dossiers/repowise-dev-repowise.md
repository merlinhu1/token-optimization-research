# Tool dossier: repowise-dev/repowise

## Identity

- Repository: `repowise-dev/repowise`
- URL: https://github.com/repowise-dev/repowise
- Version/ref inspected: `0.45.0` release at commit `e2bb8a2e4eff3d00005a602ac65a8e4be7daa4a3`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: e2bb8a2e4eff3d00005a602ac65a8e4be7daa4a3
- Commit URL: https://github.com/repowise-dev/repowise/commit/e2bb8a2e4eff3d00005a602ac65a8e4be7daa4a3
- License: AGPL-3.0-or-later
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 0.45.0 release checkout from the batch release corpus, the same bytes its lanes install; representative source/config files inspected)

## Summary

RepoWise precomputes a local codebase-intelligence index and exposes task-shaped retrieval through CLI and MCP. The inspected source combines structural parsing, dependency and call relationships, git-history signals, generated structural documentation, decisions, change risk, dead code, and code-health data. It also contains a separate command-output distillation subsystem.

## Evidence inventory

| Evidence | Inspected surface | Finding |
|---|---|---|
| Package and source snapshot | `pyproject.toml`; 3,606 tracked files at the pinned commit | Python 3.11+ package, version 0.39.0, AGPL-3.0-or-later; a pinned wheel was built for isolated evaluation. |
| Indexing | `packages/core/src/repowise/core/pipeline/full_index.py`, `packages/core/src/repowise/core/ingestion/parser.py` | Provider-free structural indexing persists the data used by later retrieval and analysis. |
| MCP retrieval | `packages/server/src/repowise/server/mcp_server/_server.py`, `packages/server/src/repowise/server/mcp_server/tool_context/context.py`, `packages/server/src/repowise/server/mcp_server/tool_search.py` | The stdio server registers task-shaped context/search and related code-intelligence tools. |
| Output bounds | `packages/server/src/repowise/server/mcp_server/_budget/budgeter.py`, MCP budget/context/search tests | MCP payloads have explicit budgeting and truncation logic with focused unit coverage. |
| Codex integration | `packages/cli/src/repowise/cli/mcp_config.py`, `packages/cli/src/repowise/cli/editor_integrations/codex.py`, `docs/agent/CODEX.md` | Official setup writes project-local MCP configuration, hooks, and managed `AGENTS.md` guidance. |
| Output distillation | `packages/core/src/repowise/core/distill/engine.py`, hook and CLI docs/tests | Supported command output can be compacted and omissions can be expanded, but automatic rewriting is opt-in. |

## Source-logic findings

- `repowise init --yes --provider <codex_cli|opencode> --no-prose` builds the graph, git, health, decision, and structural-wiki state deterministically while binding the provider used by the answer path.
- `repowise mcp` serves the local index over stdio. The default single-repository surface includes repository listing plus overview, context, symbol, search, risk, change-risk, health, why, dead-code, and answer-oriented tools.
- Context retrieval accepts task-oriented targets and selectable enrichment rather than requiring repeated raw-file reads.
- Search combines indexed documentation and code structures; semantic search requires a configured embedder, while the prepared provider-configured profiles retain full-text, structural, and provider-backed answer retrieval.
- MCP response budgeting and truncation bound returned material, while index freshness metadata warns when live `HEAD` diverges from indexed state.
- `repowise init --codex` creates project-local `.codex/config.toml`, `plugins/codex/hooks/hooks.json`, and a managed `AGENTS.md`. The hooks supply lifecycle guidance and stale-index reminders.
- RepoWise documents generic stdio MCP compatibility. The OpenCode profile therefore uses the same pinned local server plus RepoWise-generated `AGENTS.md`; it does not claim an upstream OpenCode-specific installer.
- Command-output distillation is a second token surface. Because its automatic rewrite hook is opt-in, the prepared non-interactive lifecycle profiles do not force-enable it.

## Token-saving mechanism

RepoWise targets repeated exploration cost: it computes code relationships, repository summaries, risk signals, and documentation before the agent asks, then returns bounded task-shaped answers instead of repeated grep and whole-file reads. Its optional distill path targets terminal-output cost by retaining salient output and leaving reversible expansion markers.

Why it may perform well: Lifecycle tasks that require cross-file discovery, caller tracing, architectural orientation, or risk assessment can reuse the warm index and avoid redundant source reads. Generated product guidance and lifecycle hooks may also improve natural uptake in Codex.

Why it may not: small or obvious tasks may not repay indexing and MCP-call overhead; unsupported or partially resolved language relationships can mislead retrieval; stale indexes can require correction work; and OpenCode lacks the richer upstream Codex-specific hook installer. Provider-billed savings also depend on whether the model naturally uses the installed tools.

## Installation and integration behavior

- Canonical package: pinned wheel built from source commit `a3b6714c5523dc7c45d6bce0522035339bcf3afd`, SHA-256 `e7d3068856a45a3d0501b84e6f52db24521512803a07881cdf145da546d932b4`.
- Codex: official structural init with `--provider codex_cli --codex --no-prose`, `REPOWISE_PROVIDER=codex_cli`, project-local MCP config, lifecycle hooks, generated `AGENTS.md`, warm index, runtime binary probe, and MCP initialize/tools-list proof.
- OpenCode: structural init with `--provider opencode --no-prose`, `REPOWISE_PROVIDER=opencode`, generated `AGENTS.md`, isolated host-agnostic stdio MCP registration, warm index, runtime binary probe, and MCP initialize/tools-list proof.
- Model-facing task assistance remains byte-compatible with the matched Lifecycle V1 control; tool use is natural and unforced.
- Generated `.repowise`, `plugins/codex/.mcp.json`, `.codex`, and managed guidance are treatment state and excluded from task-source diffs.

## Runtime behavior

The prepared profiles build a warm structural index before the model session, bind RepoWise's provider explicitly, probe the pinned executable, and prove the stdio MCP initialize and tools-list exchange. During a run, RepoWise serves bounded structural and full-text retrieval from lane-local SQLite state and can use its provider-backed answer path. Codex also receives the product-generated lifecycle hooks; OpenCode receives the generic MCP server and generated `AGENTS.md` guidance.

## Local Lifecycle V1 observation

The provider-backed Codex V2 screen completed both active fixtures with all three tasks and final verifiers passing. Fastify used 5,690,107 provider tokens (+342.03% versus its matched bare-Codex control) and Beets used 2,326,247 (+97.38%); the fresh-input-plus-output deltas were +151.57% and +119.89%. These are single-replicate screening observations, not ranking estimates. The prepared OpenCode protocol has not yet been executed.

## Compatibility notes

RepoWise is a broad retrieval/context authority and overlaps with CodeGraph, jCodeMunch, Serena, SigMap, Graphify, Code Review Graph, CodeScope, and LeanCTX. Run it alone in the individual-tool screen. Its optional command rewriting also overlaps with RTK, Snip, LowFat, and TokenJuice and should not be combined without a separately declared stack protocol.

## Failure modes and limits

The pinned source is alpha-stage software with a large dependency set and local SQLite/index state. Initial indexing adds setup time and disk use. Structural and full-text modes do not require a provider, but model-written prose and semantic embeddings can introduce separate cost, network, and privacy boundaries and are disabled in these prepared runs.

## Evidence boundary

The maintainer reports token, tool-call, latency, and risk-prediction benchmark results in upstream documentation. Those claims remain maintainer evidence: this dossier does not promote them to benchmark-audit or reproduction. Local Codex V2 evidence is retained in the two compact sessions and matched comparisons cited by the evaluation registry; it is a single-replicate screen. OpenCode remains launch-ready but unexecuted. Invalid provider-free runs and protocols are deleted under receipt, and no-provider fallbacks are discarded before registry publication.

## Code-detail inspection findings

### Path drift at this pin

Between the commit this dossier used to describe and the pinned 0.45.0 release, the tree was restructured into a `packages/{cli,core,server}` monorepo. Every path below was cited by the readings in this dossier and no longer resolves as written:

- `packages/cli/src/repowise/cli/mcp_config.py` → `packages/cli/src/repowise/cli/mcp_config.py`
- `packages/core/src/repowise/core/distill/engine.py` → `packages/core/src/repowise/core/distill/engine.py`
- `packages/cli/src/repowise/cli/editor_integrations/codex.py` → `packages/cli/src/repowise/cli/editor_integrations/codex.py`
- `packages/core/src/repowise/core/ingestion/parser.py` → `packages/core/src/repowise/core/ingestion/parser.py`
- `packages/server/src/repowise/server/mcp_server/_budget/budgeter.py` → `packages/server/src/repowise/server/mcp_server/_budget/budgeter.py`
- `packages/server/src/repowise/server/mcp_server/_server.py` → `packages/server/src/repowise/server/mcp_server/_server.py`
- `packages/core/src/repowise/core/pipeline/full_index.py` → `packages/core/src/repowise/core/pipeline/full_index.py`
- `packages/server/src/repowise/server/mcp_server/tool_context/context.py` → `packages/server/src/repowise/server/mcp_server/tool_context/context.py`
- `packages/server/src/repowise/server/mcp_server/tool_search.py` → `packages/server/src/repowise/server/mcp_server/tool_search.py`
- `plugins/codex/.mcp.json` → `plugins/codex/.mcp.json` (a shipped plugin template in the source tree; not the file an installer writes into a target repository)
- `plugins/codex/hooks/hooks.json` → `plugins/codex/hooks/hooks.json` (likewise a shipped template)
- `.codex/config.toml` — removed: no file of that name exists anywhere in this release

The paths are corrected here; the **behavioural claims attached to them were not re-verified** against the pinned release. A file that moved during a restructure can also have changed what it does, so treat those specific readings as carried over from the older commit rather than as current source-logic evidence.
