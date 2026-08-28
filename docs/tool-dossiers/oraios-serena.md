# Tool dossier: oraios/serena

## Identity

- Repository: `oraios/serena`
- URL: https://github.com/oraios/serena
- Version/ref inspected: `1.7.0` release at commit `949a27ef1e5fda1a6e7b561e777bcece345c6ffd`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: 949a27ef1e5fda1a6e7b561e777bcece345c6ffd
- Commit URL: https://github.com/oraios/serena/commit/949a27ef1e5fda1a6e7b561e777bcece345c6ffd
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 1.7.0 release checkout from the batch release corpus, the same bytes its lanes install; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection (2026-07-01, not refreshed offline): 25,797
- Forks at inspection (2026-07-01, not refreshed offline): 1,717
- License: MIT
- Updated at (2026-07-01, not refreshed offline): 2026-06-26T07:03:50Z

## Summary

Serena is an MCP toolkit providing code retrieval and editing capabilities using language-server style project understanding. It is a possible code-retrieval authority in token-saving stacks.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json` | Used to identify installer, plugin, MCP, test, and benchmark paths beyond README. |
| README/docs | README path identified when present. | README claims require source and benchmark follow-up. |
| Installer/config/plugin files | Paths identified below. | Integration review started. |
| Runtime source | Representative implementation files inspected; see code-detail section. | Source-logic review is recorded for representative modules; uninspected modules remain benchmark-audit/reproduction follow-up. |
| Tests/benchmarks | Representative tests or metrics files inspected where available. | Full benchmark-method review remains open. |

## Initial source-structure finding

Tree inspection of the pinned `1.7.0` release checkout found 1048 files: 471 source, 61 documentation, 719 test/benchmark, and 136 matching installer, host-integration, hook, plugin, skill, MCP, or configuration patterns.

Integration code — what actually performs a host install, and therefore what an install protocol must be written against:

- `scripts/agno_agent.py`
- `scripts/mcp_server.py`
- `src/interprompt/__init__.py`
- `src/interprompt/util/__init__.py`
- `src/serena/__init__.py`
- `src/serena/agent.py`
- `src/serena/config/__init__.py`
- `src/serena/config/client_setup.py`
- `src/serena/config/context_mode.py`
- `src/serena/config/serena_config.py`
- `src/serena/hooks.py`
- `src/serena/jetbrains/jetbrains_plugin_client.py`
- `src/serena/mcp.py`
- `src/serena/tools/__init__.py`
- `src/serena/tools/config_tools.py`
- `src/solidlsp/__init__.py`
- `src/solidlsp/initialize_params.py`
- `src/solidlsp/language_servers/elixir_tools/__init__.py`
- `src/solidlsp/ls_config.py`

Host-integration documentation shipped in the release:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/02-usage/010_installation.md`
- `docs/02-usage/025_jetbrains_plugin.md`
- `docs/02-usage/030_clients.md`
- `docs/02-usage/050_configuration.md`


## Code-detail inspection findings

### Pinned-release refresh (2026-08-28)

This dossier previously described `103a17072e9b`, read from GitHub HEAD on 2026-07-01. That is not the code any lane runs. `BATCH_RELEASES` pins this tool to the **1.7.0** release at `949a27ef1e5f`, and the runner rewrites every lane path onto it, so the reading below is now taken from that pinned checkout instead. Inspecting the corpus checkout rather than a fresh network fetch keeps the reading reproducible after upstream HEAD moves again.

Upstream shipped **3 releases** between 2026-07-01 and this pin (`CHANGELOG.md`). A protocol derived from the older reading is how the 2026-08-22 review found five drifts and one blocking defect, so any integration step below is worth re-checking against the pinned release rather than trusted.

This project's changelog headings carry no descriptive titles, so which of those releases touched an install surface cannot be read off the headings. The most recent are:

- v1.7.0 (2026-08-09)
- v1.6.1 (2026-07-21)
- v1.6.0 (2026-07-16)

The official install guide this tool is evaluated against is `source/docs/02-usage/030_clients.md` at sha256 `62b271277e5ba778…` in the pinned release.

Evidence artifact: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.


- `src/serena/mcp.py` wraps Serena tools into FastMCP tools, builds schemas from tool metadata, and includes OpenAI-tool schema sanitization when needed.
- `src/serena/agent.py` manages the exposed tool set, project activation, language-server manager, modes, and memory/tool availability boundaries.
- `src/serena/tools/symbol_tools.py` implements language-server-backed symbolic read/edit tools such as symbol overviews with `max_answer_chars` limits for output control.
- `src/serena/tools/file_tools.py` implements file reads, directory listing, and edits with output-length limiting and diagnostics contexts for edits.
- `src/serena/ls_manager.py` creates and manages SolidLSP language servers per language, so retrieval quality depends on language-server setup and project-language support.

### Implementation-level limits

- Serena is a retrieval/editing authority, not merely a passive search index; stack compatibility must account for editing tools and diagnostics behavior.
- Language-server quality and setup determine retrieval reliability.
- It should not be combined casually with CodeGraph, Token Savior retrieval, or LeanCTX code graph without testing duplicate/contradictory retrieval behavior.

## Installation and integration behavior

- Tool type: MCP retrieval/editing tool
- Primary intervention surface: MCP-based semantic code retrieval and editing toolkit
- Integration status: documented integration paths and/or source locations were identified, but exact runtime behavior has not yet been fully reviewed.
- Disable/uninstall path: requires follow-up inspection of installer/plugin code and documentation.
- Failure behavior if dependency is missing: partially inspected in representative files; complete deployment failure-mode review remains open.

## Runtime behavior

- Intervention surface: MCP-based semantic code retrieval and editing toolkit
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: MCP-based semantic code retrieval and editing toolkit
- Reduction method: identified from representative implementation files; full benchmark/reproduction review remains open.
- Quality-preservation mechanism: partially identified from representative source where present; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: depends on turn count, prompt caching, failure/retry behavior, and whether the tool changes agent workflow length.

## Benchmarks and claims

| Claim | Source | Measurement scope | Reviewed method | Caveats |
|---|---|---|---|---|
| Token-saving or context-reduction claims exist or are implied by repository description/metadata. | Repository metadata, existing catalog records, and pinned source-logic refresh. | Varies by tool. | Reviewed at source-logic level through representative implementation files; not benchmark-audited or reproduced. | Maintainer claims must not be treated as reproduced evidence. |

## Compatibility notes

Use as one code retrieval/editing authority. It conflicts with CodeGraph, Token Savior retrieval, LeanCTX code graph, or other code-index MCP servers when multiple tools return overlapping context.

Compatibility-safe stack selection means the tools should not fight over the same hook, context surface, retrieval authority, memory authority, proxy, or output channel.

## Failure modes and limits

- Language-server quality varies by language and project setup.
- Editing tools can create behavior beyond read-only retrieval; safety and rollback behavior require inspection.
- Multiple retrieval authorities can duplicate context or disagree.

## Open questions and next review tasks

- [ ] Inspect MCP server tool schemas and language-server adapters.
- [ ] Inspect project indexing and symbol lookup behavior.
- [ ] Review tests for editing safety and failure behavior.
- [ ] Compare against CodeGraph on architecture, implementation, and edit tasks.
