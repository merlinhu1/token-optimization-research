#!/usr/bin/env bash
set -euo pipefail
cd "${WORKFLOW_REPO:?WORKFLOW_REPO is required}"
uv run --offline --frozen --no-project pytest -q test/plugins/test_ftintitle.py -k 'split_on_feat'
uv run --offline --frozen --no-project ruff format --check beetsplug/ftintitle.py
