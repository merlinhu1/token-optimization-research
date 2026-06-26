# fastify-response-2xx-serializer-regression

## Fixture

- Project: `fastify/fastify`
- Shared workflow base commit: `94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd`
- Evidence stage target: `reproduction`
- Task class: `controlled-project-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Restore JSON content parsing and media-type parser fallback behavior.

Complexity upgrade: this task now verifies multiple related symptoms and uses a multi-edit seed patch rather than a one-line localized mutation.

## Seeded start state

Apply `seed-regression.patch` after checking out the shared workflow base commit. The patch creates a controlled broken state in production code while preserving the verifier.

## Agent prompt

- Path: `sources/evaluations/medium-projects/fastify-fastify/tasks/fastify-response-2xx-serializer-regression/agent-prompt.txt`
- SHA-256: `781ee7da00a86ad86aafa5497748dbf825b871356096445e954e1c51de7f1100`

## Verifier

```bash
sources/evaluations/medium-projects/fastify-fastify/tasks/fastify-response-2xx-serializer-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
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
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the described regression unless explicitly justified.
- The solution addresses project behavior rather than hard-coding only the visible failing assertion.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.

Five-file complexity bar: this seeded start state changes at least five production files, and the verifier includes source-invariant checks for every supplemental file-level regression.
