#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"

# Controller-only Lifecycle V2 acceptance. These upstream cases are a narrow smoke for the
# task's essential behavior; broader checks remain diagnostic.
uv run --offline --frozen python -m py_compile beetsplug/lyrics.py &&
  uv run --offline --frozen pytest -q test/plugins/test_lyrics.py
