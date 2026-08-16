#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"

# Controller-only Lifecycle V2 acceptance. These upstream cases are a narrow smoke for the
# task's essential behavior; broader checks remain diagnostic.
node --check lib/schema-controller.js &&
  node --test test/internals/schema-controller-perf.test.js
