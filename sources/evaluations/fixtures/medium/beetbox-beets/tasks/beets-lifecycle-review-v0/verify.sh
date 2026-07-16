#!/usr/bin/env bash
set -euo pipefail
repo="${WORKFLOW_REPO:-${1:-$(pwd)}}"
target="$repo/test/controller_hidden/lifecycle/test_ftintitle_review.py"
mkdir -p "$(dirname "$target")"
cp "$(dirname "$0")/controller-hidden/test/controller_hidden/lifecycle/test_ftintitle_review.py" "$target"
trap 'rm -f "$target"' EXIT
cd "$repo"
uv run --offline --frozen --no-project pytest -q test/controller_hidden/lifecycle/test_ftintitle_review.py
