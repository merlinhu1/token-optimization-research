#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
CONTROLLER_DIR="$TASK_DIR/controller-hidden"
if [[ ! -d "$CONTROLLER_DIR" ]]; then CONTROLLER_DIR="$PROJECT_DIR/controller-hidden"; fi
repo="${WORKFLOW_REPO:-$PROJECT_DIR/repo}"
original="internal/cloud/backend_tfPolicyEvaluation_test.go"
hidden="internal/cloud/lifecycle_v0_policy_summary_test.go"
adapter="internal/cloud/lifecycle_v0_policy_summary_adapter_test.go"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/workflow-cloud-tests.XXXXXX")"
restore() {
  for rel in "$original" "$hidden" "$adapter"; do
    if [[ -f "$tmp/$rel" ]]; then
      mkdir -p "$repo/$(dirname "$rel")"
      cp "$tmp/$rel" "$repo/$rel"
    else
      rm -f "$repo/$rel"
    fi
  done
  rm -rf "$tmp"
}
trap restore EXIT
for rel in "$original" "$hidden" "$adapter"; do
  if [[ -f "$repo/$rel" ]]; then
    mkdir -p "$tmp/$(dirname "$rel")"
    cp "$repo/$rel" "$tmp/$rel"
  fi
done
rm -f "$repo/$original"
mkdir -p "$repo/$(dirname "$hidden")"
cp "$CONTROLLER_DIR/$hidden" "$repo/$hidden"
call='return b.renderTFPolicyEvaluations(ctx, run, stages...)'
if grep -Eq 'func \(b \*Cloud\) renderTFPolicyEvaluations\([^)]*,[[:space:]]*_[[:space:]]+bool' "$repo/internal/cloud/backend_tfPolicyEvaluation.go"; then
  call='return b.renderTFPolicyEvaluations(ctx, run, false, stages...)'
fi
printf '%s\n' \
  'package cloud' \
  '' \
  'import (' \
  '    "context"' \
  '    tfe "github.com/hashicorp/go-tfe"' \
  ')' \
  '' \
  'func lifecycleRenderTFPolicyEvaluations(b *Cloud, ctx context.Context, run *tfe.Run, stages ...tfe.TFPolicyEvaluationStageType) error {' \
  "    $call" \
  '}' > "$repo/$adapter"
cd "$repo"
go test ./internal/cloud \
  -run 'TestCloud_(renderTFPolicyEvaluations_pagination|writeTFPolicyEvaluations)|TestLifecycleV0PolicySummaryCountsRenderedOutcomes' \
  -count=1
