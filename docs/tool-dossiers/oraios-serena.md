# Tool dossier: oraios/serena

## Identity

- Repository: `oraios/serena`
- URL: https://github.com/oraios/serena
- Version/ref inspected: local shallow clone `103a17072e9b`, 2026-07-01
- Snapshot status: pinned-commit
- Commit inspected: 103a17072e9b915c9c9980f946902be856695978
- Commit URL: https://github.com/oraios/serena/commit/103a17072e9b915c9c9980f946902be856695978
- Source artifact path: `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json`
- Date inspected: 2026-07-01
- Evidence stage: source-logic (fresh pinned shallow clone; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection: 25,797
- Forks at inspection: 1,717
- License: MIT
- Updated at: 2026-06-26T07:03:50Z

## Summary

Serena is an MCP toolkit providing code retrieval and editing capabilities using language-server style project understanding. It is a possible code-retrieval authority in token-saving stacks.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` | Used to identify installer, plugin, MCP, test, and benchmark paths beyond README. |
| README/docs | README path identified when present. | README claims require source and benchmark follow-up. |
| Installer/config/plugin files | Paths identified below. | Integration review started. |
| Runtime source | Representative implementation files inspected; see code-detail section. | Source-logic review is recorded for representative modules; uninspected modules remain benchmark-audit/reproduction follow-up. |
| Tests/benchmarks | Representative tests or metrics files inspected where available. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 961 files and 888 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/workflows/pytest.yml`
- `.github/workflows/test-parallel.yml`
- `AGENTS.md`
- `docs/.gitignore`
- `docs/01-about/.gitignore`
- `docs/01-about/020_programming-languages.md`
- `docs/01-about/030_serena-in-action.md`
- `docs/01-about/050_acknowledgements.md`
- `docs/02-usage/000_intro.md`
- `docs/02-usage/010_installation.md`
- `docs/02-usage/020_running.md`
- `docs/02-usage/025_jetbrains_plugin.md`
- `docs/02-usage/030_clients.md`
- `docs/02-usage/040_workflow.md`
- `docs/02-usage/045_memories.md`
- `docs/02-usage/050_configuration.md`
- `docs/02-usage/060_dashboard.md`
- `docs/02-usage/065_logs.md`
- `docs/02-usage/070_security.md`
- `docs/02-usage/999_additional-usage.md`
- `docs/03-special-guides/000_intro.md`
- `docs/03-special-guides/cpp_setup.md`
- `docs/03-special-guides/custom_agent.md`
- `docs/03-special-guides/godot_gdscript_setup_guide_for_serena.md`
- `docs/03-special-guides/groovy_setup_guide_for_serena.md`
- `docs/03-special-guides/ocaml_setup_guide_for_serena.md`
- `docs/03-special-guides/scala_setup_guide_for_serena.md`
- `docs/03-special-guides/serena_on_chatgpt.md`
- `docs/03-special-guides/unreal_engine_setup_guide_for_serena.md`
- `docs/04-evaluation/000_evaluation-intro.md`
- `docs/04-evaluation/010_methodology.md`
- `docs/04-evaluation/020_prompts/000_prompts.md`
- `docs/04-evaluation/020_prompts/010_evaluation-prompt.md`
- `docs/04-evaluation/020_prompts/020_summary-prompt.md`
- `docs/04-evaluation/030_results/000_evaluation-results.md`
- `docs/04-evaluation/030_results/010_cc_on_tianshou.md`
- `docs/04-evaluation/030_results/020_codex_on_jbplugin.md`
- `docs/04-evaluation/030_results/030_copilot_cli_on_ente.md`
- `docs/04-evaluation/030_results/040_glm_on_tianshou.md`



## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`.

### Fresh pinned-source refresh

The 2026-07-01 refresh pins the inspected source to `103a17072e9b915c9c9980f946902be856695978` and records a fresh tree plus selected implementation excerpts in `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` and `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`. Representative files captured for this refresh include `AGENTS.md`, `docs/01-about/020_programming-languages.md`, `docs/01-about/030_serena-in-action.md`, `docs/01-about/050_acknowledgements.md`, `docs/02-usage/000_intro.md`, `docs/02-usage/010_installation.md`. Treat benchmark, savings, and deployment claims below as source-logic only unless a benchmark-audit or reproduction artifact is explicitly cited.
 The artifact contains raw GitHub file paths, byte sizes, SHA-256 prefixes, and behavior-line excerpts from the inspected implementation files.

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
