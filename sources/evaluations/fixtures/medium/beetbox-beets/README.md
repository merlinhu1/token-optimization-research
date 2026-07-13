# beetbox/beets production workflow fixture

Fixture ID: `medium-beetbox-beets`

- Status: active production comparison fixture
- Upstream: `https://github.com/beetbox/beets`
- Pinned snapshot: `8ddae794d30e9984be904f80459614155c6592d9`
- Runtime: Python with `uv`
- Active sequence: `beets-maintenance-sequence-v4`
- Qualification: `qualification-composite-v9.json`

The active workflow has three sequential tasks: path-format routing, multivalue metadata, and Tidal synchronization. All seed regressions coexist in one concealed composite broken start, prompts are disclosed one at a time, and cumulative verification runs after the final prompt.

Run preparation with:

```bash
PATH=/opt/data/.local/bin:$PATH python3 scripts/run_sequential_workflow_matrix.py --prepare-only --max-parallel 1 beets-maintenance-sequence-v4
```

The local `repo/`, dependency caches, and run scratch trees are generated and must not be committed.
