#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
REPO="$PROJECT_DIR/repo"
COMMIT="b4e933dd73ba8d4be04f1613808b53d5e129957c"
URL="https://github.com/hashicorp/terraform.git"

GIT=(git --git-dir="$REPO/.git" --work-tree="$REPO")
if [ ! -d "$REPO/.git" ] || ! "${GIT[@]}" rev-parse --git-dir >/dev/null 2>&1; then
  rm -rf "$REPO/.git"
  mkdir -p "$REPO"
  find "$REPO" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
  git init "$REPO"
  GIT=(git --git-dir="$REPO/.git" --work-tree="$REPO")
  "${GIT[@]}" remote add origin "$URL"
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
(cd "$REPO" && "${GIT[@]}" apply "$TASK_DIR/seed-regression.patch")
"${GIT[@]}" status --short
