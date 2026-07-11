#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${WORKFLOW_REPO:?WORKFLOW_REPO is required}"
test_path=internal/policy/callback/baseline_v2_deferred_test.go
created=0
if [[ ! -f "$test_path" ]]; then mkdir -p "$(dirname "$test_path")"; cp "$TASK_DIR/controller-visible/$test_path" "$test_path"; created=1; fi
trap 'if [[ $created == 1 ]]; then rm -f "$test_path"; fi' EXIT
go test ./internal/policy/callback -run '^TestBaselineV2DeferredDataSource$'
