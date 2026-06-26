# beets-template-escape-character-regression

## Fixture

- Project: `beetbox/beets`
- Shared workflow base commit: `8ddae794d30e9984be904f80459614155c6592d9`
- Evidence stage target: `reproduction`
- Task class: `controlled-project-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Restore config pair validation, hidden-byte path decoding, POSIX path display, pipeline mutator return semantics, and template escaping.

Complexity upgrade: this task now requires repairing at least five production files. The verifier exercises every seeded behavior group.

## Seeded start state

Apply `seed-regression.patch` after checking out the shared workflow base commit. The patch creates a controlled broken state in production code while preserving the verifier.

## Agent prompt

- Path: `sources/evaluations/medium-projects/beetbox-beets/tasks/beets-template-escape-character-regression/agent-prompt.txt`
- SHA-256: `d3795c0992aeabf59d2cde7fda04df0629821738245454902ec882580c1b3d47`

## Verifier

```bash
sources/evaluations/medium-projects/beetbox-beets/tasks/beets-template-escape-character-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
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
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the described regression unless explicitly justified.
- The solution addresses project behavior rather than hard-coding only the visible failing assertion.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
