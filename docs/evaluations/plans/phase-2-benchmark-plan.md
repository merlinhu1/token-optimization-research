# Production evaluation plan

## Status

Production token-evidence collection is active.

## Portfolio

Run exactly three lifecycle-v0 sequences: Fastify, Beets, and Terraform. Each sequence uses feature implementation, behavior-preserving refactor, and code review/correction.

## Order of operations

1. Keep pinned snapshots, prompts, seed patches, concealed tests, and generated qualification synchronized.
2. Freeze one current v0 execution contract for each lane/profile.
3. Run one isolated bare baseline replicate per sequence.
4. Retain the first operationally complete, integrity-valid provider sample regardless of model verifier/review outcome.
5. Record verifier and source-review outcomes diagnostically; do not use them to select or replace token samples.
6. Repair fixture defects before attribution, then rerun only the invalid fixture contract under a new fingerprint.
7. Run treatment under the same compatible lane contract and replicate.
8. Compare only weighted token cost within a compatible baseline pool; raw provider counters are calculation/audit telemetry, not a result metric.

## Eligibility

A run is usable for token accounting when every prompt completed operationally, provider usage is complete, isolation and integrity checks pass, compact evidence is recoverable, and the fixture contract is valid. Model correctness, verifier pass rate, and review score are reported outcomes—not eligibility gates.
