#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
node --test test/has-route.test.js test/head-route.test.js
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- '    this.isDisableRequestLoggingFunction = typeof this.disableRequestLogging === '"'"'function'"'"'' lib/log-controller.js >/dev/null
grep -F -- '  const methods = ['"'"'info'"'"', '"'"'error'"'"', '"'"'debug'"'"', '"'"'fatal'"'"', '"'"'warn'"'"', '"'"'trace'"'"', '"'"'child'"'"']' lib/logger-factory.js >/dev/null
grep -F -- '      version: req.headers && req.headers['"'"'accept-version'"'"'],' lib/logger-pino.js >/dev/null
grep -F -- '  if (instancePrefix.endsWith('"'"'/'"'"') && pluginPrefix[0] === '"'"'/'"'"') {' lib/plugin-override.js >/dev/null
