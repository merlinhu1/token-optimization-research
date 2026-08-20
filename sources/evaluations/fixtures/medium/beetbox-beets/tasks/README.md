# Beets — retired Lifecycle V0 task definitions

The directories here are the Lifecycle V0 task contracts, retained as historical evidence for
the audits and receipts that name them. V0 was retired on 2026-08-14 under
`sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json` and nothing active
runs them: `verify-smoke.sh` now reads the active sequence from `data/workflow-task-sequences.json`.

The active model-facing contracts are under `task-generations/lifecycle-v2/`. The active Lifecycle V2
generation is a series of 6 bounded defect repairs of comparable size, each restoring one named behavior that a
specific upstream test already decides, so every task has a closed stopping condition and no
single task dominates session cost. Each prompt states the observable symptom without naming the
file, function, or test, so locating the defect remains real retrieval work. The controller
applies all semantic start patches before prompt 1 and runs controller-only verifiers after the
final prompt.
