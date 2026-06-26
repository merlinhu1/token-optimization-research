#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
DOTNET_ROOT="${DOTNET_ROOT:-/opt/data/dotnet}"; export DOTNET_ROOT PATH="$DOTNET_ROOT:$PATH" DOTNET_SYSTEM_GLOBALIZATION_INVARIANT="${DOTNET_SYSTEM_GLOBALIZATION_INVARIANT:-1}"; "$DOTNET_ROOT/dotnet" test --no-restore --project test/OrchardCore.Tests/OrchardCore.Tests.csproj --filter-class "*Base64Tests"
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- 'namespace OrchardCore.AspireHost;' src/OrchardCore.AspireHost/ClamAV.cs >/dev/null
grep -F -- 'var builder = DistributedApplication.CreateBuilder(args);' src/OrchardCore.AspireHost/Program.cs >/dev/null
grep -F -- 'var builder = WebApplication.CreateBuilder(args);' src/OrchardCore.Cms.Web/Program.cs >/dev/null
grep -F -- 'namespace OrchardCore.Admin;' src/OrchardCore.Modules/OrchardCore.Admin/AdminAreaControllerRouteMapper.cs >/dev/null
