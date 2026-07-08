#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
node --test test/skip-reply-send.test.js test/content-type.test.js
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- 'const kRegisteredPlugins = Symbol.for('"'"'registered-plugin'"'"')' lib/plugin-utils.js >/dev/null
grep -F -- '  withResolvers: typeof Promise.withResolvers === '"'"'function'"'"'' lib/promise.js >/dev/null
grep -F -- '    isCustomValidatorCompiler: typeof opts?.compilersFactory?.buildValidator === '"'"'function'"'"',' lib/schema-controller.js >/dev/null
grep -F -- '    listenOptions = { port: 0, host: '"'"'localhost'"'"' },' lib/server.js >/dev/null
