#!/usr/bin/env bash
set -euo pipefail
cd "${WORKFLOW_REPO:?WORKFLOW_REPO is required}"
uv run --offline --frozen --no-project pytest -q test/util/test_functemplate.py -k 'escaped_sep'
uv run --offline --frozen --no-project ruff format --check beets/util/functemplate.py
