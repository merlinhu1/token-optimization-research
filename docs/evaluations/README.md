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
- [Accepted-replicate pairing](design/accepted-replicate-pairing.md) — cross-runtime pair-naming rules, worked on the archived V1 pairs
- [Token and quality policy](design/token-and-quality-policy.md) — provider accounting and diagnostic quality
- [Tool isolation policy](design/tool-isolation-policy.md) — treatment isolation requirements

## Plans and templates

- [`plans/`](plans/) contains phase plans retained for historical context.
- The reusable [evaluation protocol template](../../templates/evaluation-protocol.md) lives with the other repository-wide templates.

## Current evidence

The Lifecycle V2 fixture contract is active for Fastify and Beets, and both lanes hold provider-backed results under it. Beets was repinned on 2026-08-22 from 9acb1ecf to 746cecf2 to reach a minable window of upstream history; its pre-repin baselines are archived as incompatible controls and it was rebaselined afterwards. The pre-correction corpus of 103 provider-backed sessions was archived before rerun because the model-facing prompts and shared prompt/configuration generation changed. The archive receipt is [`lifecycle-v1-fastify-beets-results-archived-20260814.json`](../../sources/evaluations/audits/lifecycle-v1-fastify-beets-results-archived-20260814.json). Registry counts live in the generated corpus summary in [`sources/evaluations/README.md`](../../sources/evaluations/README.md).

Each runtime carries its own baselines, and a treatment is read only against a baseline from its own runtime: the Fastify baselines differ across runtimes by more than any treatment effect measured so far, so a cross-runtime pairing would attribute the runtime to the tool. Provider-free qualifications are `qualification-lifecycle-v2-20260821.json` (Fastify) and `qualification-lifecycle-v2-20260822.json` (Beets) under the fixture directories; they prove preparation only and are never an effectiveness result. Codex CLI and OpenCode runs use GPT-5.6 Sol/medium; Claude Code runs use direct-Anthropic Claude Opus 5/medium. The preceding unexecuted High-effort, compile-only, and raw-metric protocol bytes were superseded and archived.

Treatment evidence so far is a screen rather than a ranking. Where a profile holds one replicate per lane, that replicate can support "worth carrying forward" and cannot support an effect size or an ordering against another tool ([ADR 0009](../architecture/decision-records/0009-replicate-counts-are-chosen-not-registered.md)). Report the replicate count with any comparison drawn from this corpus.

Historical reports and audit receipts remain available for provenance and link to the archived session/protocol paths. They are not current findings or reusable controls for the Lifecycle V2 rerun. Lifecycle V0 remains retired under [`lifecycle-v0-framework-retired-20260814.json`](../../sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json).
