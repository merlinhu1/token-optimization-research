#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
bash "$PROJECT_DIR/setup.sh"
REPO="$PROJECT_DIR/repo"
git -C "$REPO" apply --3way "$TASK_DIR/seed-regression.patch"
if git -C "$REPO" diff --name-only --diff-filter=U | grep -q .; then
  git -C "$REPO" reset --hard HEAD
  echo "Seed patch produced merge conflicts" >&2
  exit 1
fi
git -C "$REPO" status --short
