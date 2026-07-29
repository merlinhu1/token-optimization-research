#!/usr/bin/env bash
set -euo pipefail
repo="${1:-${WORKFLOW_REPO:-}}"
[[ -n "$repo" ]] || { echo "usage: setup.sh <repo>" >&2; exit 2; }
git -C "$repo" apply "$(dirname "$0")/seed-regression.patch"
