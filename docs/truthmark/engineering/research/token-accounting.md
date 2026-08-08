---
status: active
truth_kind: engineering-contract
doc_type: contract
source_of_truth:
  - ../../../../data/workflow-sessions.json
  - ../../../../scripts/run_codex_workflow_evaluation.py
last_reviewed: 2026-08-08
---

# Token Accounting And Evaluation Contracts

## Purpose

Define the production estimand and separate experiment validity from sampled model quality.

## Scope

This contract governs active Lifecycle V1 provider-token samples, retained lifecycle-v0 baseline reuse, compatible treatment comparisons, and exclusion/rerun boundaries.

## Current Implementation Behavior

- The active portfolio contains the Fastify and Beets Lifecycle V1 sequences. Terraform's owner-declared-invalid V1 r0 was removed under an invalidation receipt and has no active rerun or treatment path.
- Lifecycle V1 tasks seed authentic semantic regressions, require agents to complete normal software-engineering objectives correctly, and permit repository discovery without exposing controller scoring.
- Controller-only component compilation gates per-task acceptance; a controller-only frozen project-wide compile command gates final workflow acceptance and treatment unlock. Tests, behavior, style, maintainability, exact source shape, and source review remain diagnostic. This internal boundary is never included in agent instructions.
- The runner captures cumulative provider usage across one persistent sequential agent session.
- Codex usage comes from provider-reported Codex JSONL snapshots. OpenCode usage comes from unique incremental `step_finish` parts; fresh input, cache read, cache write, visible output, and reasoning are normalized without counting reasoning twice.
- Replacement-runtime protocols may bind distinct runtime-specific model-condition IDs while holding provider, model, reasoning effort, fixtures, prompts, and baseline pool fixed. The frozen protocol identifies the Codex baseline condition and replacement-runtime treatment condition separately.
- OpenCode/OpenRouter Sol/high is a separately frozen, provider-free Lifecycle V1 control configuration. It has its own OpenRouter model namespace and baseline pool; it is neither a Codex-provider control nor a cross-provider token-treatment comparison. A provider-backed run remains blocked until a separate bounded authorization binds protocol hashes and a spend budget.
- Direct-Anthropic Claude Code has two completed separate conditions: `claude-code-anthropic-sonnet-5-high` binds Claude Code 2.1.220, `claude-sonnet-5`, and `high` effort for 897,108.2 weighted units; `claude-code-anthropic-opus-5-high` binds the same runtime, `claude-opus-5`, and `high` effort for 1,167,276.7 weighted units. Opus used 30.12% more weighted token cost than Sonnet, and Sonnet was already 73.85% above matched Codex and 22.71% above matched OpenCode weighted baselines, so Sonnet is the selected model for treatment experiments. Both use first-party transport without OpenRouter across six task turns; the owner account is materialized only into a lane-private `CLAUDE_CONFIG_DIR` through `TOKEN_EVAL_CLAUDE_ACCOUNT_HOME`. Provider-free qualification now covers all 30 native Sonnet treatment lanes for 15 profiles, and the serialized treatment matrix is separately owner-authorized; SDL-MCP remains excluded for its Codex-only installer surface.
- Claude Code invocations bind `--model`, `--effort`, and a strict lane-private MCP configuration when the treatment declares an MCP server. Direct-account preflight records non-secret authentication status and rejects OpenRouter endpoints/status, and Claude stream-json usage remains subject to the existing provider-reported extraction contract.
- After each successful direct-account Claude task, the runner atomically carries a changed lane-private `.credentials.json` back to the explicitly supplied account home and records a path-redacted sync receipt. Failed Claude tasks never overwrite the source credential snapshot; direct-Anthropic production matrices remain serialized so separate lanes cannot race the account refresh state.
- The matrix reuses the first operationally valid baseline for a causal comparison fingerprint and replicate.
- Direct-Anthropic Claude Code treatment matrices reuse the accepted same-condition Claude baseline pool; they do not fall back to the canonical Codex pool.
- Direct-Anthropic Sonnet treatment lanes reserve an immutable per-sequence/profile attempt receipt before provider work. The first matrix retained Fastify/RTK at 2,110,452 provider tokens (331,508.9 weighted units); Fastify/Cartog reached the provider but failed authentication with zero tokens, remains occupied, and is excluded from registry and aggregate claims. Remaining lanes require refreshed credentials and cannot reuse the occupied Cartog identity.
- Repository validation requires complete provider usage, structural isolation, clean execution integrity, and recoverable compact evidence—not verifier success or source review.
- Before any non-baseline provider launch, both repository validation and the direct runner require exact parity approval plus a current provider-free qualification receipt for every active fixture/profile protocol binding; MCP profiles additionally require non-empty `tools/list` proof.
- Canonical treatment profiles install every author-recommended Codex surface, including product-authored guidance, native skills/plugins, and reviewed hooks; reduced or prompt-emulated setups are ablations or invalid assignments, not product treatments.
- The historical shared-runner qualification covered 45 fixture/profile bindings across 15 profiles with zero provider calls; those receipts do not authorize Lifecycle V1 treatments.
- Thirty-eight provider-backed baseline records are retained under earlier frozen contracts; Fastify and Beets additionally retain one accepted Lifecycle V1 r0 pilot each, while the owner-declared-invalid Terraform V1 r0 was removed under its invalidation receipt.

## Product Truth Links

- None. This is an engineering research evidence contract.

## Contract Surface

- `data/workflow-task-sequences.json`
- `data/workflow-sessions.json`
- `scripts/run_codex_workflow_evaluation.py`
- `scripts/run_opencode_openrouter_workflow_model_condition.py`
- `scripts/extract_claude_code_usage.py`
- `scripts/opencode_workflow_adapter.py`
- `scripts/extract_opencode_usage.py`
- `scripts/validate_repository.py`
- `scripts/workflow_model_condition_runtime.py`
- `scripts/prepare_pinned_codex_marketplace.py`
- `scripts/trust_codex_plugin_hooks.py`
- `scripts/install_jcodemunch_codex_guidance.py`
- `scripts/run_sequential_workflow_matrix.py`
- `scripts/validate_repository.py`

## Inputs

Frozen causal protocol identity, provider usage events, prompt execution status, isolation/integrity audits, and compact artifacts.

## Outputs

Retained baseline/treatment token samples and compatible provider-token comparisons with model-quality diagnostics attached.

## Primary Objective

The repository measures cumulative provider-reported workflow tokens under fair, frozen lifecycle-v0 tasks. It does not evaluate model performance and does not estimate monetary cost.

## Contract

- Qualification proves fixture mechanics and discrimination; it is not a model result.
- A future treatment candidate is provider-runnable only when the parity audit's approved profile set exactly matches the fixture registry and every active fixture/profile pair has one current protocol plus a protocol-hash-matched, provider-free preparation receipt. Configuration listing alone is not assignment proof.
- Each active sequence is ordered as feature implementation, behavior-preserving refactor, and code review/correction.
- A production lane resets repository/profile/tool/agent state before execution, preserves warm state between prompts, and records the complete provider-reported token total.
- The first operationally complete, integrity-valid provider run for a causal protocol fingerprint and replicate is the retained token sample.
- An attempted paid lane remains occupied even when provider execution fails or strict compact ingress rejects the result; its immutable attempt receipt prevents a silent rerun under the same identity.
- Lifecycle V1 compile outcomes gate task/workflow acceptance and treatment unlock, but not token-sample retention. Broader test, behavior, style, exact-source, and source-review diagnostics do not trigger reruns.
- Never rerun because the model failed a verifier, produced imperfect code, or received a low review score.
- Rerun only for experiment invalidity or incompleteness: fixture/verifier defect, wrong controller assets, corrupt/missing usage, failed isolation/integrity, or incomplete prompt execution.
- Baseline/treatment comparisons require matching fixture, sequence, provider, model, reasoning effort, causal comparison fingerprint, and replicate. Runtime/model-condition IDs must also match unless the frozen profile is explicitly a replacement-runtime treatment; in that case the runtime difference is the experimental variable and both condition IDs are frozen separately.
- Report absolute provider-token totals with percentage changes.
- Treatment installation/configuration is valid treatment exposure; observed use may be zero and remains descriptive.
- OpenCode automatic-plugin activation and model-issued product-tool uptake are reported separately. A loaded automatic plugin may validly record zero model-issued product calls; an exposed MCP surface with zero selected calls is also a valid natural-use result.
- A prompt/verifier/fixture defect is attributed to the fixture, not the model.

## Token Component Contract

Every normalized provider usage record must preserve these dimensions:

```text
fresh_input_tokens  = provider non-cache input_tokens
                    + provider cache-creation input tokens
cached_input_tokens = provider cache-read input tokens
cache_write_tokens  = cache-creation input tokens (an explicit audit subset of fresh input)
output_tokens       = provider output tokens, including any reasoning output
reasoning_tokens    = reasoning-token subset when the provider reports it; otherwise exact zero with availability recorded

total_provider_tokens = fresh_input_tokens + cached_input_tokens + output_tokens
```

`cache_write_tokens` must never be added to `total_provider_tokens` a second time. The secondary comparison metric is:

```text
weighted_tokens = fresh_input_tokens + 0.1 × cached_input_tokens + 6 × output_tokens
```

For Claude/Anthropic usage, `fresh_input_tokens` is specifically `input_tokens + cache_creation_input_tokens`, while `cache_read_input_tokens` remains cached input. Nested cache-creation categories such as ephemeral five-minute and one-hour fields must be retained and summed without counting a parent aggregate twice. Claude assistant-message usage blocks are authoritative when they contain complete nonzero provider usage; the observed Claude Code/OpenRouter stream can instead expose complete per-task usage only on the final `result` event, which is accepted as a distinct warned fallback source when its cache and output dimensions are present. Zero-valued assistant blocks with null cache dimensions are not treated as authoritative. All numeric provider fields whose names contain `token` are retained in `provider_usage_details`, including fields not currently used by the normalized arithmetic. A session remains invalid for token comparison when the extractor cannot produce a complete provider-usage record from the available events; that applies equally to the older assistant-only path and to any fallback path that cannot be reconciled to the provider stream.

## Token Eligibility And Missing Evidence

A provider-backed session is not eligible for token comparison when its usage source, cache dimensions, raw token-bearing details, or arithmetic cannot be verified. Missing raw usage cannot be converted to zero. Such a session remains retained for execution evidence but must be excluded from the primary token comparison with an explicit `invalid-accounting` disposition. Corrected totals require surviving raw usage evidence or a newly authorized run; they must never be inferred from compact records that omitted a token dimension.

## Compatibility Rules

Full runner and validator hashes remain frozen provenance. Reporting, registry, validator, and post-run classification changes do not split a comparison pool when causal/model-visible execution inputs and `runner_contract_version` are unchanged.

## Evidence

Compact sessions retain `run.json`, `changes.diff`, `evidence.jsonl.gz`, and `manifest.sha256`. Structured verifier outcomes and optional quality reviews are preserved without selecting which token samples count.

## Maintenance Notes

Update this document whenever token eligibility, comparison identity, provider accounting, or invalidity boundaries change. Do not reintroduce model-performance gates into token-sample eligibility.

## Source References

- ../../../../data/workflow-task-sequences.json
- ../../../../data/workflow-sessions.json
- ../../../../docs/evaluations/operations/runbook.md
- ../../../../docs/evaluations/design/token-and-quality-policy.md
- ../../../../scripts/run_codex_workflow_evaluation.py
- ../../../../scripts/run_sequential_workflow_matrix.py
- ../../../../scripts/run_opencode_openrouter_workflow_model_condition.py
- ../../../../scripts/extract_claude_code_usage.py
- ../../../../scripts/opencode_workflow_adapter.py
- ../../../../scripts/extract_opencode_usage.py
- ../../../../scripts/workflow_model_condition_runtime.py
- ../../../../data/evaluation-agent-runtimes.json
- ../../../../data/evaluation-profiles.json
- ../../../../sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-protocol-preparation-20260808.json
- ../../../../sources/evaluations/audits/claude-code-anthropic-opus-5-high-lifecycle-v1-protocol-preparation-20260808.json
- ../../../../sources/evaluations/audits/claude-code-anthropic-opus-5-high-lifecycle-v1-baseline-authorization-20260808.json
- ../../../../sources/evaluations/audits/corrected-integration-qualification-claude-code-anthropic-sonnet-5-high-lifecycle-v1-20260808.json
- ../../../../sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-treatment-authorization-20260808.json
- ../../../../sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-cartog-fastify-ingress-rejection-20260808.json
- ../../../../scripts/prepare_pinned_codex_marketplace.py
- ../../../../scripts/trust_codex_plugin_hooks.py
- ../../../../scripts/install_jcodemunch_codex_guidance.py
- ../../../../sources/evaluations/audits/corrected-integration-qualification-jcodemunch-codex-mcp-v2-20260719.json
- ../../../../sources/evaluations/audits/opencode-next-five-batch2-results-20260730.json
- ../../../../scripts/validate_repository.py

## Engineering Decisions

Token comparisons use one final monotonic cumulative provider snapshot per distinct thread and compare only compatible baseline pools; weighted units are fresh input plus 0.1 times cached input plus 6 times output. Direct-account Claude matrices propagate refreshed OAuth bytes only after successful tasks and execute serially.

## Current Behavior

Lifecycle V1 sessions bind model condition, protocol fingerprint, profile identity, task artifacts, usage receipts, and compact manifests before publication.

## Rationale

A single monotonic provider receipt and compatible baseline binding are required to distinguish accounting integrity from causal efficiency claims. Successful-task-only OAuth propagation prevents one isolated lane from invalidating the next lane's copied refresh token without allowing an authentication failure to replace the owner credential snapshot.
