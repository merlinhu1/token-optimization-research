'use strict'

const { test } = require('node:test')
const assert = require('node:assert/strict')
const Fastify = require('../fastify')

test('Baseline V2 request media type is normalized and visible during validation and handling', async () => {
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
})
