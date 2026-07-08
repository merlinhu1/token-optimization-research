#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
uv run python - <<'PY'
import os, tempfile
from pathlib import Path
from beets.util import normpath, path_as_posix
from beets.util.units import raw_seconds_short, human_seconds_short
from beets.util.color import color_len
from beets.util.functemplate import template
from beets.util.pathformats import PF_KEY_DEFAULT
assert PF_KEY_DEFAULT == 'default'
assert normpath('.') == os.fsencode(os.path.normpath(os.path.abspath('.')))
assert path_as_posix(b'a\\b') == b'a/b'
assert raw_seconds_short('2:03') == 123.0
assert human_seconds_short(125) == '2:05'
assert color_len('\x1b[31mred\x1b[39;49;00m') == 3
assert template('%upper{$name}').substitute({'name':'bee'}, {'upper': str.upper}) == 'BEE'
PY
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- 'D = TypeVar("D", bound="Database", default=Any)' beets/dbcore/db.py >/dev/null
grep -F -- 'MaybeBytes = TypeVar("MaybeBytes", bytes, None)' beets/dbcore/pathutils.py >/dev/null
grep -F -- '    P = TypeVar("P", default=Any)' beets/dbcore/query.py >/dev/null
grep -F -- '    r"(-|\^)?"  # Negation prefixes.' beets/dbcore/queryparse.py >/dev/null
