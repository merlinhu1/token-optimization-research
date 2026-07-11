#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${WORKFLOW_REPO:?WORKFLOW_REPO is required}"
test_path=test/util/test_functemplate.py
cmp -s "$TASK_DIR/controller-visible/$test_path" "$test_path" || { printf 'model-visible acceptance test differs from canonical bytes: %s\n' "$test_path" >&2; exit 1; }
uv run --offline --frozen --no-project pytest -q test/util/test_functemplate.py -k 'escaped_sep'
uv run --offline --frozen --no-project ruff format --check beets/util/functemplate.py
