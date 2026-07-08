# beets-pathformats-query-key-regression

## Fixture

- Project: `beetbox/beets`
- Shared workflow base commit: `8ddae794d30e9984be904f80459614155c6592d9`
- Evidence stage target: `reproduction`
- Task class: `controlled-project-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Restore path-format, config wildcard, hidden-file, byte-format, and ANSI-stripping utility behavior.

Complexity upgrade: this task now requires repairing at least five production files. The verifier exercises every seeded behavior group.

## Seeded start state

Apply `seed-regression.patch` after checking out the shared workflow base commit. The patch creates a controlled broken state in production code while preserving the verifier.

## Agent prompt

- Path: `sources/evaluations/medium-projects/beetbox-beets/tasks/beets-pathformats-query-key-regression/agent-prompt.txt`
- SHA-256: `e84e32c16ab3ff2fffff6232cf3dbb74f8d29aecb8aedd24566692fabcbcb7b8`

## Verifier

```bash
sources/evaluations/medium-projects/beetbox-beets/tasks/beets-pathformats-query-key-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
uv run python - <<'PY'
from pathlib import Path
from beets.util.pathformats import PF_KEY_QUERIES
from beets.util.config import sanitize_choices
from beets.util.hidden import is_hidden
from beets.util.units import human_bytes
from beets.util.color import uncolorize
assert PF_KEY_QUERIES == {"comp": "comp:true", "singleton": "singleton:true"}
assert sanitize_choices(["alpha", "*", "alpha"], ["alpha", "beta", "gamma"]) == ["alpha", "beta", "gamma"]
assert is_hidden(Path('.secret')) is True
assert human_bytes(1024) == '1.0 KiB'
assert uncolorize('\x1b[31mred\x1b[39;49;00m') == 'red'
PY
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the described regression unless explicitly justified.
- The solution addresses project behavior rather than hard-coding only the visible failing assertion.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
