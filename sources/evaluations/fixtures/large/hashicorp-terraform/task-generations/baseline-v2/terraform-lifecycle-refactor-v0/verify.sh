#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${WORKFLOW_REPO:?WORKFLOW_REPO is required}"
test_path=internal/configs/baseline_v2_requirement_type_test.go
created=0
if [[ ! -f "$test_path" ]]; then mkdir -p "$(dirname "$test_path")"; cp "$TASK_DIR/controller-visible/$test_path" "$test_path"; created=1; fi
trap 'if [[ $created == 1 ]]; then rm -f "$test_path"; fi' EXIT
mode="${1:-all}"
behavior() { go test ./internal/configs -run '^TestParserLoadConfigDirWithStateMigrations_from_state_store$'; }
structure() { go test ./internal/configs -run '^TestBaselineV2StateStoreRequirementNamedType$'; }
case "$mode" in behavior) behavior;; structure) structure;; all) behavior; structure;; *) exit 2;; esac
