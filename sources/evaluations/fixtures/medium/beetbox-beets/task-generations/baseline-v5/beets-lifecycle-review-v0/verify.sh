#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"

# Baseline V5 compile-only acceptance: no semantic tests or source-shape checks.
uv run --offline --frozen python -m py_compile beetsplug/ftintitle.py beetsplug/duplicates.py
