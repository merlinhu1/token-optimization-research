# Terraform lifecycle v1 — active Lifecycle V1 tasks

1. `terraform-lifecycle-feature-v1` — restore deferred data-source policy callback propagation.
2. `terraform-lifecycle-refactor-v1` — restore the named provider-requirements contract without behavioral drift.
3. `terraform-lifecycle-review-v1` — review and correct input-variable checkable address parsing.

The active model-facing contracts are under `task-generations/lifecycle-v1/`. Each prompt states a complete software objective, permits normal search and related-code inspection, and expects a correct implementation and relevant validation. The controller applies all three semantic start patches before prompt 1 and runs controller-only compile verifiers after prompt 3.
