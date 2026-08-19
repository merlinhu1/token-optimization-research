# Evaluation fixtures

Runnable fixtures live under `sources/evaluations/fixtures/`. The active Lifecycle V2 portfolio contains:

- Fastify
- Beets

Terraform's V1 r0 result was owner-declared invalid and removed under `sources/evaluations/archive/lifecycle-v1-pre-corrected-prompts-20260813/audits/lifecycle-v1-terraform-invalidated-20260802.json`; it is not runnable. Each active fixture contains a pinned repository snapshot, the ordered Lifecycle V2 semantic-regression task directories under `task-generations/lifecycle-v2/` (6 for Fastify, 7 for Beets), controller-only verifier scripts and acceptance commands, setup/reset helpers, and one generated qualification. Every task gives the agent a normal software-engineering objective, permits repository search and related-code inspection, expects a complete correct implementation, and injects no acceptance-test assets. Evaluator scoring is not disclosed in the prompt. The aggregate verifier compiles every task, runs one narrow essential-behavior smoke for every task, and runs one project-wide compile command after the final prompt. Broader quality evidence remains diagnostic.

Qualification demonstrates fixed/start/composite gate behavior. It does not constitute a production result.
