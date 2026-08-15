#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"

# Controller-only Lifecycle V1 acceptance. The upstream cache tests are a
# narrow smoke for the task's essential behavior; broader checks are diagnostic.
node --check lib/content-type.js && node --test --test-name-pattern='ContentType class cache' test/content-type.test.js
