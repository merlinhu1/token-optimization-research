# beets-human-bytes-boundary-regression

## Fixture

- Project: `beetbox/beets`
- Shared workflow base commit: `8ddae794d30e9984be904f80459614155c6592d9`
- Evidence stage target: `reproduction`
- Task class: `controlled-project-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Restore ancestry/component ordering, choice deduplication, BUBBLE filtering, multi-value diff ordering, and long-duration unit scaling.

Complexity upgrade: this task now requires repairing at least five production files. The verifier exercises every seeded behavior group.

## Seeded start state

Apply `seed-regression.patch` after checking out the shared workflow base commit. The patch creates a controlled broken state in production code while preserving the verifier.

## Agent prompt

- Path: `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-human-bytes-boundary-regression/agent-prompt.txt`
- SHA-256: `70244ce6cce9dd6db78bf40230c50603f5436a7e948f3618ed40986047b99cb7`

## Verifier

```bash
sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-human-bytes-boundary-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
uv run python - <<'PY'
from beets.util import ancestry, components
from beets.util.config import sanitize_choices
from beets.util.pipeline import _allmsgs, BUBBLE
from beets.util.diff import _multi_value_diff
from beets.util.units import human_seconds
assert ancestry(b'/a/b/c') == [b'/', b'/a', b'/a/b']
assert components(b'/a/b') == [b'/', b'a', b'b']
assert sanitize_choices(['a','a','*'], ['a','b']) == ['a','b']
assert list(_allmsgs(BUBBLE)) == []
out = _multi_value_diff('tag', {'b','a'}, {'b','c'})
assert '  - a' in out and '  + c' in out
assert human_seconds(120) == '2.0 minutes'
PY
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the described regression unless explicitly justified.
- The solution addresses project behavior rather than hard-coding only the visible failing assertion.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
