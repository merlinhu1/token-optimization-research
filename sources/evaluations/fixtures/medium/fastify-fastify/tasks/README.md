# Fastify lifecycle v0 — active Baseline V5 tasks

1. `fastify-lifecycle-feature-v0` — inspect and restore compilation across the request/reply component pair.
2. `fastify-lifecycle-refactor-v0` — inspect and restore compilation across the content-type component pair.
3. `fastify-lifecycle-review-v0` — inspect and correct a proposed bootstrap/error change until it compiles.

The active model-facing contracts are under `task-generations/baseline-v5/`. Each task permits normal search and inspection, changes two production files, and exposes only its affected-component compile command. The controller applies all three start patches before prompt 1 and runs all compile verifiers after prompt 3.
