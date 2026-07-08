#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
node --test test/trust-proxy.test.js
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- 'const channels = diagnostics.tracingChannel('"'"'fastify.request.handler'"'"')' lib/handle-request.js >/dev/null
grep -F -- '    reply.header('"'"'content-length'"'"', '"'"'0'"'"')' lib/head-route.js >/dev/null
grep -F -- '  if (typeof hook !== '"'"'string'"'"') throw new FST_ERR_HOOK_INVALID_TYPE()' lib/hooks.js >/dev/null
grep -F -- '    object[name] = value && typeof value === '"'"'object'"'"' ? deepFreezeObject(value) : value' lib/initial-config-validation.js >/dev/null
