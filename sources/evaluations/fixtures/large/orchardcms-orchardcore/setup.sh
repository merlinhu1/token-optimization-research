#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$PROJECT_DIR/repo"
URL="https://github.com/OrchardCMS/OrchardCore.git"
COMMIT="91cd8a4bfcaf9cb1388edef6867af2a0b5a0a000"
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
  DOTNET_ROOT="${DOTNET_ROOT:-/opt/data/dotnet}"
  export DOTNET_ROOT
  export PATH="$DOTNET_ROOT:$PATH"
  export DOTNET_SYSTEM_GLOBALIZATION_INVARIANT="${DOTNET_SYSTEM_GLOBALIZATION_INVARIANT:-1}"
  if [ ! -x "$DOTNET_ROOT/dotnet" ]; then
    echo "Missing .NET SDK at $DOTNET_ROOT/dotnet; install 10.0.200 before qualification." >&2
    exit 2
  fi
  "$DOTNET_ROOT/dotnet" --info | sed -n '1,35p'
  )
"${GIT[@]}" status --short
