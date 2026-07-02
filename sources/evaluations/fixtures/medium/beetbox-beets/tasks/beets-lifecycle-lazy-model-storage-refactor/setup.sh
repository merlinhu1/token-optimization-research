#!/usr/bin/env bash
set -euo pipefail
repo="${1:?usage: setup.sh <repo>}"
git -C "$repo" apply "$(dirname "$0")/seed-regression.patch"
