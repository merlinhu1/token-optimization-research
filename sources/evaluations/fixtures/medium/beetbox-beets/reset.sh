#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$PROJECT_DIR/repo"
COMMIT="9acb1ecff6c7ee0a1e83e3b983c94792345712c5"
if [ ! -d "$REPO/.git" ]; then
  echo "Missing repo checkout; run $PROJECT_DIR/setup.sh first." >&2
  exit 2
fi
git -C "$REPO" reset --hard "$COMMIT"
git -C "$REPO" clean -fdx
git -C "$REPO" status --short
