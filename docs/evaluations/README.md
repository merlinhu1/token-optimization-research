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

The production surface remains lifecycle v0: Fastify, Beets, and Terraform each exercise feature implementation, behavior-preserving refactoring, and code review/correction in one persistent workflow. The active registry now contains 167 accepted sessions: 35 baselines, 3 replacement-runtime OpenCode controls, and 129 individual-tool treatments.

The corrected Phase 2 natural-use screen retains 48 eligible treatment sessions across 16 conditions. A prospective r3 screen then added three fresh bare-Codex baselines and 18 eligible treatment sessions for TokenJuice, SigMap, Ponytail, RTK, CodeGraph, and jcodemunch-mcp v2. In r3, the six-profile panel used 216,039,299 provider tokens against 202,598,376 repeated matched-baseline tokens (+6.63%) with 53/54 treatment verifiers. Four of six aggregate directions differed from the preceding screen, so the evidence does not support a stable ranking. Six Cartog direct-MCP sessions were deleted rather than relabelled after an integration-parity defect was established.

Bare OpenCode 1.18.9 with GPT-5.6 Sol/`high` retained 122,368 provider tokens and passed 9/9 task verifiers. A stricter installation audit withdrew twelve TokenJuice, Snip, Cartog, and Headroom sessions from the active corpus; only Serena's three original sessions remain accepted while source-pinned successor profiles await paid execution. See `sources/evaluations/audits/invalid-opencode-treatment-result-deletions-20260729.json`.

The completed assisted-v1 Sol/`high` baseline remains immutable historical evidence: 7,718,469 provider tokens, 9/9 task verifiers, and zero controller retries. A trajectory/source audit nevertheless found corrected implementation mistakes and one surviving Terraform hidden-contract regression. The failed **Baseline V2** paid attempt is also immutable: it spent 808,169 provider tokens and published no session or comparison. The explicitly authorized **Baseline V3** pilot retained its first provider sample on all three low-complexity sequences: 236,151 total provider tokens with all nine model commands exiting zero and producing the prescribed mechanical diffs. Fastify's repeated final verifier passed 3/3; Beets and Terraform each recorded 0/3 because the controller's final-verifier wrapper omitted `WORKFLOW_REPO`, even though the same six focused commands passed during their model turns. Two stale post-publication test assumptions initially rolled back the registry transaction; they were corrected and the three immutable compact bundles were recovered without provider reruns. The paid identities are permanently occupied, and treatment execution remains governed per sequence by the independent zero-incident audit.

**Baseline V4** is active only for Beets and Terraform. The authorized 2026-07-28 r0 pilots retained 88,200 and 87,811 provider tokens respectively under GPT-5.6 Sol/`high`. All six prescribed commands and repeated final task verifiers exited zero, and independent review recorded zero incidents in every required category for both controls. Each initial registry transaction rolled back on stale post-publication state expectations; both compact sessions were recovered under the production lock with no provider rerun. Both sequence gates permit provider-free treatment-protocol freeze, while both paid pilot identities remain permanently occupied. The accepted r1 replication added one zero-incident control per lane. The r2 campaign then retained Fastify at 90,420 and Terraform at 87,784 provider tokens; all six commands and final verifiers passed with zero independently reviewed incidents. Beets r2 failed before provider invocation because lane scratch disappeared during clone, so it remains an occupied zero-spend controller attempt with no session or token result. Owner message `1531806010350633101` prospectively authorized the distinct Beets r3 replacement, which retained 87,370 provider tokens and 43,130.2 weighted units with 3/3 commands and verifiers passing, one persistent thread, and zero retries. Its initial merge rolled back only because stale tests required the now-occupied receipt to remain absent; the exact compact bytes were recovered provider-free. The valid current controls now contain three runs per lane: 783,883 provider tokens and 322,096.0 weighted units under `fresh + 0.1×cached + 6×output`.
