# Fastify lifecycle v0 — active Baseline V5 tasks

1. `fastify-lifecycle-feature-v0` — restore normalized request media-type support.
2. `fastify-lifecycle-refactor-v0` — restore the shared bounded Content-Type cache without behavioral drift.
3. `fastify-lifecycle-review-v0` — review and correct the max-parameter-length HTTP status change.

The active model-facing contracts are under `task-generations/baseline-v5/`. Each prompt states a complete software objective, permits normal search and related-code inspection, and expects a correct implementation and relevant validation. The controller applies all three semantic start patches before prompt 1 and runs controller-only compile verifiers after prompt 3.
