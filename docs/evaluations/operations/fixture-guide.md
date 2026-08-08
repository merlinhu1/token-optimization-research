# Evaluation fixtures

Runnable fixtures live under `sources/evaluations/fixtures/`. The active Lifecycle V1 portfolio contains:

- Fastify
- Beets

Terraform's V1 r0 result was owner-declared invalid and removed under `sources/evaluations/audits/lifecycle-v1-terraform-invalidated-20260802.json`; it is not runnable. Each active fixture contains a pinned repository snapshot, three ordered Lifecycle V1 semantic-regression task directories, controller-only verifier scripts and compile commands, setup/reset helpers, and one generated `qualification-lifecycle-v1.json`. Every task gives the agent a normal software-engineering objective, permits repository search and related-code inspection, expects a complete correct implementation, and injects no acceptance-test assets. Evaluator scoring is not disclosed in the prompt. The aggregate verifier runs the affected-component compile commands and one project-wide compile command after task 3. Component and project compilation are internal pass/fail gates; broader quality evidence remains diagnostic.

Qualification demonstrates fixed/start/composite gate behavior. It does not constitute a production result.
