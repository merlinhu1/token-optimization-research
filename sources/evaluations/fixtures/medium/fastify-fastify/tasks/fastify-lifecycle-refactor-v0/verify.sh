#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
repo="${WORKFLOW_REPO:-$PROJECT_DIR/repo}"
mode="${1:-all}"
behavior() {
  (cd "$repo" && node <<'NODE'
const assert = require('node:assert/strict')
const Fastify = require('./fastify')
const ContentType = require('./lib/content-type')
;(async () => {
  const parsed = ContentType.from('Application/JSON; Charset=UTF-8; boundary="abc"')
  assert.equal(parsed.mediaType, 'application/json')
  assert.equal(parsed.parameters.get('charset'), 'UTF-8')
  assert.equal(parsed.parameters.get('boundary'), 'abc')
  const serialized = parsed.toString()
  assert.equal(ContentType.from(serialized).toString(), serialized)
  const app = Fastify({ logger: false })
  app.post('/echo', async request => ({ mediaType: request.mediaType, body: request.body }))
  const response = await app.inject({ method: 'POST', url: '/echo', headers: { 'content-type': 'Application/JSON; Charset=UTF-8' }, payload: JSON.stringify({ ok: true }) })
  assert.equal(response.statusCode, 200)
  assert.deepEqual(JSON.parse(response.payload), { mediaType: 'application/json', body: { ok: true } })
})().catch(error => { console.error(error); process.exitCode = 1 })
NODE
  )
}
structure() {
  (cd "$repo" && node <<'NODE'
const assert = require('node:assert/strict')
const ContentType = require('./lib/content-type')
const raw = 'Application/JSON; Charset=UTF-8'
assert.ok(ContentType.cache, 'ContentType must expose the shared bounded cache')
assert.strictEqual(ContentType.from(raw), ContentType.from(raw), 'identical raw values must reuse one parsed representation')
NODE
  )
}
case "$mode" in
  behavior) behavior ;;
  structure) structure ;;
  all) behavior; structure ;;
  *) echo "usage: verify.sh [behavior|structure|all]" >&2; exit 2 ;;
esac
