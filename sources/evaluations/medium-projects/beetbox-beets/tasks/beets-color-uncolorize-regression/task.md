# beets-color-uncolorize-regression

## Fixture

- Project: `beetbox/beets`
- Shared workflow base commit: `8ddae794d30e9984be904f80459614155c6592d9`
- Evidence stage target: `reproduction`
- Task class: `controlled-project-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Restore path normalization, path separator conversion, short time parsing/formatting, ANSI-aware color length, and template function evaluation.

Complexity upgrade: this task now requires repairing at least five production files. The verifier exercises every seeded behavior group.

## Seeded start state

Apply `seed-regression.patch` after checking out the shared workflow base commit. The patch creates a controlled broken state in production code while preserving the verifier.

## Agent prompt

- Path: `sources/evaluations/medium-projects/beetbox-beets/tasks/beets-color-uncolorize-regression/agent-prompt.txt`
- SHA-256: `c81d0a84ea8cb3f5b757ce8b7c0a3fb1131139715d4206c6d1f5606baa3859b7`

## Verifier

```bash
sources/evaluations/medium-projects/beetbox-beets/tasks/beets-color-uncolorize-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
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
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the described regression unless explicitly justified.
- The solution addresses project behavior rather than hard-coding only the visible failing assertion.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
