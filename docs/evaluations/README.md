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

The production surface remains lifecycle v0: Fastify, Beets, and Terraform each exercise feature implementation, behavior-preserving refactoring, and code review/correction in one persistent workflow. The active session registry contains 90 completed provider-backed records: 24 controls and 66 objective-eligible treatments.

The corrected Phase 2 natural-use screen retains 48 eligible treatment sessions across 16 conditions. A prospective r3 screen then added three fresh bare-Codex baselines and 18 eligible treatment sessions for TokenJuice, SigMap, Ponytail, RTK, CodeGraph, and jcodemunch-mcp v2. In r3, the six-profile panel used 216,039,299 provider tokens against 202,598,376 repeated matched-baseline tokens (+6.63%) with 53/54 treatment verifiers. Four of six aggregate directions differed from the preceding screen, so the evidence does not support a stable ranking. Six Cartog direct-MCP sessions were deleted rather than relabelled after an integration-parity defect was established.

The currently active assisted-v1 task contracts were activated only after the natural-use r3 campaign completed. The retained original receipt covers baseline plus six eligible r3 profiles in 21 provider-free lanes. The corrected Cartog product-v2 profile has a separate three-lane provider-free receipt. The first provider-backed assisted-v1 baseline used GPT-5.6 Sol/`high` and retained 7,718,469 provider tokens across Fastify, Beets, and Terraform with 9/9 task verifiers and zero operational retries ([audit](../../sources/evaluations/audits/assisted-v1-sol-high-baseline-r0-20260720.json)). These contracts disclose the intended implementation and focused validation workflow and are designed to reduce trajectory variance in a standardized-workflow study; no assisted treatment has run, so no treatment effect is yet estimated and the new baseline does not reinterpret retained natural-use sessions.
