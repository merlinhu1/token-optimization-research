# Beets lifecycle v0 fixture

- Upstream: `https://github.com/beetbox/beets.git`
- Snapshot: `9acb1ecff6c7ee0a1e83e3b983c94792345712c5`
- Sequence: `beets-lifecycle-sequence-v0`
- Active generation: `baseline-v5`
- Qualification: `qualification-lifecycle-v0-baseline-v5.json`
- Stages: utility feature compilation → database refactor compilation → plugin review compilation

The controller applies all three Baseline V5 production seeds before prompt 1, evaluates all three affected-component compile commands after prompt 3, and then parses every Python source file in the project packages. Component and final project compilation are the sole pass/fail gates; tests, behavior, style, and source-review quality are diagnostics only.
