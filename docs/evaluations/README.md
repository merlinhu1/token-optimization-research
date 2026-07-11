# Evaluations

This directory separates evaluation contracts from operator instructions and historical plans.

## Run an evaluation

Start with the generated [operator runbook](operations/runbook.md).

- [Runner reference](operations/runner-reference.md) — command-line and resume details
- [Workflow guide](operations/workflow-guide.md) — the active lifecycle-v0 flows
- [Fixture guide](operations/fixture-guide.md) — fixture layout and preparation

## Understand the design

- [Evaluation framework](design/framework.md) — estimand, eligibility, and interpretation
- [Persistent workflow model](design/workflow-model.md) — why tasks run in one resumed session
- [Result schema](design/result-schema.md) — cumulative result structure
- [Fixture design](design/fixture-design.md) — fixture and verifier contract
- [Token and quality policy](design/token-and-quality-policy.md) — provider accounting and diagnostic quality
- [Tool isolation policy](design/tool-isolation-policy.md) — treatment isolation requirements

## Plans and templates

- [`plans/`](plans/) contains phase plans retained for historical context.
- The reusable [evaluation protocol template](../../templates/evaluation-protocol.md) lives with the other repository-wide templates.

## Current evidence

The production surface remains lifecycle v0: Fastify, Beets, and Terraform each exercise feature implementation, behavior-preserving refactoring, and code review/correction in one persistent workflow. The active session registry contains 93 completed provider-backed records: 21 controls and 72 objective-eligible treatments.

The corrected Phase 2 natural-use screen retained 51 treatment sessions across 17 conditions. A prospective r3 screen then added three fresh bare-Codex baselines and 21 treatment sessions for TokenJuice, SigMap, Ponytail, RTK, Cartog, CodeGraph, and jcodemunch-mcp v2. In r3, the seven-profile panel used 257,591,572 provider tokens against 236,364,772 repeated matched-baseline tokens (+8.98%) with 62/63 treatment verifiers. Five of seven aggregate directions differed from the preceding screen, so the evidence does not support a stable ranking.

The currently active assisted-v1 task contracts were qualified provider-free across baseline and all seven r3 profiles only after the natural-use r3 campaign completed. They disclose the intended implementation and focused validation workflow to reduce trajectory variance in a separate standardized-workflow study; they do not reinterpret the retained natural-use sessions. The [qualification receipt](../../sources/evaluations/audits/assisted-v1-protocol-qualification-20260720.json) records all 24 passing lanes and zero provider calls.
