#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"

# Controller-only Lifecycle V1 acceptance. These upstream cases are a narrow
# smoke for the task's essential behavior; broader checks remain diagnostic.
uv run --offline --frozen python -m py_compile beets/util/functemplate.py &&
  uv run --offline --frozen pytest -q test/util/test_functemplate.py::ParseTest::test_call_two_args test/util/test_functemplate.py::ParseTest::test_call_with_escaped_sep test/util/test_functemplate.py::ParseTest::test_call_with_nested_call_argument
