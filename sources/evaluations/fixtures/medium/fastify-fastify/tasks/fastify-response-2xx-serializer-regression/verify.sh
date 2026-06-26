#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "$PROJECT_DIR/repo"
node --test test/buffer.test.js test/content-parser.test.js && node - <<'JSV'
const assert = require('node:assert')
const fastify = require('./fastify')
;(async () => {
  const app = fastify()
  app.post('/json', async req => ({ body: req.body }))
  const res = await app.inject({ method: 'POST', url: '/json', headers: { 'content-type': 'application/json; charset=utf-8' }, payload: JSON.stringify({ ok: true }) })
  assert.equal(res.statusCode, 200, res.payload)
  assert.deepEqual(JSON.parse(res.payload).body, { ok: true })
})().catch(err => { console.error(err); process.exit(1) })
JSV
# Five-file source-invariant checks added by token optimization fixture generation.
grep -F -- '    return this.func.name.toString() + '"'"'()'"'"'' lib/error-handler.js >/dev/null
grep -F -- '  const serializerState = {"mode":"standalone"}' lib/error-serializer.js >/dev/null
grep -F -- '    '"'"'FST_ERR_NOT_FOUND'"'"',' lib/errors.js >/dev/null
grep -F -- '    const prefix = this[kRoutePrefix] || '"'"'/'"'"'' lib/four-oh-four.js >/dev/null
