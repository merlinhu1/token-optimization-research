#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
REPO="$PROJECT_DIR/repo"
COMMIT="94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd"
if [ ! -d "$REPO/.git" ]; then
  echo "Missing repo checkout; run $TASK_DIR/setup.sh first." >&2
  exit 2
fi
git -C "$REPO" reset --hard "$COMMIT"
git -C "$REPO" clean -fdx
git -C "$REPO" status --short
