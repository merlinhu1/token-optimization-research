# Beets Lifecycle V2 fixture

- Upstream: `https://github.com/beetbox/beets.git`
- Snapshot: `9acb1ecff6c7ee0a1e83e3b983c94792345712c5`
- Sequence: `beets-lifecycle-sequence-v2`
- Active generation: `lifecycle-v2`
- Qualification: `qualification-lifecycle-v2-20260821.json`
- Tasks: 6 bounded defect repairs, each restoring one named behavior a specific upstream test decides

Every task is drawn from the `beets/` core package -- `library/`, `autotag/`, `ui/`, and the plugin
dispatch modules -- rather than from independent `beetsplug/` plugins. That is deliberate. Baselines
of the previous seven-plugin set reproduced to 31.3% at three replicates against 1.7% for Fastify,
and the diagnosis in
[`beets-lane-variance-diagnosis-20260820.json`](../../../audits/beets-lane-variance-diagnosis-20260820.json)
attributes that to accumulated context never re-converging: consecutive tasks in unrelated plugins
each pull in material no other task needs, so an early divergence is inherited by every later task
instead of washing out. Tasks in one shared region should let the context an agent reads amortise.
Whether it does is an open question this fixture exists to answer; the earlier baselines are
archived under `sources/evaluations/archive/lifecycle-v2-beets-plugin-tasks-20260820/` and are not
compatible controls.

The controller applies all six semantic regressions as one composite start before prompt 1. Agents
receive normal engineering objectives and are expected to implement them correctly; evaluator
scoring and controller commands are not model-facing. Prompts state the observable symptom and
never name the file, function, or test, so locating the defect remains real retrieval work. After
the final prompt, the controller compiles every affected component, runs one narrow upstream
essential-behavior smoke per task, and parses every Python source file in the project packages.
Broader tests, behavior, style, and source-review quality are diagnostics. The current verifier
bytes require a new provider pilot before treatment launch.

Six prompts across the two lanes were rewritten on 2026-08-21 after measuring how differently an agent explores when handed the same prompt. Exploration variance tracked prompt precision: the tightest task reproduced to 0.2% while two poorly specified ones reached 57% and 39%. The repaired prompts state one required change, describe a symptom that could not fit another part of the project, and name a recognisable defect shape, all without naming a file, symbol or test. Baselines of the previous bytes are archived under `sources/evaluations/archive/lifecycle-v2-pre-prompt-repair-20260821/` and are not compatible controls.
