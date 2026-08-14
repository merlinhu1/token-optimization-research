# ADR 0006: Gate Repository State With One Operator-Invoked Check

## Status

Accepted

## Context

Research state lives in machine registries under `data/`, with generated views and human-facing
prose derived from them. Stale prose that contradicts the registries is the main way this
repository can mislead a reader, so the synchronization rule and the check that enforces it
have to be explicit.

Between 2026-06 and 2026-08 that enforcement lived in the Truthmark workflow. It was removed on
2026-08-14 as too heavy for a single-maintainer research corpus; the decisions below are what
survived it.

## Decision

- Decision (2026-07-16): An evidence-changing action is incomplete until active state surfaces
  are synchronized or deleted.
- Decision (2026-08-12): The required-checks gate has one executable definition, `make check`;
  the `AGENTS.md` list documents that target rather than standing as a separate hand-run
  checklist.
- Decision (2026-08-12): `schemas/workflow-session-record.schema.json` is the shape authority
  for session records and is enforced against every retained session. Record shape and the
  schema change together; the validator keeps only constraints the schema cannot express.
- Decision (2026-08-14): This repository runs no continuous integration. It is a research
  evidence corpus rather than a deployed software system, so the gate is invoked by the agent or
  operator completing a change, not by a hosted runner on push.
- Decision (2026-08-14): The Truthmark workflow is removed. Its routing, ownership, lease, and
  sync ceremony cost more per change than it returned on a corpus with one maintainer, and its
  durable output was decision records that are now plain ADRs under this directory.

## Consequences

- `make check` is the whole gate. Nothing runs it automatically, so an unrun gate is no gate.
- Registries are updated first; generated runbooks and prose follow.
- Architecture decisions are recorded here, dated inline, with Git history as the audit trail.

## Provenance

Migrated 2026-08-14 from `docs/truthmark/engineering/research/agent-workflow.md` when the
Truthmark workflow was removed. Four decisions in that document described Truthmark's own
routing and ownership model and were dropped rather than migrated, because the tooling they
governed no longer exists.
