'use strict'

const { test } = require('node:test')
const assert = require('node:assert/strict')
const Fastify = require('../fastify')

test('Baseline V2 max parameter length returns HTTP 414 through default and custom handlers', async () => {
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
})
