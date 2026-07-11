#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
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
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- '        return f"{self.__class__.__name__}()"' beets/dbcore/sort.py >/dev/null
grep -F -- 'MULTI_VALUE_DELIMITER = "\\␀"' beets/dbcore/types.py >/dev/null
grep -F -- '    "ArchiveImportTask",' beets/importer/__init__.py >/dev/null
grep -F -- '    TRACKS = "TRACKS"' beets/importer/actions.py >/dev/null
