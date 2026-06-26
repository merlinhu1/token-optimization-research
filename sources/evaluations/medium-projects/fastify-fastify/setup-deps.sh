#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR/repo"
if [ ! -d node_modules ]; then npm install --ignore-scripts --no-audit --no-fund; fi
