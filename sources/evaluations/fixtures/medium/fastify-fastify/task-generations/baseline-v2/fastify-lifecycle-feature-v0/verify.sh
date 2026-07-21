#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${WORKFLOW_REPO:-$PROJECT_DIR/repo}"
tmpdir="$(mktemp -d workflow-hidden-types.XXXXXX)"
trap 'rm -rf "$tmpdir"' EXIT
node <<'NODE'
const assert = require('node:assert/strict')
const Fastify = require('./fastify')

;(async () => {
  const app = Fastify({ logger: false })
  const observed = []
  app.addHook('preValidation', async request => {
    observed.push(request.mediaType)
  })
  app.post('/typed', {
    schema: {
      body: {
        content: {
          'application/json': {
            schema: {
              type: 'object',
              required: ['ok'],
              properties: { ok: { type: 'boolean' } }
            }
          }
        }
      }
    }
  }, async request => ({ mediaType: request.mediaType, body: request.body }))

  const accepted = await app.inject({
    method: 'POST',
    url: '/typed',
    headers: { 'content-type': 'Application/JSON; Charset=UTF-8' },
    payload: JSON.stringify({ ok: true })
  })
  assert.equal(accepted.statusCode, 200)
  assert.equal(JSON.parse(accepted.payload).mediaType, 'application/json')
  assert.deepEqual(observed, ['application/json'])

  const rejected = await app.inject({
    method: 'POST',
    url: '/typed',
    headers: { 'content-type': 'Application/JSON; Charset=UTF-8' },
    payload: JSON.stringify({ ok: 'nope' })
  })
  assert.equal(rejected.statusCode, 400)
  assert.match(JSON.parse(rejected.payload).message, /boolean/)
})().catch(error => {
  console.error(error)
  process.exitCode = 1
})
NODE
cat > "$tmpdir/request-media-type.tst.ts" <<'TS'
import { expect } from 'tstyche'
import { FastifyRequest } from '../fastify.js'

declare const request: FastifyRequest
expect(request.mediaType).type.toBe<string | undefined>()
TS
npx tstyche --target 6.0 "$tmpdir/request-media-type"
