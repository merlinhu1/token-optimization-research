# Production evaluation plan

## Status

Pre-production. No execution result has been accepted or retained.

## Portfolio

Run exactly three lifecycle v0 sequences: Fastify, Beets, and Terraform. Each sequence uses feature implementation, behavior-preserving refactor, and code review/correction.

## Order of operations

1. Keep the pinned snapshots, prompts, start patches, review patches, concealed tests, and generated qualification evidence synchronized.
2. Freeze one current v0 execution contract for each selected lane/profile.
3. Run one isolated bare baseline replicate per sequence.
4. Complete independent correctness and software-quality review.
5. Reject fixture defects before attributing model failure.
6. Only after an accepted baseline, run the selected treatment under the same lane contract.
7. Compare cumulative provider-reported tokens only within a compatible baseline pool.

## Acceptance

A run is usable only when all task outcomes are structurally recorded, all final concealed verifiers pass, tool isolation passes, provider usage is complete, and independent quality review accepts the final tree.
