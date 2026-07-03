#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
repo="${WORKFLOW_REPO:-$PROJECT_DIR/repo}"
target="test/controller_hidden/lifecycle/test_ftintitle_review.py"
mkdir -p "$repo/$(dirname "$target")"
cp "$TASK_DIR/controller-hidden/$target" "$repo/$target"
trap 'rm -f "$repo/$target"' EXIT
cd "$repo"
uv run --offline --frozen --no-project ruff check beetsplug/ftintitle.py
uv run --offline --frozen --no-project pytest -q \
  test/plugins/test_ftintitle.py \
  "$target"
