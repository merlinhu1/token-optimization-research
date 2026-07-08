#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
REPO="$PROJECT_DIR/repo"
COMMIT="8ddae794d30e9984be904f80459614155c6592d9"
URL="https://github.com/beetbox/beets.git"
GIT=(git --git-dir="$REPO/.git" --work-tree="$REPO")
if [ ! -d "$REPO/.git" ] || ! "${GIT[@]}" rev-parse --git-dir >/dev/null 2>&1; then
  rm -rf "$REPO"
  git clone --filter=blob:none --no-checkout "$URL" "$REPO"
  GIT=(git --git-dir="$REPO/.git" --work-tree="$REPO")
else
  "${GIT[@]}" remote set-url origin "$URL"
fi
"${GIT[@]}" reset --hard >/dev/null 2>&1 || true
"${GIT[@]}" clean -fdx
"${GIT[@]}" fetch --depth 1 origin "$COMMIT"
FETCHED="$("${GIT[@]}" rev-parse FETCH_HEAD)"
if [ "$FETCHED" != "$COMMIT" ]; then
  echo "Fetched $FETCHED, expected pinned commit $COMMIT" >&2
  exit 1
fi
"${GIT[@]}" checkout --detach FETCH_HEAD
"${GIT[@]}" reset --hard "$COMMIT"
"${GIT[@]}" clean -fdx
if [ -x "$PROJECT_DIR/setup-deps.sh" ]; then
  bash "$PROJECT_DIR/setup-deps.sh"
fi
(cd "$REPO" && "${GIT[@]}" apply "$TASK_DIR/seed-regression.patch")
"${GIT[@]}" status --short
