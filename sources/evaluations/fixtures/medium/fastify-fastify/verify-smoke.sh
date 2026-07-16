#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$PROJECT_DIR/tasks/fastify-lifecycle-feature-v0/verify.sh"
"$PROJECT_DIR/tasks/fastify-lifecycle-refactor-v0/verify.sh"
"$PROJECT_DIR/tasks/fastify-lifecycle-review-v0/verify.sh"
