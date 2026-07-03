#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$PROJECT_DIR/tasks/terraform-lifecycle-feature-v0/verify.sh"
"$PROJECT_DIR/tasks/terraform-lifecycle-refactor-v0/verify.sh"
"$PROJECT_DIR/tasks/terraform-lifecycle-review-v0/verify.sh"
