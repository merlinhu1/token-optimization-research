# Beets lifecycle v0 fixture

- Upstream: `https://github.com/beetbox/beets.git`
- Snapshot: `9acb1ecff6c7ee0a1e83e3b983c94792345712c5`
- Sequence: `beets-lifecycle-sequence-v0`
- Active generation: `baseline-v5`
- Qualification: `qualification-lifecycle-v0-baseline-v5.json`
- Stages: escaped function-template separators → LazyDict iterator refactor → featuring-token review

The controller applies all three semantic regressions before prompt 1. Agents receive normal engineering objectives and are expected to implement them correctly; evaluator scoring and compile commands are not model-facing. After prompt 3, the controller runs all affected-component compile commands and parses every Python source file in the project packages. Component and final project compilation are the internal pass/fail gates; tests, behavior, style, and source-review quality are diagnostics.
