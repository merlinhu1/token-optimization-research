#!/usr/bin/env bash
set -euo pipefail
repo="${WORKFLOW_REPO:-${1:-$(pwd)}}"
mode="${2:-${1:-all}}"
if [[ "$mode" == "$repo" ]]; then mode=all; fi
behavior() {
  target="$repo/test/controller_hidden/lifecycle/test_lazy_model_storage_refactor.py"
  mkdir -p "$(dirname "$target")"
  cp "$(dirname "$0")/controller-hidden/test/controller_hidden/lifecycle/test_lazy_model_storage_refactor.py" "$target"
  trap 'rm -f "$target"' EXIT
  (cd "$repo" && uv run --offline --frozen --no-project pytest -q test/controller_hidden/lifecycle/test_lazy_model_storage_refactor.py)
}
structure() {
  (cd "$repo" && uv run --offline --frozen --no-project python - <<'PY'
from collections import UserDict
from beets.dbcore import db
assert hasattr(db, "LazyDict")
assert issubclass(db.LazyDict, UserDict)
assert not hasattr(db, "LazyConvertDict")
assert not hasattr(db.Model, "_awaken")
print("lazy-model-storage-structure-ok")
PY
  )
}
case "$mode" in
  behavior) behavior ;;
  structure) structure ;;
  all) behavior; structure ;;
  *) echo "usage: verify.sh [repo] [behavior|structure|all]" >&2; exit 2 ;;
esac
