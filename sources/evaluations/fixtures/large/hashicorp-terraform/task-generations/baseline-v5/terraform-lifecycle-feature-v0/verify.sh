#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"

# Controller-only Baseline V5 compilation assessment. This policy is not model-facing.
export PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH; GOTOOLCHAIN=auto go test -run '^$' ./internal/policy/callback
