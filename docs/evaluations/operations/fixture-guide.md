# Evaluation fixtures

Runnable fixtures live under `sources/evaluations/fixtures/`. The sole active portfolio is lifecycle v0:

- Fastify
- Beets
- Terraform

Each fixture contains a pinned repository snapshot, three ordered Baseline V5 compile-repair task directories, controller-only verifier scripts, setup/reset helpers, and one generated `qualification-lifecycle-v0-baseline-v5.json`. Every task seeds two production files, exposes its affected-component compile command, permits normal repository search and inspection, and injects no acceptance-test assets. The aggregate verifier additionally runs one project-wide compile command after task 3. Component and final project compilation are the only pass/fail gates; broader quality remains diagnostic.

Qualification demonstrates fixed/start/composite gate behavior. It does not constitute a production result.
