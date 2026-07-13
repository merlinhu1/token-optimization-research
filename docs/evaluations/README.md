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

The production surface remains lifecycle v0: Fastify, Beets, and Terraform each exercise feature implementation, behavior-preserving refactoring, and code review/correction in one persistent workflow. The active session registry contains 93 completed provider-backed records: 27 controls and 66 objective-eligible treatments.

The corrected Phase 2 natural-use screen retains 48 eligible treatment sessions across 16 conditions. A prospective r3 screen then added three fresh bare-Codex baselines and 18 eligible treatment sessions for TokenJuice, SigMap, Ponytail, RTK, CodeGraph, and jcodemunch-mcp v2. In r3, the six-profile panel used 216,039,299 provider tokens against 202,598,376 repeated matched-baseline tokens (+6.63%) with 53/54 treatment verifiers. Four of six aggregate directions differed from the preceding screen, so the evidence does not support a stable ranking. Six Cartog direct-MCP sessions were deleted rather than relabelled after an integration-parity defect was established.

The completed assisted-v1 Sol/`high` baseline remains immutable historical evidence: 7,718,469 provider tokens, 9/9 task verifiers, and zero controller retries. A trajectory/source audit nevertheless found corrected implementation mistakes and one surviving Terraform hidden-contract regression. The failed **Baseline V2** paid attempt is also immutable: it spent 808,169 provider tokens and published no session or comparison. The explicitly authorized **Baseline V3** pilot retained its first provider sample on all three low-complexity sequences: 236,151 total provider tokens with all nine model commands exiting zero and producing the prescribed mechanical diffs. Fastify's repeated final verifier passed 3/3; Beets and Terraform each recorded 0/3 because the controller's final-verifier wrapper omitted `WORKFLOW_REPO`, even though the same six focused commands passed during their model turns. Two stale post-publication test assumptions initially rolled back the registry transaction; they were corrected and the three immutable compact bundles were recovered without provider reruns. The paid identities are permanently occupied, and treatment execution remains governed per sequence by the independent zero-incident audit.

**Baseline V4** is the provider-free-qualified successor only for Beets and Terraform. It retains the V3 workload and acceptance behavior while moving the repository fallback into six generation-local task verifiers. Both generated aggregate verifiers pass all three tasks with `WORKFLOW_REPO` removed; six literal command rehearsals, two qualifications, and the retained serial prepare-only matrix pass with zero provider calls. Fastify remains on its passing V3 baseline. No V4 attempt receipt or paid-pilot audit exists, so V4 pilot and treatment execution remain fail-closed until separately authorized and audited.
