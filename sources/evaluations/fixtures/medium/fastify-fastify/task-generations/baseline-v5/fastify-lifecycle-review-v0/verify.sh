#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"

# Baseline V5 compile-only acceptance: no semantic tests or source-shape checks.
node --check fastify.js && node --check lib/errors.js
