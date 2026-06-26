#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
. .venv/bin/activate
PYTHONPATH=. python tests/runtests.py check_framework.test_mail --verbosity 2
