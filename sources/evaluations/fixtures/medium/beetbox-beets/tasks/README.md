# Beets lifecycle v2 — active Lifecycle V2 tasks

1. `beets-lifecycle-feature-v1` — restore escaped separators in function-template arguments.
2. `beets-lifecycle-refactor-v1` — remove the unnecessary LazyDict iterator layer without behavioral drift.
3. `beets-lifecycle-review-v1` — review and correct featuring-token selection in ftintitle.

The active model-facing contracts are under `task-generations/lifecycle-v2/`. Lifecycle V2 is a series of 7 bounded defect repairs of comparable size, each restoring one named behavior that a specific upstream test already decides, so every task has a closed stopping condition and no single task dominates session cost. Each prompt states the observable symptom without naming the file, function, or test, so locating the defect remains real retrieval work. The controller applies all semantic start patches before prompt 1 and runs controller-only verifiers after the final prompt.
