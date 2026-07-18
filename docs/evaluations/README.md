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

The production surface remains lifecycle v0: Fastify, Beets, and Terraform each exercise feature implementation, behavior-preserving refactoring, and code review/correction in one persistent workflow. The repository retains 60 completed provider-backed sessions and 54 historical treatment comparisons.

The official-integration parity audit excludes 42 of the 54 treatment sessions from objective claims while preserving their provider-accounting evidence. The historical Phase 3 TokenJuice+jcodemunch screen is withdrawn as a product-effect decision. Corrected TokenJuice and neutral direct-binary jcodemunch profiles are versioned and no-provider-qualified but have no provider-backed samples; a product-guided jcodemunch condition would require a separate instruction-policy profile.

The current validity authority is the [official-integration parity audit](../papers/official-integration-parity-audit.md). Phase 2 and Phase 3 reports remain as historical accounting reports with superseding notices.

Natural tool use remains unconstrained after valid assignment. Valid assignment now requires the pinned product's real Codex integration and, for MCP, a retained successful handshake. Product-authored routing guidance is part of the treatment when the pinned guide makes it part of normal setup; evaluator-authored steering remains forbidden.
