# Evaluations

This directory separates evaluation contracts from operator instructions and historical plans.

**Metric authority:** weighted token cost (`fresh input + 0.1 × cached input + 6 × output`) is
the sole token metric. Raw provider counters may exist in evidence for calculation and audit, but
must never be presented, compared, ranked, or interpreted as a result.

## Run an evaluation

Start with the generated [operator runbook](operations/runbook.md).

- [Runner reference](operations/runner-reference.md) — command-line and resume details
- [Workflow guide](operations/workflow-guide.md) — the active Lifecycle V2 flows
- [Fixture guide](operations/fixture-guide.md) — fixture layout and preparation

## Understand the design

- [Evaluation framework](design/framework.md) — estimand, eligibility, and interpretation
- [Persistent workflow model](design/workflow-model.md) — why tasks run in one resumed session
- [Result schema](design/result-schema.md) — cumulative result structure
- [Fixture design](design/fixture-design.md) — fixture and verifier contract
- [Lifecycle V1 accepted-replicate pairing](design/lifecycle-v1-accepted-replicate-pairing.md) — cross-runtime pair-naming rules, worked on the archived V1 pairs
- [Token and quality policy](design/token-and-quality-policy.md) — provider accounting and diagnostic quality
- [Tool isolation policy](design/tool-isolation-policy.md) — treatment isolation requirements

## Plans and templates

- [`plans/`](plans/) contains phase plans retained for historical context.
- The reusable [evaluation protocol template](../../templates/evaluation-protocol.md) lives with the other repository-wide templates.

## Current evidence

The Lifecycle V2 fixture contract is active for Fastify and Beets. The result registry holds three accepted Fastify baseline replicates, r0 to r2, median 678,873.4 weighted with a 1.7% spread. Beets holds none: its lane was rebuilt on 2026-08-20 onto beets/ core tasks and its earlier plugin-set baselines are archived as incompatible controls. The pre-correction corpus of 103 provider-backed sessions was archived before rerun because the model-facing prompts and shared prompt/configuration generation changed. The archive receipt is [`lifecycle-v1-fastify-beets-results-archived-20260814.json`](../../sources/evaluations/audits/lifecycle-v1-fastify-beets-results-archived-20260814.json).

The current no-result baseline protocols are retained as `frozen-ready-not-run` contracts under the forward GPT-5.6 Sol/medium condition. Their provider-free qualifications are `qualification-lifecycle-v2-20260818.json` (Fastify) and `qualification-lifecycle-v2-20260816.json` (Beets) under the fixture directories. They prove preparation only; they are not effectiveness results. The preceding unexecuted High-effort, compile-only, and raw-metric protocol bytes were superseded and archived. New OpenCode runs also use GPT-5.6 Sol/medium; new Claude Code runs use direct-Anthropic Claude Opus 5/medium. A future current-contract baseline and treatment campaign requires fresh provider execution and explicit authorization.

Historical reports and audit receipts remain available for provenance and link to the archived session/protocol paths. They are not current findings or reusable controls for the Lifecycle V2 rerun. Lifecycle V0 remains retired under [`lifecycle-v0-framework-retired-20260814.json`](../../sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json).
