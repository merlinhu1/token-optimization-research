# Beets lifecycle v1 — active Lifecycle V1 tasks

1. `beets-lifecycle-feature-v1` — restore escaped separators in function-template arguments.
2. `beets-lifecycle-refactor-v1` — remove the unnecessary LazyDict iterator layer without behavioral drift.
3. `beets-lifecycle-review-v1` — review and correct featuring-token selection in ftintitle.

The active model-facing contracts are under `task-generations/lifecycle-v1/`. Each prompt states a complete software objective, permits normal search and related-code inspection, and expects a correct implementation and relevant validation. The controller applies all three semantic start patches before prompt 1 and runs controller-only compile verifiers after prompt 3.
