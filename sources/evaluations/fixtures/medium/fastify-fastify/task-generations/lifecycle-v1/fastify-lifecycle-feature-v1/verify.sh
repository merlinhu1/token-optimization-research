#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"

# Controller-only Lifecycle V1 compilation assessment. This policy is not model-facing.
node --check lib/request.js
