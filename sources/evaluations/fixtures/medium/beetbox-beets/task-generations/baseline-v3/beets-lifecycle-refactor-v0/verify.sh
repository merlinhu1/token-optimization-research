#!/usr/bin/env bash
set -euo pipefail
cd "${WORKFLOW_REPO:?WORKFLOW_REPO is required}"
mode="${1:-all}"
behavior() { uv run --offline --frozen python -c "from beets.dbcore.db import LazyDict; value=LazyDict({'a': 1}, lambda k,v:v); assert list(value)==['a']"; }
structure() { uv run --offline --frozen python -c "from beets.dbcore.db import LazyDict; value=LazyDict({'a': 1}, lambda k,v:v); assert type(iter(value)).__name__ == 'set_iterator'"; }
case "$mode" in behavior) behavior;; structure) structure;; all) behavior; structure;; *) exit 2;; esac
