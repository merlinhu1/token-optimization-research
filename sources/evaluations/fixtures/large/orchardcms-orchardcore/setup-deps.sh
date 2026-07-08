#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$PROJECT_DIR/repo"
DOTNET_ROOT="${DOTNET_ROOT:-/opt/data/dotnet}"
export DOTNET_ROOT PATH="$DOTNET_ROOT:$PATH" DOTNET_SYSTEM_GLOBALIZATION_INVARIANT="${DOTNET_SYSTEM_GLOBALIZATION_INVARIANT:-1}"
"$DOTNET_ROOT/dotnet" restore "$REPO/test/OrchardCore.Tests/OrchardCore.Tests.csproj" >/dev/null
