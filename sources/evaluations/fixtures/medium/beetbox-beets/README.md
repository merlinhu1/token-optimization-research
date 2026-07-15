# beetbox/beets production workflow fixture

Fixture ID: `medium-beetbox-beets`

- Status: active production comparison fixture
- Upstream: `https://github.com/beetbox/beets`
- Pinned snapshot: `9acb1ecff6c7ee0a1e83e3b983c94792345712c5`
- Runtime: Python with `uv`
- Active sequence: `beets-lifecycle-sequence-v1`
- Qualification: `qualification-lifecycle-v1.json`

The active workflow has three sequential task classes: multi-value modify feature implementation, behavior-preserving refactoring of lazy model storage into a `UserDict`-backed abstraction, and review/correction of the authentic pre-merge `ftintitle` metadata-hook change from PR #6726. The missing feature, old storage implementation, and flawed review revision coexist in one concealed composite broken start; prompts are disclosed one at a time, the proposed review patch is disclosed only with task 3, and every verifier runs after the final prompt.

Run preparation with:

```bash
PATH=/opt/data/.local/bin:$PATH python3 scripts/run_sequential_workflow_matrix.py --prepare-only --max-parallel 1 beets-lifecycle-sequence-v1
```

The local `repo/`, dependency caches, and run scratch trees are generated and must not be committed.
