# Terraform lifecycle v0 — active Baseline V3 tasks

1. `terraform-lifecycle-feature-v0` — propagate the existing deferred flag into the callback response.
2. `terraform-lifecycle-refactor-v0` — restore the named provider requirements type.
3. `terraform-lifecycle-review-v0` — restore the `var` input-variable address prefix.

The active model-facing contracts are under `task-generations/baseline-v3/`. The controller applies all three start patches before prompt 1 and runs all verifiers after prompt 3.
