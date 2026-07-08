#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
REPO="$PROJECT_DIR/repo"
COMMIT="91cd8a4bfcaf9cb1388edef6867af2a0b5a0a000"
if [ ! -d "$REPO/.git" ]; then
  echo "Missing repo checkout; run $TASK_DIR/setup.sh first." >&2
  exit 2
fi
git -C "$REPO" reset --hard "$COMMIT"
git -C "$REPO" clean -fdx
git -C "$REPO" status --short
