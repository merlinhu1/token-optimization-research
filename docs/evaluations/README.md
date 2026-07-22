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

The completed assisted-v1 Sol/`high` baseline remains immutable historical evidence: 7,718,469 provider tokens, 9/9 task verifiers, and zero controller retries. A trajectory/source audit nevertheless found corrected implementation mistakes and one surviving Terraform hidden-contract regression, so the experiment owner rejected that task family as too complex for the provider-token estimand. **Baseline V2** is now active for future execution: nine routine tasks across the same three persistent lifecycle sequences, one or two production files per task, exact recipes, complete model-visible focused acceptance, and no discovery or broad-suite work. All three sequences pass provider-free qualification and have frozen Sol/`high` pilot protocols ([qualification audit](../../sources/evaluations/audits/baseline-v2-task-family-qualification-20260721.json)); zero provider calls were made. Treatment protocol freezing, matrix preparation, and direct execution are machine-blocked until an exact-protocol independent audit records zero incidents across every required category.
