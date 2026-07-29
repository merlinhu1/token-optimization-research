#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"

# Baseline V5 compile-only acceptance: no semantic tests or source-shape checks.
export PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH; GOTOOLCHAIN=auto go test -run '^$' ./internal/policy/callback
