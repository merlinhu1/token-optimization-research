#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$PROJECT_DIR/repo"
if [ ! -d "$REPO/.git" ]; then
  echo "Missing repo checkout; run $PROJECT_DIR/setup.sh first." >&2
  exit 2
fi
(
  cd "$REPO"
  node --test test/schema-validation.test.js
)
