#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
REPO="$PROJECT_DIR/repo"
COMMIT="91cd8a4bfcaf9cb1388edef6867af2a0b5a0a000"
URL="https://github.com/OrchardCMS/OrchardCore.git"
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
if [ "$FETCHED" != "$COMMIT" ]; then echo "Fetched $FETCHED, expected pinned commit $COMMIT" >&2; exit 1; fi
"${GIT[@]}" checkout --detach FETCH_HEAD
"${GIT[@]}" reset --hard "$COMMIT"
"${GIT[@]}" clean -fdx
bash "$PROJECT_DIR/setup-deps.sh"
(cd "$REPO" && "${GIT[@]}" apply "$TASK_DIR/seed-regression.patch")
"${GIT[@]}" status --short
