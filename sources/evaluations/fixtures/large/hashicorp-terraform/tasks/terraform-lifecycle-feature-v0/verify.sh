#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
repo="${WORKFLOW_REPO:-$PROJECT_DIR/repo}"
rel="internal/policy/callback/lifecycle_v0_deferred_callbacks_test.go"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/workflow-callback-tests.XXXXXX")"
if [[ -f "$repo/$rel" ]]; then mkdir -p "$tmp/$(dirname "$rel")"; cp "$repo/$rel" "$tmp/$rel"; fi
cleanup() { if [[ -f "$tmp/$rel" ]]; then cp "$tmp/$rel" "$repo/$rel"; else rm -f "$repo/$rel"; fi; rm -rf "$tmp"; }
trap cleanup EXIT
mkdir -p "$repo/$(dirname "$rel")"; cp "$PROJECT_DIR/controller-hidden/$rel" "$repo/$rel"
cd "$repo"; go test ./internal/policy/callback -run TestLifecycleV0DeferredCallbacksPreserveState -count=1
