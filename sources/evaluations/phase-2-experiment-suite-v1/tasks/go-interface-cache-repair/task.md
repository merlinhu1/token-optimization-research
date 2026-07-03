# Task: Go interface compile repair

## Identity

- Task ID: `go-interface-cache-repair`
- Task class: build-repair
- Repository fixture: `sources/evaluations/fixture-corpus/v1/go-interface-cache-repair/repo`
- Fixture snapshot: generated fixture corpus v1, reset by `sources/evaluations/fixture-corpus/v1/materialize.py go-interface-cache-repair`
- Date created: 2026-07-01

## Agent prompt

```text
Fix the Go cache implementation so it satisfies the Store interface and passes go test ./.... Keep the API minimal and do not weaken tests.
```

## Expected result

- Required behavior: Add the context-aware Put method signature while preserving Get behavior and the Store interface.
- Expected files/symbols: `cache/cache.go`, `cache/cache_test.go`
- Forbidden shortcuts: do not skip tests, delete assertions, remove verifier checks, hard-code only the visible assertion unless the task explicitly asks for an answer artifact, or enable unlisted token-saving surfaces.
- Acceptance verifier: `cd sources/evaluations/fixture-corpus/v1/go-interface-cache-repair/repo && PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH go test ./...`

## Token-waste hypothesis

- Primary token-waste surface: `build-output`
- Expected useful intervention: Go build/test diagnostics exercise typed interface errors and compiler output distinct from Python tracebacks.
- Expected failure mode: lower visible tokens by hiding the root diagnostic, broad-reading the fixture, leaking stale state, or passing by under-solving.

## Baseline and treatment profiles

- Baseline profile ID: `baseline-codex-no-mcp`
- Treatment profile IDs: `terminal-rtk`, `terminal-lowfat`, `terminal-snip`, `retrieval-serena`, `retrieval-leanctx`

## Quality gates

- Deterministic command: `cd sources/evaluations/fixture-corpus/v1/go-interface-cache-repair/repo && PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH go test ./...`
- Human review rubric additions: focused diff, no unrelated generated noise, raw evidence paths preserved, and no unrequested overlapping surface owners.
- Critical diagnostic facts to preserve: failing command, file path, line/column or operation ID where applicable, exact compiler/error/root cause, and raw artifact recovery path.

## Reset procedure

- Repository reset: `python3 sources/evaluations/fixture-corpus/v1/materialize.py go-interface-cache-repair`
- Agent/tool state reset: clear treatment-specific hooks, indexes, memory stores, generated profile files, and provider session state before each run.
- Memory/index reset: required for retrieval, broad-owner, installer, and replacement-runtime treatments unless the protocol explicitly preserves state.
