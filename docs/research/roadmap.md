# Research roadmap

## Current state

The current execution contract is Lifecycle V2 across Fastify and Beets: 6 bounded defect repairs per lane, each restoring one named behavior a specific upstream test decides, under authentic semantic regressions, normal software-engineering prompts, and lenient controller-only acceptance. Every task compiles and also runs one narrow essential-behavior smoke. Fastify requalified on 2026-08-21 against the repaired prompts; Beets was repinned to 746cecf2 and requalified on 2026-08-22.

The previous provider-backed Lifecycle V1 corpus was archived before rerun because model-facing prompts and shared prompt/configuration identity changed. The archive contains 103 historical sessions, their comparisons, and superseded protocols. They remain immutable evidence for the prior bytes and are not current controls.

Both lanes now carry provider-backed results under the current contract. Four interventions were tried against the Beets lane's earlier 22-31% spread -- shared code region, matched task count, prompt precision, and a repin onto a seed-size-bounded task set -- and the first three did not narrow it; the repinned lane has since been measured directly. Further provider work must be fresh and bound to the current Lifecycle V2 qualification hashes. The forward model policy is GPT-5.6 Sol/medium for Codex CLI and OpenCode, and direct-Anthropic Claude Opus 5/medium for Claude Code. High effort is retired for new work because excess deliberation can increase trajectory divergence.

Registry counts, role splits, and runtime splits live in the generated corpus summary in the top-level [`README.md`](../../README.md) rather than being restated here. What that summary cannot say is what the numbers currently support:

- **The three runtimes are not interchangeable controls.** On Fastify each holds baselines whose weighted token cost differs by more than any treatment effect measured so far, so a treatment is only ever read against a baseline from its own runtime. The cross-runtime numbers describe the runtimes, not the tools.
- **The first treatment is a screen, not an effect estimate.** Caveman holds one replicate per lane on each of Claude Code and Codex. Under [ADR 0009](../architecture/decision-records/0009-replicate-counts-are-chosen-not-registered.md) a single replicate can support "worth carrying forward" and cannot support a ranked effect size. Nothing here is yet a ranking.
- **Caveman changed weighted cost in opposite directions on the two runtimes.** On Claude Code both lanes came in below the whole retained baseline range (Fastify 543,826 against 609,877/657,436; Beets 342,202 against 478,129/444,683). On Codex both came in above it (Fastify 830,055 against a 727,939-822,709 spread; Beets 711,158 against 564,733-614,214). Same tool, same task family, opposite sign. Whatever caveman does, it is not a property of the tool alone, and a result from either runtime must not be reported as caveman's effect without naming the runtime.
- **The Codex arm is the cleaner of the two.** All six verifiers passed on both Codex lanes and on Claude Code Fastify, so those three pairs compare equal work. Claude Code Beets missed task-04, and a run that does less work costs less, so that single largest reduction is the one number here that is confounded and should not be leaned on.
- **On Claude Code the two cost factors moved against each other.** Steps fell well below baseline while weighted cost per step rose (Fastify 52 steps at 10,458 against 71 at 9,260; Beets 36 at 9,506 against 66 at 6,738), so the totals fell on trajectory length rather than on cheaper steps. On Codex Fastify neither factor helped: 72 steps at 11,528 against baselines of 69-76 steps at 9,972-10,970. The r0 baselines predate the step instrumentation, so these step figures compare a treatment r0 against a baseline r1.

The next thing worth spending on is a second caveman replicate per runtime, because the runtime-dependent sign is the claim that most needs a second sample and the one most likely to be trajectory variance.

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
