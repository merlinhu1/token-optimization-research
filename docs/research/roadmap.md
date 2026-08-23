# Research roadmap

## Current state

The current execution contract is Lifecycle V2 across Fastify and Beets: 6 bounded defect repairs per lane, each restoring one named behavior a specific upstream test decides, under authentic semantic regressions, normal software-engineering prompts, and lenient controller-only acceptance. Every task compiles and also runs one narrow essential-behavior smoke. Fastify requalified on 2026-08-21 against the repaired prompts; Beets was repinned to 746cecf2 and requalified on 2026-08-22.

The previous provider-backed Lifecycle V1 corpus was archived before rerun because model-facing prompts and shared prompt/configuration identity changed. The archive contains 103 historical sessions, their comparisons, and superseded protocols. They remain immutable evidence for the prior bytes and are not current controls.

Both lanes now carry provider-backed results under the current contract. Four interventions were tried against the Beets lane's earlier 22-31% spread -- shared code region, matched task count, prompt precision, and a repin onto a seed-size-bounded task set -- and the first three did not narrow it; the repinned lane has since been measured directly. Further provider work must be fresh and bound to the current Lifecycle V2 qualification hashes. The forward model policy is GPT-5.6 Sol/medium for Codex CLI and OpenCode, and direct-Anthropic Claude Opus 5/medium for Claude Code. High effort is retired for new work because excess deliberation can increase trajectory divergence.

Registry counts, role splits, and runtime splits live in the generated corpus summary in the top-level [`README.md`](../../README.md) rather than being restated here. What that summary cannot say is what the numbers currently support:

- **The three runtimes are not interchangeable controls.** On Fastify each holds baselines whose weighted token cost differs by more than any treatment effect measured so far, so a treatment is only ever read against a baseline from its own runtime. The cross-runtime numbers describe the runtimes, not the tools.
- **The first treatment is a screen, not an effect estimate.** Caveman holds one replicate per lane on Claude Code. Under [ADR 0009](../architecture/decision-records/0009-replicate-counts-are-chosen-not-registered.md) a single replicate can support "worth carrying forward" and cannot support a ranked effect size. Nothing here is yet a ranking.
- **The two cost factors moved in opposite directions for caveman, which is the interesting part.** Both lanes came in well below their Claude Code baselines on agent steps and above them on weighted cost per step: Fastify 52 steps at 10,458 against a baseline 71 at 9,260, Beets 36 at 9,506 against a baseline 66 at 6,738. The totals fell because the step reduction was the larger move. Read this cautiously -- the r0 baselines predate the step instrumentation, so the step figures compare a treatment r0 against a baseline r1, and one replicate cannot separate a real shortening from trajectory variance. It is a hypothesis for the next replicate, not a finding.

## Archived evidence

The archived corpus is [`lifecycle-v1-pre-corrected-prompts-20260813/`](../../sources/evaluations/archive/lifecycle-v1-pre-corrected-prompts-20260813/).

Historical papers and audit receipts remain for provenance. Their results must not be presented as current Lifecycle V2 findings or reused as controls for the rerun.

## Next research step

1. Preserve the current Fastify and Beets fixture, qualification, and protocol bytes.
2. Do not reopen or reuse any archived provider identity.
3. Obtain explicit authorization for fresh Lifecycle V2 baseline execution.
4. Run the Lifecycle V2 baseline lanes first, serially, and publish their accepted evidence.
5. Freeze compatible treatment protocols only after the Lifecycle V2 baseline/pilot gates pass.
6. Run future treatments only against the new Lifecycle V2 controls, retaining prompt/configuration hashes in every result.
7. Use weighted token cost as the sole token metric and keep correctness/quality as separate diagnostics; never publish a raw-token comparison.
