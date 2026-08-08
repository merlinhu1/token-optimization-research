---
status: active
truth_kind: engineering-workflow
doc_type: workflow
source_of_truth:
  - ../../../../AGENTS.md
  - ../../../../.truthmark/config.yml
last_reviewed: 2026-07-16
---

# Agent Research Workflow

## Purpose

This doc owns the durable agent-facing workflow for keeping evidence, registries, generated procedure, prompts, and research truth synchronized.

## Scope

This workflow covers repository-local agent instructions, evaluation state changes, generated runbooks, active prompts/templates/skills, Truthmark routing, and structural validation. It does not own the scientific content of each individual evaluation contract or raw evidence bundle.

## Current Implementation Behavior

- `AGENTS.md` is the repository-authored instruction authority. It is not generated or managed by Truthmark.
- `.agents/skills/` contains repo-local research skills.
- `.truthmark/config.yml` declares `docs/truthmark` as the Truthmark workspace.
- Truthmark routes connect code, data, prompts, and documentation to bounded durable truth docs.
- `scripts/validate_repository.py` and `scripts/update_workflow_runbook.py --check` enforce repository and generated-runbook consistency.
- Direct-Anthropic Claude Code Lifecycle V1 preparation is recorded in a frozen audit authority and generated protocol files; the owner account is accepted only through `TOKEN_EVAL_CLAUDE_ACCOUNT_HOME`, copied ephemerally into the lane, and never retained in evidence.

## Product Truth Links

- None. This is an installed repository-maintenance workflow, not a product capability of any evaluated tool.

## Execution Model

Agents update authoritative registries first, derive generated procedure from them, reconcile routed human-facing surfaces, and then run structural and Truthmark checks. Raw evidence remains immutable; current state is projected through registries and generated views.

## Triggers

Apply the synchronization workflow after an evaluation run, qualification/protocol refresh, fixture-state change, session merge/deletion, treatment comparison, evidence-stage promotion, policy change, or edit to a routed prompt/template/skill.

## Steps

1. Read the active contract in `AGENTS.md` and the relevant repo-local skill.
2. Update machine authorities first, especially `data/workflow-sessions.json` and `data/repository-fixtures.json`.
3. Regenerate `docs/evaluations/operations/runbook.md` from the registries.
4. Reconcile active README, roadmap, current-findings, prompt, schema, skill, and Truthmark surfaces that report the changed state or policy.
5. Search for the retired status, path, identifier, and policy wording. Delete a redundant document or template when it has no distinct maintained authority or current consumer.
6. Preserve immutable protocol and evidence bytes; record current state in registries and generated views.
7. Run `truthmark check --json`, `truthmark index --json`, `python3 scripts/validate_repository.py`, the workflow contract tests, and `git diff --check` as applicable.
8. Inspect Git status after tests. Restore any required test deleted by a destructive fixture and ensure new evidence is tracked before handoff.

## Outputs

- Evidence and registry state that agree.
- Generated operator guidance that does not rerun occupied samples.
- Prompts and skills that encode the current token-accounting estimand.
- Small Git-reviewable Truthmark summaries of durable methodology and findings.

## Engineering decisions

- Decision (2026-06-26): Truthmark is a research-truth workflow layer, not a feature of evaluated tools.
- Decision (2026-06-26): Truthmark does not own raw `sources/**` evidence artifacts.
- Decision (2026-07-16): `AGENTS.md` is maintained directly by the repository; ignored `instruction_targets` and nonexistent managed-block claims are removed.
- Decision (2026-07-16): An evidence-changing action is incomplete until active state surfaces are synchronized or deleted.

## Non-goals

- Truthmark does not generate or rewrite `AGENTS.md`.
- Temporary scratch notes do not require Truthmark updates.
- Durable truth docs do not replace raw provider evidence or authoritative JSON registries.

## Maintenance Notes

- Update this truth doc whenever `AGENTS.md` changes the evidence/document synchronization sequence.
- Keep `docs/truthmark/routes/areas.md` synchronized with added, moved, or deleted prompt, template, schema, skill, and validator surfaces.
- Do not reintroduce `instruction_targets` or claims that Truthmark generates an `AGENTS.md` managed block.

## Source References

- ../../../../AGENTS.md
- ../../../../.truthmark/config.yml
- ../../../../.agents/skills/index.md
- ../../../../scripts/validate_repository.py
- ../../../../scripts/update_workflow_runbook.py
- ../../../../scripts/run_codex_fixture_evaluation.py
- ../../../../scripts/claude_code_workflow_adapter.py
- ../../../../sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-protocol-preparation-20260808.json
- ../../routes/areas.md

## Engineering Decisions

Repository changes follow the machine registries and generated runbook as the authoritative execution record; Truthmark routing remains documentation metadata and does not override evaluation controls.

## Current Behavior

Research-truth changes are synchronized after code and registry changes, with validation and artifact-preservation checks required before publication.

## Rationale

Centralizing execution state in registries and generated views prevents stale prose from being mistaken for provider-backed evidence.
