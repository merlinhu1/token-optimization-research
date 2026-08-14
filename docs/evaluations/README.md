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

The active production surface is Lifecycle V1: Fastify and Beets, authentic pre-seeded semantic regressions, normal software-engineering objectives, and controller-only compile scoring. Affected-component and final project-wide compilation are not disclosed in agent prompts. The Lifecycle V1 bare-Codex controls retained accepted r0 and r1 samples per lane. Bare OpenCode retained accepted r1 and r2 samples after its r0 evidence-ingress rejection. Cross-runtime evidence is named and reported as [`accepted-pair-01` and `accepted-pair-02`](design/lifecycle-v1-accepted-replicate-pairing.md), not by matching raw runtime-local `rN` labels. Terraform V1 is rejected historical evidence with no active rerun or treatment path.

RepoWise 0.39.0 is provider-configured qualified on both active fixtures for the official Codex integration and the documented generic MCP surface under OpenCode. The Codex V2 screen completed valid Fastify and Beets lanes at 5,690,107 and 2,326,247 provider tokens (+342.03% and +97.38% versus matched bare Codex; +151.57% and +119.89% on the fresh-input-plus-output view). These single-replicate observations are `eligible_for_ranking: false`; the OpenCode protocols remain prepared but unexecuted. The earlier provider-free generation was invalid and was deleted under its owner-authorized receipt. Any provider-backed RepoWise lane that reports `no-llm-provider` is discarded before registry publication.

The 2026-08-08 OpenCode Lifecycle V1 screen completed eight accepted lanes for Graphify, LeanCTX, Snip, and CodeScope across Fastify and Beets. The two-sequence descriptive weighted deltas versus matched bare OpenCode were Graphify -12.49%, LeanCTX +16.33%, Snip -26.61%, and CodeScope -0.52%. These are single-replicate observations marked `eligible_for_ranking: false`; Cartog was explicitly excluded before provider execution because its pinned native binary did not reproduce the frozen artifact identity. See [`../papers/opencode-four-tool-lifecycle-v1-screen-20260808.md`](../papers/opencode-four-tool-lifecycle-v1-screen-20260808.md).

The direct-Anthropic Claude Code campaigns completed under bounded baseline-only authorizations: `claude-code-anthropic-sonnet-5-high` binds `claude-sonnet-5` with `high` effort and used 897,108.2 weighted units; `claude-code-anthropic-opus-5-high` binds `claude-opus-5` with `high` effort and used 1,167,276.7 weighted units. Opus used 30.12% more weighted token cost than Sonnet, and Sonnet was already 73.85% above matched Codex and 22.71% above matched OpenCode weighted baselines, so treatment experiments continue with Sonnet 5/high; Opus remains baseline-only. Thirteen Fastify treatments are accepted. Versus the 460,555.0-weighted Fastify Claude baseline, RTK, Graphify, Snip, LowFat, Caveman, Token Savior, LeanCTX, jCodeMunch, CodeScope, Serena, Ponytail, SigmaP, and CodeGraph changed weighted usage by -28.02%, -20.08%, -9.82%, -6.14%, -4.23%, +7.50%, +16.14%, +17.10%, +18.92%, +22.22%, +30.86%, +54.35%, and +107.62%. Beets retains RTK and Cartog at +55.02% and +135.20% versus its 436,553.2-weighted baseline. Fastify/Cartog and Fastify/TokenJuice are occupied excluded failures. Thirteen Beets lanes remain unlaunched, so these incomplete observations are not ranking evidence. See the [Sonnet preparation authority](../../sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-protocol-preparation-20260808.json), [qualification receipt](../../sources/evaluations/audits/corrected-integration-qualification-claude-code-anthropic-sonnet-5-high-lifecycle-v1-20260810.json), [treatment authorization](../../sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-treatment-authorization-20260810.json), [Cartog rejection audit](../../sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-cartog-fastify-ingress-rejection-20260808.json), [TokenJuice controller-failure audit](../../sources/evaluations/audits/claude-code-anthropic-sonnet-5-high-lifecycle-v1-tokenjuice-fastify-controller-failure-20260809.json), and [Opus preparation authority](../../sources/evaluations/audits/claude-code-anthropic-opus-5-high-lifecycle-v1-protocol-preparation-20260808.json).

The current Phase 2 Lifecycle V1 report retains 36 accepted treatment sessions across 18 product/runtime conditions, with 108/108 accepted task outcomes across Fastify and Beets. Codex increased weighted usage by 34.01% against its repeated bare-Codex baseline; OpenCode reduced weighted usage by 17.66% against its matched native no-treatment control. LowFat/Codex and Token Savior/OpenCode were blocked before provider spend. The standalone report is [`../papers/phase-2-lifecycle-v1-natural-use-screening.md`](../papers/phase-2-lifecycle-v1-natural-use-screening.md). Earlier lifecycle-v0 screens were retired on 2026-08-14 and are no longer evidence.

Lifecycle V0 and every screen built on it were retired on 2026-08-14 under [`lifecycle-v0-framework-retired-20260814.json`](../../sources/evaluations/audits/lifecycle-v0-framework-retired-20260814.json). Their sessions, artifacts, and protocols are deleted; the reports that describe them are annotated as retired evidence and are not comparison controls for Lifecycle V1.
The successive r1 screen retained a fresh bare OpenCode control at 122,994 raw provider tokens and 66,744.2 weighted units. RTK was +0.38% raw and -10.22% weighted; Graphify +9.16% / +17.62%; CodeGraph +21.82% / +17.22%; SwarmVault +48.88% / +12.60%; and CodeScope +52.79% / +10.79%. All 15 treatment sessions and 45 task verifiers passed. Task-target patches matched bare 45/45, while full task deltas matched 36/45 because SwarmVault retained product wiki state; final Git status matched 6/15 because SwarmVault, Graphify, and CodeGraph retained expected product state. All native integrations activated, but natural-use execution produced no model-issued product-tool calls; Graphify's plugin automatically injected guidance into nine bash calls. The machine-readable single-replicate screening result is `sources/evaluations/audits/opencode-next-five-sol-high-r1-results-20260730.json`.

The following corrected r1 screen retained jCodemunch, LeanCTX, SigMap, Caveman, and LowFat. All five used more weighted tokens than the same fresh bare control: +111.91%, +62.83%, +13.26%, +1.10%, and +18.99%, respectively. The panel retained 15 sessions, 1,098,566 raw provider tokens, and 472,615.4 weighted units. Verifier diagnostics were 43/45 task passes and 14/15 final passes; all three failures occurred in LeanCTX Fastify. LeanCTX generated seven model-issued product calls, while the other treatments recorded zero. All manifests and cumulative usage streams reconciled exactly. See [`../papers/opencode-successive-next-five-r1-screen.md`](../papers/opencode-successive-next-five-r1-screen.md).
