---
status: active
truth_kind: architecture
doc_type: architecture
source_of_truth:
  - ../../../../data/compatibility-edges.json
  - ../../../../docs/reference/compatibility-taxonomy.md
last_reviewed: 2026-07-18
---

# Stack Compatibility

## Purpose

This doc owns the durable compatibility-safe stack model.

It keeps tool combinations organized by owned surfaces and conflict risk.

## Scope

This doc covers token-saving technique surfaces, stack hypotheses, conflicts, and ablation expectations.

It does not store raw tool-source inspection notes.

## Current Implementation Behavior

- The repository stores techniques in `data/techniques.json`.
- The repository stores compatibility edges in `data/compatibility-edges.json`.
- The Phase 1 report frames current stack hypotheses as compatibility-safe research candidates, not measured selections.
- The historical `stack-tokenjuice-jcodemunch-mcp` executions are excluded from stack-effect claims. TokenJuice's Codex hook was absent and disabled; jcodemunch lacked the pinned direct-binary path, positive handshake proof, and an explicit neutral-versus-guided estimand. The retained 67,155,585-token total is forensic accounting, and the prior “does not advance” conclusion is withdrawn.

## Product Truth Links

- None. Stack compatibility describes research architecture, not product behavior.

## System Role

This model is the repository's architecture layer for combining token-saving tools without surface-owner conflicts.


## Components

- Terminal-output owners compact or summarize shell and tool output.
- Retrieval and code-context tools select relevant source context.
- Memory authorities persist and reinject repository or session facts.
- Context-compression owners rewrite broad conversation or prompt context.
- Workflow-execution owners change how tasks are delegated or executed.
- Output-style controllers reduce assistant prose or artifact verbosity.
- Artifact-policy controllers reduce generated artifact size or complexity.
- Routing authorities decide which component sees which context.

## Data And Control Flow

- Tool dossiers and technique records identify mechanisms.
- Compatibility edges record whether surfaces compose, conflict, or require isolation.
- Stack reports turn those records into benchmarkable hypotheses.

## Ownership

- Compatibility ownership lives in `docs/truthmark/engineering/research/stack-compatibility.md`.
- Detailed dossier evidence remains under `docs/tool-dossiers/**`.

## Cross-Cutting Constraints

- Stack claims must remain evidence-stage calibrated.
- Duplicate surface ownership is a compatibility risk.
- Benchmark conclusions require ablation planning.

## Engineering Decisions

- Decision (2026-06-26): Compatibility-safe stacks should avoid duplicate ownership of the same surface.
- Decision (2026-06-26): Installer or orchestrator tools are evaluated separately from reducers.
- Decision (2026-06-26): Multi-component stack claims require ablation planning before benchmark conclusions.
- Decision (2026-07-18): The historical TokenJuice+jcodemunch stack decision is withdrawn because the intended component assignments were not validly installed/proven. Preserve its provider-accounting records as excluded evidence.
- Decision (2026-07-18): A future stack requires separately qualified versioned individual integrations and a new preregistered stack identity.

## Rationale

Token-saving tools can conflict when two components rewrite the same context surface.

Surface ownership makes stack design testable and reviewable.

## Non-Goals

- This doc does not declare measured selections without benchmark-audit or reproduction evidence.
- This doc does not promote lead-stage tools into recommendations.
- This doc does not replace individual tool dossiers.

## Maintenance Notes

- Update this doc when `data/compatibility-edges.json` or the compatibility taxonomy changes.
- Use `stack-ablation-planner` before evaluating multi-component stacks.
- Keep stack wording aligned with `compatibility-safe` framing.

## Source References

- ../../../../data/compatibility-edges.json
- ../../../../data/techniques.json
- ../../../../docs/reference/compatibility-taxonomy.md
- ../../../../docs/architecture/compatibility-graph.md
- ../../../../docs/papers/phase-1-compatibility-safe-token-saving-stacks.md
- ../../../../.agents/skills/stack-ablation-planner.md

## Product Decisions

A compatibility-safe stack assigns one clear owner to each token-relevant surface; overlapping retrieval, compaction, memory, hook, or proxy tools require explicit ablation identities.
