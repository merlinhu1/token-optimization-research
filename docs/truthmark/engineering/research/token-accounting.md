---
status: active
truth_kind: engineering-contract
last_reviewed: 2026-07-30
---

# Token Accounting And Evaluation Contracts

## Purpose

Define the production estimand and separate experiment validity from sampled model quality.

## Scope

This contract governs lifecycle-v0 provider-token samples, baseline reuse, compatible treatment comparisons, and exclusion/rerun boundaries.

## Current Implementation Behavior

- The active portfolio contains Fastify, Beets, and Terraform lifecycle-v0 sequences.
- The runner captures cumulative provider usage across one persistent sequential agent session.
- Codex usage comes from provider-reported Codex JSONL snapshots. OpenCode usage comes from unique incremental `step_finish` parts; fresh input, cache read, cache write, visible output, and reasoning are normalized without counting reasoning twice.
- Replacement-runtime protocols may bind distinct runtime-specific model-condition IDs while holding provider, model, reasoning effort, fixtures, prompts, and baseline pool fixed. The frozen protocol identifies the Codex baseline condition and replacement-runtime treatment condition separately.
- The matrix reuses the first operationally valid baseline for a causal comparison fingerprint and replicate.
- Repository validation requires complete provider usage, structural isolation, clean execution integrity, and recoverable compact evidence—not verifier success or source review.
- Before any non-baseline provider launch, both repository validation and the direct runner require exact parity approval plus a current provider-free qualification receipt for every active fixture/profile protocol binding; MCP profiles additionally require non-empty `tools/list` proof.
- Canonical treatment profiles install every author-recommended Codex surface, including product-authored guidance, native skills/plugins, and reviewed hooks; reduced or prompt-emulated setups are ablations or invalid assignments, not product treatments.
- The final shared-runner qualification covers 45 current selectable fixture/profile bindings across 15 profiles with zero provider calls.
- Eighteen provider-backed baseline records are currently retained.

## Product Truth Links

- None. This is an engineering research evidence contract.

## Contract Surface

- `data/workflow-task-sequences.json`
- `data/workflow-sessions.json`
- `scripts/run_codex_workflow_evaluation.py`
- `scripts/opencode_workflow_adapter.py`
- `scripts/extract_opencode_usage.py`
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
- Concealed-verifier outcomes and source-quality reviews are diagnostic model-behavior fields. They do not gate token accounting or baseline reuse.
- Never rerun because the model failed a verifier, produced imperfect code, or received a low review score.
- Rerun only for experiment invalidity or incompleteness: fixture/verifier defect, wrong controller assets, corrupt/missing usage, failed isolation/integrity, or incomplete prompt execution.
- Baseline/treatment comparisons require matching fixture, sequence, provider, model, reasoning effort, causal comparison fingerprint, and replicate. Runtime/model-condition IDs must also match unless the frozen profile is explicitly a replacement-runtime treatment; in that case the runtime difference is the experimental variable and both condition IDs are frozen separately.
- Report absolute provider-token totals with percentage changes.
- Treatment installation/configuration is valid treatment exposure; observed use may be zero and remains descriptive.
- OpenCode automatic-plugin activation and model-issued product-tool uptake are reported separately. A loaded automatic plugin may validly record zero model-issued product calls; an exposed MCP surface with zero selected calls is also a valid natural-use result.
- A prompt/verifier/fixture defect is attributed to the fixture, not the model.

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
- ../../../../scripts/opencode_workflow_adapter.py
- ../../../../scripts/extract_opencode_usage.py
- ../../../../scripts/workflow_model_condition_runtime.py
- ../../../../scripts/prepare_pinned_codex_marketplace.py
- ../../../../scripts/trust_codex_plugin_hooks.py
- ../../../../scripts/install_jcodemunch_codex_guidance.py
- ../../../../sources/evaluations/audits/corrected-integration-qualification-jcodemunch-codex-mcp-v2-20260719.json
- ../../../../sources/evaluations/audits/opencode-next-five-batch2-results-20260730.json
- ../../../../scripts/validate_repository.py
