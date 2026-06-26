# Tool dossier: chopratejas/headroom

## Identity

- Repository: `chopratejas/headroom`
- URL: https://github.com/chopratejas/headroom
- Version/ref inspected: GitHub `HEAD` tree via API, 2026-06-26
- Date inspected: 2026-06-26
- Review level: 3-source-behavior (representative core pipeline, proxy, and savings metrics inspected)
- Stars at inspection: 51,329
- Forks at inspection: 3,642
- License: Apache-2.0
- Updated at: 2026-06-26T07:44:25Z

## Summary

Headroom is a broad compression layer for tool outputs, logs, files, RAG chunks, conversation/history, and agent/app traffic. It can act as a compression owner across multiple integration modes.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-06-26-five-more-tool-source-structures.json` | Used to identify installer, plugin, MCP, test, and benchmark paths beyond README. |
| README/docs | README path identified when present. | README claims require source and benchmark follow-up. |
| Installer/config/plugin files | Paths identified below. | Integration review started. |
| Runtime source | Representative implementation files inspected; see code-detail section. | Source-behavior review has started and should continue across remaining modules. |
| Tests/benchmarks | Representative tests or metrics files inspected where available. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 3,427 files and 2,479 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `.github/ISSUE_TEMPLATE/copilot-subscription-test-report.md`
- `Cargo.toml`
- `REALIGNMENT/11-phase-I-test-infra.md`
- `TESTING-copilot-subscription.md`
- `agent-evals/.gitignore`
- `agent-evals/Makefile`
- `agent-evals/README.md`
- `agent-evals/pyproject.toml`
- `agent-evals/src/agent_evals/__init__.py`
- `agent-evals/src/agent_evals/arms.py`
- `agent-evals/src/agent_evals/benchmarks/__init__.py`
- `agent-evals/src/agent_evals/cli.py`
- `agent-evals/src/agent_evals/config.py`
- `agent-evals/src/agent_evals/harnesses/__init__.py`
- `agent-evals/src/agent_evals/judge/__init__.py`
- `agent-evals/src/agent_evals/logging.py`
- `agent-evals/src/agent_evals/manifest.py`
- `agent-evals/src/agent_evals/metrics/__init__.py`
- `agent-evals/src/agent_evals/metrics/savings.py`
- `agent-evals/src/agent_evals/models.py`
- `agent-evals/src/agent_evals/orchestrator.py`
- `agent-evals/src/agent_evals/probes/__init__.py`
- `agent-evals/src/agent_evals/protocols.py`
- `agent-evals/src/agent_evals/report/__init__.py`
- `agent-evals/src/agent_evals/report/scorecard.py`
- `agent-evals/src/agent_evals/stats/__init__.py`
- `agent-evals/tests/__init__.py`
- `agent-evals/tests/conftest.py`
- `agent-evals/tests/test_arms.py`
- `agent-evals/tests/test_config.py`
- `agent-evals/tests/test_integration_phase0.py`
- `agent-evals/tests/test_live_integration.py`
- `agent-evals/tests/test_manifest.py`
- `agent-evals/tests/test_models.py`
- `agent-evals/tests/test_orchestrator.py`
- `agent-evals/tests/test_savings.py`
- `agent-evals/tests/test_scorecard.py`
- `benchmarks/__init__.py`
- `benchmarks/adversarial_ccr_tests.py`
- `benchmarks/agent_cost_benchmark.py`



## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-06-26-five-more-tool-code-inspection.json`. The artifact contains raw GitHub file paths, byte sizes, SHA-256 prefixes, and behavior-line excerpts from the inspected implementation files.

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
- Failure behavior if dependency is missing: requires source-behavior review.

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
- Reduction method: identified at mechanism level; implementation details require source-behavior review.
- Quality-preservation mechanism: requires source and benchmark review.
- Cases where savings may not translate to provider-billed reductions: depends on turn count, prompt caching, failure/retry behavior, and whether the tool changes agent workflow length.

## Benchmarks and claims

| Claim | Source | Measurement scope | Reviewed method | Caveats |
|---|---|---|---|---|
| Token-saving or context-reduction claims exist or are implied by repository description/metadata. | Repository metadata and existing catalog records. | Varies by tool. | Not yet reviewed beyond source-tree and metadata inspection in this dossier. | Maintainer claims must not be treated as reproduced evidence. |

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

