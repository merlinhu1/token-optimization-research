# beets-hidden-dotfile-regression

## Fixture

- Project: `beetbox/beets`
- Shared workflow base commit: `8ddae794d30e9984be904f80459614155c6592d9`
- Evidence stage target: `reproduction`
- Task class: `controlled-project-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Restore filesystem traversal, pipeline message expansion, template unknown-symbol preservation, pair wildcard expansion, and small numeric diff tolerance.

Complexity upgrade: this task now requires repairing at least five production files. The verifier exercises every seeded behavior group.

## Seeded start state

Apply `seed-regression.patch` after checking out the shared workflow base commit. The patch creates a controlled broken state in production code while preserving the verifier.

## Agent prompt

- Path: `sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-hidden-dotfile-regression/agent-prompt.txt`
- SHA-256: `f73e8b09040aa268510bb0bd814d60b5aa44b0d8c404f7aae41ddb9d9efd18dc`

## Verifier

```bash
sources/evaluations/fixtures/medium/beetbox-beets/tasks/beets-hidden-dotfile-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
uv run python - <<'PY'
import tempfile
from pathlib import Path
from beets.util import sorted_walk
from beets.util.pipeline import _allmsgs, multiple
from beets.util.functemplate import template
from beets.util.config import sanitize_pairs
from beets.util.diff import _field_diff
class M(dict):
    def get(self,k,d=None): return dict.get(self,k,d)
class F(dict):
    def __init__(self, model, **vals): super().__init__(vals); self.model=model
with tempfile.TemporaryDirectory() as d:
    p=Path(d); (p/'B.txt').write_text('b'); (p/'a.txt').write_text('a')
    rows=list(sorted_walk(p))
    assert rows[0][2] == [b'a.txt', b'B.txt']
assert list(_allmsgs(multiple([1,2,3]))) == [1,2,3]
assert template('$missing').substitute({}) == '$missing'
assert sanitize_pairs([('artist','*')], [('artist','name'),('album','title')]) == [('artist','name')]
assert _field_diff('score', F(M(score=1.0), score='1.00'), F(M(score=1.005), score='1.00')) is None
PY
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the described regression unless explicitly justified.
- The solution addresses project behavior rather than hard-coding only the visible failing assertion.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
