#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
node --test test/schema-feature.test.js test/schema-serialization.test.js
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- 'module.exports = validate10;' lib/config-validator.js >/dev/null
grep -F -- '    if (headerValue == null || headerValue === '"'"''"'"' || headerValue === '"'"'undefined'"'"') {' lib/content-type.js >/dev/null
grep -F -- '  const separator = '"'"', '"'"'' lib/context.js >/dev/null
grep -F -- '  if (fn && (typeof fn.getter === '"'"'function'"'"' || typeof fn.setter === '"'"'function'"'"')) {' lib/decorate.js >/dev/null
