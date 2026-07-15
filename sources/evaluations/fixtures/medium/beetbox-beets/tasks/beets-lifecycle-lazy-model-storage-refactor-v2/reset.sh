#!/usr/bin/env bash
set -euo pipefail
repo="${1:?usage: reset.sh <repo>}"
git -C "$repo" apply --reverse "$(dirname "$0")/seed-regression.patch"
