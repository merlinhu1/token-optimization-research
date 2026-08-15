#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"

# Controller-only Lifecycle V1 acceptance. The upstream test is a narrow smoke
# for the task's essential behavior; broader quality checks remain diagnostic.
node --check lib/request.js && node --test test/request-media-type.test.js
