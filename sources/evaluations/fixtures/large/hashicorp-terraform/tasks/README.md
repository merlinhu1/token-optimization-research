# Terraform lifecycle v0 — active Baseline V5 tasks

1. `terraform-lifecycle-feature-v0` — inspect and restore compilation across two policy-callback files.
2. `terraform-lifecycle-refactor-v0` — inspect and restore compilation across two configuration files.
3. `terraform-lifecycle-review-v0` — inspect and correct a proposed address change until the package compiles.

The active model-facing contracts are under `task-generations/baseline-v5/`. Each task permits normal search and inspection, changes two production files, and exposes only its affected-package compile command. The controller applies all three start patches before prompt 1 and runs all compile verifiers after prompt 3.
