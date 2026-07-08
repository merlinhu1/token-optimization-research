#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$PROJECT_DIR/repo"
URL="https://github.com/fastify/fastify.git"
COMMIT="94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd"
mkdir -p "$PROJECT_DIR/runs" "$PROJECT_DIR/tasks"
if [ ! -d "$REPO/.git" ]; then
  rm -rf "$REPO"
  git clone --filter=blob:none --no-checkout "$URL" "$REPO"
fi
GIT=(git -C "$REPO")
"${GIT[@]}" remote set-url origin "$URL"
"${GIT[@]}" reset --hard >/dev/null 2>&1 || true
"${GIT[@]}" clean -fdx
"${GIT[@]}" fetch --depth 1 origin "$COMMIT"
FETCHED="$("${GIT[@]}" rev-parse FETCH_HEAD)"
if [ "$FETCHED" != "$COMMIT" ]; then
  echo "Fetched $FETCHED, expected pinned commit $COMMIT" >&2
  exit 1
fi
"${GIT[@]}" checkout --detach "$COMMIT"
"${GIT[@]}" reset --hard "$COMMIT"
"${GIT[@]}" clean -fdx
(
  cd "$REPO"
  npm install --ignore-scripts --no-audit --no-fund
  )
"${GIT[@]}" status --short
