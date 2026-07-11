#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
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
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- 'V = TypeVar("V")' beets/autotag/hooks.py >/dev/null
grep -F -- '    AnyMatch = TypeVar("AnyMatch", "TrackMatch", "AlbumMatch")' beets/autotag/match.py >/dev/null
grep -F -- '_music_dir_var: ContextVar[bytes] = ContextVar("music_dir", default=b"")' beets/context.py >/dev/null
grep -F -- '    "InvalidQueryError",' beets/dbcore/__init__.py >/dev/null
