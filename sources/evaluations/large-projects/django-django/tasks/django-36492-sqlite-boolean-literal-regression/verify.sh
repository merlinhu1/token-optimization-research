#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
. .venv/bin/activate
PYTHONPATH=. python tests/runtests.py lookup.tests.LookupTests.test_exact_booleanfield lookup.tests.LookupTests.test_exact_booleanfield_annotation --verbosity 2
