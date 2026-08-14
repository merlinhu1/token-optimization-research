# Beets Lifecycle V1 fixture

- Upstream: `https://github.com/beetbox/beets.git`
- Snapshot: `9acb1ecff6c7ee0a1e83e3b983c94792345712c5`
- Sequence: `beets-lifecycle-sequence-v1`
- Active generation: `lifecycle-v1`
- Qualification: `qualification-lifecycle-v1-20260813.json`
- Stages: function-template argument splitting → LazyDict iterator refactor → featuring-token review

The controller applies all three semantic regressions before prompt 1. Agents receive normal engineering objectives, focused-check guidance, and are expected to implement them correctly; evaluator scoring and compile commands are not model-facing. The feature seed now removes argument-local comma handling, producing a real regression in unescaped argument splitting while escaped commas remain literal. After prompt 3, the controller runs all affected-component compile commands and parses every Python source file in the project packages. Component and final project compilation are the internal pass/fail gates; tests, behavior, style, and source-review quality are diagnostics. The corrected task bytes require a new provider pilot before treatment launch.
