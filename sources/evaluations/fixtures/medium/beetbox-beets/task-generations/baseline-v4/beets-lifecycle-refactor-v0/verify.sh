#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"
mode="${1:-all}"
behavior() { uv run --offline --frozen python -c "from beets.dbcore.db import LazyDict; value=LazyDict({'a': 1}, lambda k,v:v); assert list(value)==['a']"; }
structure() { uv run --offline --frozen python -c "from beets.dbcore.db import LazyDict; value=LazyDict({'a': 1}, lambda k,v:v); assert type(iter(value)).__name__ == 'set_iterator'"; }
case "$mode" in behavior) behavior;; structure) structure;; all) behavior; structure;; *) exit 2;; esac
