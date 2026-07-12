# Evaluation fixtures

Runnable fixtures live under `sources/evaluations/fixtures/`. The sole active portfolio is lifecycle v0:

- Fastify
- Beets
- Terraform

Each fixture contains a pinned repository checkout, three ordered lifecycle task directories, controller-only verifier scripts and canonical integrity copies, setup/reset helpers, and one generated `qualification-lifecycle-v0.json`. The historical Baseline V2 and active Baseline V3 zero-mistake generations keep every required focused acceptance behavior and test model-visible; the canonical copies only prove that those visible bytes were not altered before final verification.

Qualification demonstrates fixed/start/composite gate behavior. It does not constitute a production result.
