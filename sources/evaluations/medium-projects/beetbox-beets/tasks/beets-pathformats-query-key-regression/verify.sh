#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
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
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- '__version__ = "2.12.0"' beets/__init__.py >/dev/null
grep -F -- 'if __name__ == "__main__":' beets/__main__.py >/dev/null
grep -F -- '    if name == "current_metadata":' beets/autotag/__init__.py >/dev/null
grep -F -- 'VA_ARTISTS = ("", "various artists", "various", "va", "unknown")' beets/autotag/distance.py >/dev/null
