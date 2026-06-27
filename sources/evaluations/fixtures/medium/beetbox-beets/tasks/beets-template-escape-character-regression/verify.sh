#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
uv run python - <<'PY'
from pathlib import Path
from beets.util.config import sanitize_pairs, UnknownPairError
from beets.util.hidden import is_hidden
from beets.util import displayable_path
from beets.util.pipeline import mutator_stage
from beets.util.functemplate import template
try:
    sanitize_pairs([('artist','missing')], [('artist','name')], raise_on_unknown=True)
except UnknownPairError:
    pass
else:
    raise AssertionError('expected UnknownPairError')
assert is_hidden(b'.hidden') is True
assert displayable_path([b'a', b'b'], separator='|') == 'a|b'
@mutator_stage
def set_x(item): item['x']=1
c=set_x(); next(c); assert c.send({}) == {'x':1}
assert template('cost $$5 $name').substitute({'name':'Bee'}) == 'cost $5 Bee'
PY
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- 'log = logging.getLogger("beets")' beets/importer/session.py >/dev/null
grep -F -- 'log = logging.getLogger("beets")' beets/importer/stages.py >/dev/null
grep -F -- 'log = logging.getLogger("beets")' beets/importer/state.py >/dev/null
grep -F -- 'log = logging.getLogger("beets")' beets/importer/tasks.py >/dev/null
