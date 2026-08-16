# Fastify lifecycle v2 — active Lifecycle V2 tasks

1. `fastify-lifecycle-feature-v1` — restore normalized request media-type support.
2. `fastify-lifecycle-refactor-v1` — restore the shared bounded Content-Type cache without behavioral drift.
3. `fastify-lifecycle-review-v1` — review and correct the max-parameter-length HTTP status change.

The active model-facing contracts are under `task-generations/lifecycle-v2/`. Lifecycle V2 is a series of 6 bounded defect repairs of comparable size, each restoring one named behavior that a specific upstream test already decides, so every task has a closed stopping condition and no single task dominates session cost. Each prompt states the observable symptom without naming the file, function, or test, so locating the defect remains real retrieval work. The controller applies all semantic start patches before prompt 1 and runs controller-only verifiers after the final prompt.
