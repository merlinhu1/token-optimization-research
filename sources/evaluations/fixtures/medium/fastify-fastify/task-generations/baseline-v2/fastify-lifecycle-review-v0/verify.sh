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
  const seen = []
  const app = Fastify({
    logger: false,
    maxParamLength: 2,
    frameworkErrors (error, request, reply) {
      seen.push({ code: error.code, url: request.url })
      reply.code(error.statusCode || 500).send({ code: error.code, message: error.message })
    }
  })
  app.get('/:id', async request => ({ id: request.params.id }))
  app.register(async child => {
    child.setNotFoundHandler((request, reply) => {
      reply.code(499).send({ child: true, url: request.url })
    })
    child.get('/:id', async request => ({ child: request.params.id }))
  }, { prefix: '/c' })

  const ok = await app.inject('/ab')
  assert.equal(ok.statusCode, 200)
  assert.deepEqual(JSON.parse(ok.payload), { id: 'ab' })

  const tooLong = await app.inject('/abc')
  assert.equal(tooLong.statusCode, 414)
  assert.equal(JSON.parse(tooLong.payload).code, 'FST_ERR_MAX_PARAM_LENGTH')
  assert.deepEqual(seen, [{ code: 'FST_ERR_MAX_PARAM_LENGTH', url: '/abc' }])

  const defaultApp = Fastify({ logger: false, maxParamLength: 2 })
  defaultApp.get('/:id', async request => ({ id: request.params.id }))
  const defaultTooLong = await defaultApp.inject('/abc')
  assert.equal(defaultTooLong.statusCode, 414)
  assert.equal(JSON.parse(defaultTooLong.payload).code, 'FST_ERR_MAX_PARAM_LENGTH')

  const childOk = await app.inject('/c/ab')
  assert.equal(childOk.statusCode, 200)
  assert.deepEqual(JSON.parse(childOk.payload), { child: 'ab' })

  const childTooLong = await app.inject('/c/abc')
  assert.equal(childTooLong.statusCode, 414)
  assert.equal(JSON.parse(childTooLong.payload).code, 'FST_ERR_MAX_PARAM_LENGTH')

  const customNotFound = await app.inject('/c/no/xx')
  assert.equal(customNotFound.statusCode, 499)
  assert.deepEqual(JSON.parse(customNotFound.payload), { child: true, url: '/c/no/xx' })
})().catch(error => {
  console.error(error)
  process.exitCode = 1
})
NODE
cat > "$tmpdir/max-param.tst.ts" <<'TS'
import { FastifyErrorCodes, FastifyRouterOptions, FastifyServerOptions, RawReplyDefaultExpression, RawRequestDefaultExpression } from '../fastify.js'
import { expect } from 'tstyche'

expect({ maxParamLength: 8 }).type.toBeAssignableTo<FastifyServerOptions>()
expect({
  onMaxParamLength: (path: string, req: RawRequestDefaultExpression, res: RawReplyDefaultExpression) => {
    path.toUpperCase()
    req.url
    res.statusCode = 414
  }
}).type.toBeAssignableTo<FastifyRouterOptions<import('node:http').Server>>()
expect('FST_ERR_MAX_PARAM_LENGTH').type.toBeAssignableTo<keyof FastifyErrorCodes>()
TS
npx tstyche --target 6.0 "$tmpdir/max-param"
