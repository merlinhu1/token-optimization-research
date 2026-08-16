# Beets Lifecycle V2 fixture

- Upstream: `https://github.com/beetbox/beets.git`
- Snapshot: `9acb1ecff6c7ee0a1e83e3b983c94792345712c5`
- Sequence: `beets-lifecycle-sequence-v1`
- Active generation: `lifecycle-v2`
- Qualification: `qualification-lifecycle-v2-20260816.json`
- Stages: function-template argument splitting → LazyDict iterator refactor → featuring-token review

The controller applies all three semantic regressions before prompt 1. Agents receive normal engineering objectives and are expected to implement them correctly; evaluator scoring and controller commands are not model-facing. The feature seed removes argument-local comma handling, producing a real regression in unescaped argument splitting while escaped commas remain literal. After prompt 3, the controller compiles every affected component, runs one narrow essential-behavior smoke for the feature and refactor tasks, leaves the review task compile-only, and parses every Python source file in the project packages. Broader tests, behavior, style, and source-review quality are diagnostics. The current verifier bytes require a new provider pilot before treatment launch.
