#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$PROJECT_DIR/repo"
URL="https://github.com/beetbox/beets.git"
COMMIT="746cecf204a48667dcce8a303272ff2b79dae8a3"
mkdir -p "$PROJECT_DIR/runs"
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
  uv sync --group test --frozen
  )
"${GIT[@]}" status --short
