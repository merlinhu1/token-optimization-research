# Research roadmap

## Current state

The repository is pre-production and has no accepted execution results. Contract design is converged on three lifecycle v0 lanes: Fastify, Beets, and Terraform. Each lane orders feature implementation, behavior-preserving refactor, and code review/correction in one persistent workflow.

## Exit criteria before production

1. Every start patch independently applies to its pinned snapshot.
2. Feature and review starts fail behavioral acceptance for the intended reason.
3. Refactor starts pass behavior acceptance and fail the disclosed structural gate.
4. All three start patches compose without conflicts.
5. Fixed snapshots pass every verifier.
6. Qualification evidence and frozen v0 execution contracts match registry fingerprints.
7. Repository validation and contract tests pass.

## First production step

Run one isolated bare baseline replicate per lane. Review correctness and final-tree quality before any treatment run or token comparison. A failed fixture or verifier contract is a fixture failure, not a model result; repair v0 before accepting evidence.
