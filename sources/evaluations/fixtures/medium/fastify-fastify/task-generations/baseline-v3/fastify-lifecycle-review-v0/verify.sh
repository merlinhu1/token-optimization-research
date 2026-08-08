#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"
test_path=test/baseline-v3-max-param.test.js
canonical="$TASK_DIR/controller-visible/$test_path"
created=0
if [[ -f "$test_path" ]]; then
  cmp -s "$canonical" "$test_path" || { printf 'model-visible acceptance test differs from canonical bytes: %s\n' "$test_path" >&2; exit 1; }
else
  [[ "${WORKFLOW_QUALIFICATION_CANONICAL_MATERIALIZATION:-0}" == 1 ]] || { printf 'model-visible acceptance test is missing: %s\n' "$test_path" >&2; exit 1; }
  mkdir -p "$(dirname "$test_path")"
  cp "$canonical" "$test_path"
  created=1
fi
trap 'if [[ $created == 1 ]]; then rm -f "$test_path"; fi' EXIT
node --test "$test_path"
