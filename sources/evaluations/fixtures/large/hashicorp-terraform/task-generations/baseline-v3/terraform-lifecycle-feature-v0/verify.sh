#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${WORKFLOW_REPO:?WORKFLOW_REPO is required}"
export PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH
test_path=internal/policy/callback/baseline_v3_deferred_test.go
canonical="$TASK_DIR/controller-visible/$test_path"
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
go test ./internal/policy/callback -run '^TestBaselineV3DeferredDataSource$'
