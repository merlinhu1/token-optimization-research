# Beets lifecycle v0 — active Baseline V5 tasks

1. `beets-lifecycle-feature-v0` — restore escaped separators in function-template arguments.
2. `beets-lifecycle-refactor-v0` — remove the unnecessary LazyDict iterator layer without behavioral drift.
3. `beets-lifecycle-review-v0` — review and correct featuring-token selection in ftintitle.

The active model-facing contracts are under `task-generations/baseline-v5/`. Each prompt states a complete software objective, permits normal search and related-code inspection, and expects a correct implementation and relevant validation. The controller applies all three semantic start patches before prompt 1 and runs controller-only compile verifiers after prompt 3.
