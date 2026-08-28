# Tool dossier: chopratejas/headroom

## Identity

- Repository: `chopratejas/headroom`
- URL: https://github.com/chopratejas/headroom
- Version/ref inspected: `0.36.3` release at commit `87e71dd10057ff3cbe826bde617682971339e4f8`, pinned batch release corpus, 2026-08-28
- Snapshot status: pinned-commit
- Commit inspected: 87e71dd10057ff3cbe826bde617682971339e4f8
- Commit URL: https://github.com/chopratejas/headroom/commit/87e71dd10057ff3cbe826bde617682971339e4f8
- Source artifact path: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`
- Date inspected: 2026-08-28
- Evidence stage: source-logic (pinned 0.36.3 release checkout from the batch release corpus, the same bytes its lanes install; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection (2026-07-01, not refreshed offline): 51,329
- Forks at inspection (2026-07-01, not refreshed offline): 3,642
- License: Apache-2.0
- Updated at (2026-07-01, not refreshed offline): 2026-06-26T07:44:25Z

## Summary

Headroom is a broad compression layer for tool outputs, logs, files, RAG chunks, conversation/history, and agent/app traffic. It can act as a compression owner across multiple integration modes.

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

Tree inspection of the pinned `0.36.3` release checkout found 2311 files: 1759 source, 147 documentation, 1209 test/benchmark, and 426 matching installer, host-integration, hook, plugin, skill, MCP, or configuration patterns.

Integration code — what actually performs a host install, and therefore what an install protocol must be written against:

- `claude_analysis_ttl.py`
- `crates/headroom-core/src/transforms/pipeline/config.rs`
- `crates/headroom-core/src/transforms/smart_crusher/config.rs`
- `crates/headroom-core/src/transforms/text_crusher/config.rs`
- `crates/headroom-proxy/src/config.rs`
- `crates/headroom-simulators/src/config.rs`
- `docs/next.config.mjs`
- `docs/postcss.config.mjs`
- `docs/source.config.ts`
- `e2e/__init__.py`
- `e2e/_lib/__init__.py`
- `e2e/init/run.py`
- `examples/langchain_demo/__init__.py`
- `examples/mcp_demo/__init__.py`
- `examples/mcp_demo/mock_mcp_servers.py`
- `examples/mcp_demo/run_agent_eval.py`
- `examples/mcp_demo/show_before_after.py`
- `examples/mcp_demo/show_compression.py`
- `headroom/__init__.py`
- `headroom/agent_savings.py`
- `headroom/audit/__init__.py`
- `headroom/audit/codex.py`
- `headroom/backends/__init__.py`
- `headroom/cache/__init__.py`
- `headroom/cache/backends/__init__.py`
- `headroom/capture/__init__.py`
- `headroom/ccr/__init__.py`
- `headroom/ccr/mcp_http.py`

Host-integration documentation shipped in the release:

- `docs/claude-code-bedrock-headroom.md`
- `docs/content/docs/agent-orchestration.mdx`
- `docs/content/docs/claude-code-azure-foundry.mdx`
- `docs/content/docs/claude-code-vertex.mdx`
- `docs/content/docs/codex-recovery.mdx`
- `docs/content/docs/configuration.mdx`
- `docs/content/docs/docker-install.mdx`
- `docs/content/docs/installation.mdx`
- `docs/content/docs/mcp.mdx`
- `docs/content/docs/opencode-deepseek.mdx`
- `docs/content/docs/opencode.mdx`
- `docs/content/docs/persistent-installs.mdx`
- `docs/content/docs/vscode-claude-code.mdx`
- `examples/deployment/macos-launchagent/README.md`


## Code-detail inspection findings

### Path drift at this pin

Between the commit this dossier used to describe and the pinned 0.36.3 release, one cited component was removed outright. Every path below was cited by the readings in this dossier and no longer resolves as written:

- `agent-evals/src/agent_evals/metrics/savings.py` — removed: the whole `agent-evals` subproject is absent from this release; the nearest surviving code is `headroom/cli/savings.py`, which is a different component

The paths are corrected here; the **behavioural claims attached to them were not re-verified** against the pinned release. A file that moved during a restructure can also have changed what it does, so treat those specific readings as carried over from the older commit rather than as current source-logic evidence.

### Pinned-release refresh (2026-08-28)

This dossier previously described `715ed7d200cb`, read from GitHub HEAD on 2026-07-01. That is not the code any lane runs. `BATCH_RELEASES` pins this tool to the **0.36.3** release at `87e71dd10057`, and the runner rewrites every lane path onto it, so the reading below is now taken from that pinned checkout instead. Inspecting the corpus checkout rather than a fresh network fetch keeps the reading reproducible after upstream HEAD moves again.

Upstream shipped **11 releases** between 2026-07-01 and this pin (`CHANGELOG.md`). A protocol derived from the older reading is how the 2026-08-22 review found five drifts and one blocking defect, so any integration step below is worth re-checking against the pinned release rather than trusted.

This project's changelog headings carry no descriptive titles, so which of those releases touched an install surface cannot be read off the headings. The most recent are:

- [0.36.3](https://github.com/headroomlabs-ai/headroom/compare/v0.36.2...v0.36.3) (2026-08-21)
- [0.36.2](https://github.com/headroomlabs-ai/headroom/compare/v0.36.1...v0.36.2) (2026-08-21)
- [0.36.1](https://github.com/headroomlabs-ai/headroom/compare/v0.36.0...v0.36.1) (2026-08-20)
- [0.36.0](https://github.com/headroomlabs-ai/headroom/compare/v0.35.0...v0.36.0) (2026-08-20)
- [0.35.0](https://github.com/headroomlabs-ai/headroom/compare/v0.34.0...v0.35.0) (2026-08-12)
- [0.34.0](https://github.com/headroomlabs-ai/headroom/compare/v0.33.0...v0.34.0) (2026-08-05)
- [0.33.0](https://github.com/headroomlabs-ai/headroom/compare/v0.32.0...v0.33.0) (2026-07-29)
- [0.32.0](https://github.com/headroomlabs-ai/headroom/compare/v0.31.0...v0.32.0) (2026-07-17)
- …and 3 further releases; see `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.

The official install guide this tool is evaluated against is `source/README.md` at sha256 `fee6ad17c8df5d69…` in the pinned release.

Evidence artifact: `sources/discovery/2026-08-28-batch-pinned-dossier-refresh.json`.


- `crates/headroom-core/src/transforms/pipeline/orchestrator.rs` implements a compression pipeline combining reformat and offload transforms, tracking `steps_applied`, `bytes_saved`, and `cache_keys`.
- The orchestrator comments and code emphasize fail-open behavior: transform failures are recorded/skipped and the pipeline must return some output rather than panic inside a tool-call response path.
- `crates/headroom-core/src/transforms/pipeline/traits.rs` defines reformat and offload transform boundaries. Its CCR model assumes dropped pieces can be retrieved through a cache-backed tool call, so offload transforms have stronger state/correctness implications than simple truncation.
- `crates/headroom-proxy/src/compression/mod.rs` owns compressible-path classification and provider-specific dispatchers for Anthropic/OpenAI-shaped requests.
- `crates/headroom-proxy/src/proxy.rs` implements reverse-proxy routing, compression policy, cache stabilization, provider auth boundaries, and structured failure behavior.
- `agent-evals/src/agent_evals/metrics/savings.py` parses per-response `x-headroom-*` token headers and separates those from run-level `/stats` aggregates.

### Implementation-level limits

- Headroom is a broad compression/proxy owner; combining it with other broad compressors risks duplicate compression, cache mismatch, or retrieval indirection.
- CCR/offload behavior depends on retrievable cache state; privacy, eviction, and recovery behavior require deeper review before sensitive deployment.
- Savings claims should separate per-request token headers from run-level cache effects and task success metrics.

## Installation and integration behavior

- Tool type: Compression/proxy/MCP tool
- Primary intervention surface: Broad context compression through library, proxy, agent wrapper, and MCP modes
- Integration status: documented integration paths and/or source locations were identified, but exact runtime behavior has not yet been fully reviewed.
- Disable/uninstall path: requires follow-up inspection of installer/plugin code and documentation.
- Failure behavior if dependency is missing: partially inspected in representative files; complete deployment failure-mode review remains open.

## Runtime behavior

- Intervention surface: Broad context compression through library, proxy, agent wrapper, and MCP modes
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Broad context compression through library, proxy, agent wrapper, and MCP modes
- Reduction method: identified from representative implementation files; full benchmark/reproduction review remains open.
- Quality-preservation mechanism: partially identified from representative source where present; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: depends on turn count, prompt caching, failure/retry behavior, and whether the tool changes agent workflow length.

## Benchmarks and claims

| Claim | Source | Measurement scope | Reviewed method | Caveats |
|---|---|---|---|---|
| Token-saving or context-reduction claims exist or are implied by repository description/metadata. | Repository metadata, existing catalog records, and pinned source-logic refresh. | Varies by tool. | Reviewed at source-logic level through representative implementation files; not benchmark-audited or reproduced. | Maintainer claims must not be treated as reproduced evidence. |

## Compatibility notes

Should generally be the only broad compression owner in a stack. It can conflict with RTK, LeanCTX proxy compression, TokenTamer, Kompact, or other output/context compressors unless a specific combination is tested.

Compatibility-safe stack selection means the tools should not fight over the same hook, context surface, retrieval authority, memory authority, proxy, or output channel.

## Failure modes and limits

- Compression may require extra turns or retrieval calls, offsetting per-request savings.
- Proxy/wrap modes introduce provider transport and configuration risk.
- Raw-content cache and retrieval behavior must be inspected before sensitive deployments.

## Open questions and next review tasks

- [ ] Inspect compression pipeline and CCR/raw retrieval implementation.
- [ ] Inspect provider wrapper/proxy behavior for Claude and Codex.
- [ ] Review agent-evals and benchmark scoring/token accounting.
- [ ] Check whether raw cache is local-only and how it is evicted.
