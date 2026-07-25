#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"
export PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH
test_path=internal/configs/baseline_v3_requirement_type_test.go
canonical="$TASK_DIR/controller-visible/$test_path"
upstream_test_path=internal/configs/parser_config_dir_test.go
cmp -s "$TASK_DIR/controller-visible/$upstream_test_path" "$upstream_test_path" || { printf 'model-visible upstream acceptance test differs from canonical bytes: %s\n' "$upstream_test_path" >&2; exit 1; }
created=0
if [[ -f "$test_path" ]]; then
  cmp -s "$canonical" "$test_path" || { printf 'model-visible acceptance test differs from canonical bytes: %s\n' "$test_path" >&2; exit 1; }
else
  [[ "${WORKFLOW_QUALIFICATION_CANONICAL_MATERIALIZATION:-0}" == 1 ]] || { printf 'model-visible acceptance test is missing: %s\n' "$test_path" >&2; exit 1; }
  mkdir -p "$(dirname "$test_path")"
  cp "$canonical" "$test_path"
  created=1
fi
trap 'if [[ $created == 1 ]]; then rm -f "$test_path"; fi' EXIT
mode="${1:-all}"
behavior() { go test ./internal/configs -run '^TestParserLoadConfigDirWithStateMigrations_from_state_store$'; }
structure() { go test ./internal/configs -run '^TestBaselineV3StateStoreRequirementNamedType$'; }
case "$mode" in behavior) behavior;; structure) structure;; all) behavior; structure;; *) exit 2;; esac
