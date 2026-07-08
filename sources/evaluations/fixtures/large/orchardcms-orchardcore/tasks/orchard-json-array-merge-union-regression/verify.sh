#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
DOTNET_ROOT="${DOTNET_ROOT:-/opt/data/dotnet}"; export DOTNET_ROOT PATH="$DOTNET_ROOT:$PATH" DOTNET_SYSTEM_GLOBALIZATION_INVARIANT="${DOTNET_SYSTEM_GLOBALIZATION_INVARIANT:-1}"; "$DOTNET_ROOT/dotnet" test --no-restore --project test/OrchardCore.Tests/OrchardCore.Tests.csproj --filter-class "*HtmlSanitizerTests"
DOTNET_ROOT="${DOTNET_ROOT:-/opt/data/dotnet}"; export DOTNET_ROOT PATH="$DOTNET_ROOT:$PATH" DOTNET_SYSTEM_GLOBALIZATION_INVARIANT="${DOTNET_SYSTEM_GLOBALIZATION_INVARIANT:-1}"; "$DOTNET_ROOT/dotnet" test --no-restore --project test/OrchardCore.Tests/OrchardCore.Tests.csproj --filter-class "*CommandManagerTests"
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- 'namespace OrchardCore.Admin;' src/OrchardCore.Modules/OrchardCore.Admin/AdminThemeService.cs >/dev/null
grep -F -- 'namespace OrchardCore.Admin;' src/OrchardCore.Modules/OrchardCore.Admin/AdminZoneFilter.cs >/dev/null
grep -F -- 'namespace OrchardCore.Admin.Controllers;' src/OrchardCore.Modules/OrchardCore.Admin/Controllers/AdminController.cs >/dev/null
