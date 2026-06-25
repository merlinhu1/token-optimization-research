---
status: active
truth_kind: engineering-workflow
last_reviewed: 2026-06-26
---

# Agent Research Workflow

## Purpose

This doc owns the durable agent-facing workflow for maintaining research truth in this repository.

It links repo-local skills, AGENTS instructions, Truthmark routing, and validation gates.

## Scope

This doc covers agent maintenance behavior for research docs and evaluation artifacts.

It does not own the content of each individual methodology or evaluation contract.

## Current Implementation Behavior

- `AGENTS.md` contains repo-specific research instructions and a Truthmark-managed workflow block.
- `.agents/skills/` contains seven repo-local research skills.
- `.truthmark/config.yml` configures `docs/truthmark` as the workspace and `AGENTS.md` as the instruction target.

## Product Truth Links

- None. Truthmark is an injected repository-truth workflow layer for this research repo.

## Triggers

- An agent changes report, methodology, evaluation, prompt, template, or local skill files.
- An agent changes Truthmark config, routes, or truth docs.
- An agent changes repository validation rules.

## Inputs

- `AGENTS.md` provides repo-level agent instructions.
- `.agents/skills/**` provides repo-local research skills.
- `docs/truthmark/routes/areas/**` maps durable research surfaces to truth docs.
- `scripts/validate_repository.py` provides the repository structural validation gate.

## Execution Model

Agents use the repo-local skills for research quality and Truthmark for durable truth maintenance.

Docs-only changes still need Truthmark checks when they affect routed truth.

## Steps

1. Load relevant repo-local skills from `.agents/skills/` before research-writing or evaluation work.
2. Make the research or documentation change.
3. Update the bounded Truthmark truth doc when durable methodology or findings change.
4. Run `truthmark check --json` and `truthmark index --json` after Truthmark changes.
5. Run `python3 scripts/validate_repository.py` after repository structure changes.
6. Run `git diff --check` before handoff.

## Outputs

- Research docs aligned with repo-local skill guidance.
- Truthmark docs that summarize durable research truth.
- Validation output suitable for human review.

## Engineering Decisions

- Decision (2026-06-26): Truthmark is used as a research-truth workflow layer in this repo.
- Decision (2026-06-26): Truthmark does not own raw `sources/**` evidence artifacts.
- Decision (2026-06-26): Repo-local skills remain under `.agents/skills/` and are referenced by `AGENTS.md`.

## Rationale

The repository's main quality risk is drift between evidence, methodology, and polished research conclusions.

Truthmark gives that durable truth a small Git-reviewable surface.

## Non-Goals

- This doc does not make Truthmark a product feature of any evaluated tool.
- This doc does not require global Hermes skills.
- This doc does not require Truthmark updates for every temporary note.

## Maintenance Notes

- Rerun `truthmark init` when `truthmark check` reports stale generated surfaces.
- Preserve the Truthmark-managed block in `AGENTS.md`.
- Keep custom repo instructions outside the managed block.

## Source References

- ../../../../AGENTS.md
- ../../../../.truthmark/config.yml
- ../../../../.agents/skills/index.md
- ../../../../scripts/validate_repository.py
- ../../routes/areas.md
