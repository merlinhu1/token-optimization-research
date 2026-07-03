# Task: Node ESM import repair

## Identity

- Task ID: `node-esm-import-repair`
- Task class: build-repair
- Repository fixture: `sources/evaluations/fixture-corpus/v1/node-esm-import-repair/repo`
- Fixture snapshot: generated fixture corpus v1, reset by `sources/evaluations/fixture-corpus/v1/materialize.py node-esm-import-repair`
- Date created: 2026-07-01

## Agent prompt

```text
Fix the Node ESM import/runtime failure and pass node --test. Keep the public function names stable unless the tests require otherwise.
```

## Expected result

- Required behavior: Repair the named import/export mismatch without weakening the test.
- Expected files/symbols: `src/normalize.js`, `src/cart.js`, `test/cart.test.js`
- Forbidden shortcuts: do not skip tests, delete assertions, remove verifier checks, hard-code only the visible assertion unless the task explicitly asks for an answer artifact, or enable unlisted token-saving surfaces.
- Acceptance verifier: `cd sources/evaluations/fixture-corpus/v1/node-esm-import-repair/repo && node --test`

## Token-waste hypothesis

- Primary token-waste surface: `build-output`
- Expected useful intervention: Node ESM failures add JavaScript runtime/module-resolution diagnostics to the suite without external package dependencies.
- Expected failure mode: lower visible tokens by hiding the root diagnostic, broad-reading the fixture, leaking stale state, or passing by under-solving.

## Baseline and treatment profiles

- Baseline profile ID: `baseline-codex-no-mcp`
- Treatment profile IDs: `terminal-rtk`, `terminal-lowfat`, `terminal-snip`, `retrieval-leanctx`

## Quality gates

- Deterministic command: `cd sources/evaluations/fixture-corpus/v1/node-esm-import-repair/repo && node --test`
- Human review rubric additions: focused diff, no unrelated generated noise, raw evidence paths preserved, and no unrequested overlapping surface owners.
- Critical diagnostic facts to preserve: failing command, file path, line/column or operation ID where applicable, exact compiler/error/root cause, and raw artifact recovery path.

## Reset procedure

- Repository reset: `python3 sources/evaluations/fixture-corpus/v1/materialize.py node-esm-import-repair`
- Agent/tool state reset: clear treatment-specific hooks, indexes, memory stores, generated profile files, and provider session state before each run.
- Memory/index reset: required for retrieval, broad-owner, installer, and replacement-runtime treatments unless the protocol explicitly preserves state.
