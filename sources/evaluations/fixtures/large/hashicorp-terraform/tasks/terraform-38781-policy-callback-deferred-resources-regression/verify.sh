#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
export PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH
go test ./internal/terraform -run "TestContext2(Apply|Plan)_PolicyCallback_(GetDataSource|GetResources_Deferral)" -count=1
