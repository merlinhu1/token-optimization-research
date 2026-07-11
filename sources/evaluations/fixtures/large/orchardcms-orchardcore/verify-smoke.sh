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
  DOTNET_ROOT="${DOTNET_ROOT:-/opt/data/dotnet}"
  export DOTNET_ROOT
  export PATH="$DOTNET_ROOT:$PATH"
  export DOTNET_SYSTEM_GLOBALIZATION_INVARIANT="${DOTNET_SYSTEM_GLOBALIZATION_INVARIANT:-1}"
  "$DOTNET_ROOT/dotnet" test --project test/OrchardCore.Tests/OrchardCore.Tests.csproj --list-tests
)
