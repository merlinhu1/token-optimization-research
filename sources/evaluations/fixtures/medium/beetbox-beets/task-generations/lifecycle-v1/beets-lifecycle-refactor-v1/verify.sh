#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"

# Controller-only Lifecycle V1 acceptance. This rejects the seeded generator
# while allowing any behaviorally correct non-generator iterator implementation.
uv run --offline --frozen python -m py_compile beets/dbcore/db.py &&
  uv run --offline --frozen python -c "import inspect; from beets.dbcore.db import LazyDict; value = LazyDict({'a': 1}, lambda key, item: item); iterator = iter(value); assert not inspect.isgenerator(iterator); assert set(iterator) == {'a'}"
