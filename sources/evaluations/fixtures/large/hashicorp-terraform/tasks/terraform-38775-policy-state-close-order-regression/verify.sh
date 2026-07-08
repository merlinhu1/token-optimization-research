#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
export PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH
go test ./internal/command ./internal/terraform -run "TestApply_PolicyResultsJSON_WithSavedPlan|TestApplyGraphBuilder_PolicyClient|TestPlanGraphBuilder_PolicyClient" -count=1
