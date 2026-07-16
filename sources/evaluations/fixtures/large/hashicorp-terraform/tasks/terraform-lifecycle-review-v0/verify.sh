#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
repo="${WORKFLOW_REPO:-$PROJECT_DIR/repo}"
original="internal/cloud/backend_tfPolicyEvaluation_test.go"
hidden="internal/cloud/lifecycle_v0_policy_summary_test.go"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/workflow-cloud-tests.XXXXXX")"
restore() {
  for rel in "$original" "$hidden"; do
    if [[ -f "$tmp/$rel" ]]; then mkdir -p "$repo/$(dirname "$rel")"; cp "$tmp/$rel" "$repo/$rel"; else rm -f "$repo/$rel"; fi
  done
  rm -rf "$tmp"
}
trap restore EXIT
for rel in "$original" "$hidden"; do
  if [[ -f "$repo/$rel" ]]; then mkdir -p "$tmp/$(dirname "$rel")"; cp "$repo/$rel" "$tmp/$rel"; fi
  rm -f "$repo/$rel"
done
mkdir -p "$repo/$(dirname "$hidden")"; cp "$PROJECT_DIR/controller-hidden/$hidden" "$repo/$hidden"
cd "$repo"; go test ./internal/cloud -run TestLifecycleV0PolicySummaryCountsRenderedOutcomes -count=1
