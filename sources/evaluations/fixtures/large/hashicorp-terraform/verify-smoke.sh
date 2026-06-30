#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$PROJECT_DIR/tasks/terraform-161ffe-tracing-context-regression/verify.sh"
"$PROJECT_DIR/tasks/terraform-520378-computed-block-capabilities-regression/verify.sh"
"$PROJECT_DIR/tasks/terraform-9ae470-objchange-validation-regression/verify.sh"
