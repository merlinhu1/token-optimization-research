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

The production surface is lifecycle v0 only. Fastify, Beets, and Terraform each exercise feature implementation, behavior-preserving refactoring, and code review/correction in one persistent workflow. The repository retains 60 operationally valid provider-backed sessions and 54 matched treatment comparisons.

Phase 3 does not introduce new tasks or rerun retained components. The first completed stack profile, `stack-tokenjuice-jcodemunch-mcp`, used the same lifecycle-v0 pool and added only a TokenJuice-plus-jcodemunch treatment session for each lane. It reduced aggregate tokens 9.12% versus bare Codex but used 27.19% more than TokenJuice alone and failed the incremental-value criterion.

The current synthesis is the [Phase 3 TokenJuice + jcodemunch MCP stack-screen paper](../papers/phase-3-tokenjuice-jcodemunch-stack-screen.md), with component evidence in the [Phase 2 lifecycle-v0 natural-use screening paper](../papers/phase-2-lifecycle-v0-natural-use-screening.md).

Verifier and optional source-review outcomes are diagnostic; complete provider usage and execution integrity determine token-accounting eligibility. Natural availability without forced invocation remains the treatment boundary.
