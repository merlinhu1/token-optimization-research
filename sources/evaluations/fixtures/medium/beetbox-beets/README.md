# Beets Lifecycle V2 fixture

- Upstream: `https://github.com/beetbox/beets.git`
- Snapshot: `746cecf204a48667dcce8a303272ff2b79dae8a3`
- Sequence: `beets-lifecycle-sequence-v2`
- Active generation: `lifecycle-v2`
- Qualification: `qualification-lifecycle-v2-20260822.json`
- Tasks: 6 bounded defect repairs, each restoring one named behavior a specific upstream test decides

Repinned on 2026-08-22 from `9acb1ecf`, and deliberately 54 commits behind upstream head so the
mining window stays refreshable. Repinning was the fix for candidate scarcity rather than a
refresh: a seed patch is reversed against the pinned tree, so the commits that can become tasks
are the ones close to the pin. At the old snapshot 22 of 26 near-miss candidates failed to apply,
and scanning 2,500 commits yielded four usable tasks; scanning 320 at the new pin yielded six.

Seed patches span 468 to 794 characters, below Fastify's 855. That bound is empirical: across the
previous task set, seed size and between-replicate exploration variance rank-correlated at +1.00,
recorded in
[`beets-lane-variance-diagnosis-20260820.json`](../../../audits/beets-lane-variance-diagnosis-20260820.json).
Whether a tighter seed bound narrows the lane spread is untested; three earlier interventions --
shared code region, matched task count, and prompt precision -- each failed to do so, and none of
them addressed cancellation, which is the property that governs the lane total.

The controller applies all six semantic regressions as one composite start before prompt 1. Agents
receive normal engineering objectives and are expected to implement them correctly; evaluator
scoring and controller commands are not model-facing. Prompts state the observable symptom and
never name the file, function, or test, so locating the defect remains real retrieval work. After
the final prompt, the controller compiles every affected component, runs one narrow upstream
essential-behavior smoke per task, and parses every Python source file in the project packages.
Broader tests, behavior, style, and source-review quality are diagnostics. The current verifier
bytes require a new provider pilot before treatment launch.
