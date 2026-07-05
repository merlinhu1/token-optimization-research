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

The production surface remains lifecycle v0: Fastify, Beets, and Terraform each exercise feature implementation, behavior-preserving refactoring, and code review/correction in one persistent workflow. The active session registry contains 18 completed provider-backed records: six bare-Codex controls and 12 objective-eligible treatments across four narrow conditions.

The official-integration parity audit found 42 corrupted historical treatment sessions. At the experiment owner's direction, their session records, comparisons, compact bundles, and occupied protocols were deleted from the active corpus—not relabelled as baseline. Two deletion receipts record the affected identities and recovery commit. The historical Phase 3 TokenJuice+jcodemunch screen remains withdrawn.

Thirteen corrected individual-tool profiles and 39 fixture-specific frozen protocols now cover every deleted individual condition. All 39 passed provider-free fixture preparation, host-integration, warm-state, and applicable initialize plus tools/list handshake gates; the retained machine receipt records every lane. Product-authored routing guidance is part of the treatment when normal pinned setup installs it; evaluator-authored steering remains forbidden. No corrected profile has a provider-backed sample.
