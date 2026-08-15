# Evaluations

This directory separates evaluation contracts from operator instructions and historical plans.

## Run an evaluation

Start with the generated [operator runbook](operations/runbook.md).

- [Runner reference](operations/runner-reference.md) — command-line and resume details
- [Workflow guide](operations/workflow-guide.md) — the active Lifecycle V1 flows
- [Fixture guide](operations/fixture-guide.md) — fixture layout and preparation

## Understand the design

- [Evaluation framework](design/framework.md) — estimand, eligibility, and interpretation
- [Persistent workflow model](design/workflow-model.md) — why tasks run in one resumed session
- [Result schema](design/result-schema.md) — cumulative result structure
- [Fixture design](design/fixture-design.md) — fixture and verifier contract
- [Lifecycle V1 accepted-replicate pairing](design/lifecycle-v1-accepted-replicate-pairing.md) — canonical cross-runtime pair names and raw-label rules
- [Token and quality policy](design/token-and-quality-policy.md) — provider accounting and diagnostic quality
- [Tool isolation policy](design/tool-isolation-policy.md) — treatment isolation requirements

## Plans and templates

- [`plans/`](plans/) contains phase plans retained for historical context.
- The reusable [evaluation protocol template](../../templates/evaluation-protocol.md) lives with the other repository-wide templates.

## Current evidence

The corrected Lifecycle V1 fixture contract remains active for Fastify and Beets, but the active provider-backed result registry is currently empty. The pre-correction corpus of 103 provider-backed sessions was archived before rerun because the model-facing prompts and shared prompt/configuration generation changed. The archive receipt is [`lifecycle-v1-fastify-beets-results-archived-20260814.json`](../../sources/evaluations/audits/lifecycle-v1-fastify-beets-results-archived-20260814.json).

The corrected no-result baseline protocols are retained as `frozen-ready-not-run` contracts. Their provider-free qualifications are `qualification-lifecycle-v1-20260813.json` under the Fastify and Beets fixture directories. They prove preparation only; they are not effectiveness results. A future corrected-contract baseline and treatment campaign requires fresh provider execution and explicit authorization.

Historical reports and audit receipts remain available for provenance and link to the archived session/protocol paths. They are not current findings or reusable controls for the corrected rerun. Lifecycle V0 remains retired under [`lifecycle-v0-framework-retired-20260814.json`](../../sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json).
