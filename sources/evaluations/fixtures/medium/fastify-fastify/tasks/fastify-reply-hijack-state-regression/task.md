# fastify-reply-hijack-state-regression

## Fixture

- Project: `fastify/fastify`
- Shared workflow base commit: `94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd`
- Evidence stage target: `reproduction`
- Task class: `controlled-project-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Preserve reply lifecycle state for hijacked and plain-string responses.

Complexity upgrade: this task now verifies multiple related symptoms and uses a multi-edit seed patch rather than a one-line localized mutation.

## Seeded start state

Apply `seed-regression.patch` after checking out the shared workflow base commit. The patch creates a controlled broken state in production code while preserving the verifier.

## Agent prompt

- Path: `sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-reply-hijack-state-regression/agent-prompt.txt`
- SHA-256: `1b2e87500551bf7ffc5a064f0910b477e00dd7a57dd510c2517da362f922b0c0`

## Verifier

```bash
sources/evaluations/fixtures/medium/fastify-fastify/tasks/fastify-reply-hijack-state-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
node --test test/skip-reply-send.test.js test/content-type.test.js
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the described regression unless explicitly justified.
- The solution addresses project behavior rather than hard-coding only the visible failing assertion.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.

Five-file complexity bar: this seeded start state changes at least five production files, and the verifier includes source-invariant checks for every supplemental file-level regression.
