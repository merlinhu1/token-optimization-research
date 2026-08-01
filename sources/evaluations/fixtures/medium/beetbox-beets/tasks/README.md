# Beets lifecycle v0 — active Baseline V5 tasks

1. `beets-lifecycle-feature-v0` — inspect and restore compilation across two utility modules.
2. `beets-lifecycle-refactor-v0` — inspect and restore compilation across two database-core modules.
3. `beets-lifecycle-review-v0` — inspect and correct a proposed plugin change until both modules compile.

The active model-facing contracts are under `task-generations/baseline-v5/`. Each task permits normal search and inspection, changes two production files, and exposes only its affected-component compile command. The controller applies all three start patches before prompt 1 and runs all compile verifiers after prompt 3.
