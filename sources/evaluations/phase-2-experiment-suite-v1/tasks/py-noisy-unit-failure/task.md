# Task: Python noisy unit-test repair

## Identity

- Task ID: `py-noisy-unit-failure`
- Task class: noisy-terminal-repair
- Repository fixture: `sources/evaluations/fixture-corpus/v1/py-noisy-unit-failure/repo`
- Fixture snapshot: generated fixture corpus v1, reset by `sources/evaluations/fixture-corpus/v1/materialize.py py-noisy-unit-failure`
- Date created: 2026-07-01

## Agent prompt

```text
Fix the failing unit test in this repository. Keep the implementation minimal. Run the verifier and report the final command output.
```

## Expected result

- Required behavior: Fix percent_delta so it computes change relative to the old value and handles zero-denominator behavior as documented.
- Expected files/symbols: `ledger_math.py`
- Forbidden shortcuts: do not skip tests, delete assertions, remove verifier checks, hard-code only the visible assertion unless the task explicitly asks for an answer artifact, or enable unlisted token-saving surfaces.
- Acceptance verifier: `cd sources/evaluations/fixture-corpus/v1/py-noisy-unit-failure/repo && python3 -m unittest discover -s tests -v`

## Token-waste hypothesis

- Primary token-waste surface: `terminal-output`
- Expected useful intervention: Terminal-output owners reduce diagnostic artifact tokens while preserving the exact failing assertion, file, line, command exit status, and raw-output recovery path.
- Expected failure mode: lower visible tokens by hiding the root diagnostic, broad-reading the fixture, leaking stale state, or passing by under-solving.

## Baseline and treatment profiles

- Baseline profile ID: `baseline-codex-no-mcp`
- Treatment profile IDs: `terminal-rtk`, `terminal-lowfat`, `terminal-snip`, `terminal-tokenjuice`, `terminal-headroom`

## Quality gates

- Deterministic command: `cd sources/evaluations/fixture-corpus/v1/py-noisy-unit-failure/repo && python3 -m unittest discover -s tests -v`
- Human review rubric additions: focused diff, no unrelated generated noise, raw evidence paths preserved, and no unrequested overlapping surface owners.
- Critical diagnostic facts to preserve: failing command, file path, line or operation ID where applicable, exact error/root cause, and raw artifact recovery path.

## Reset procedure

- Repository reset: `python3 sources/evaluations/fixture-corpus/v1/materialize.py py-noisy-unit-failure`
- Agent/tool state reset: clear treatment-specific hooks, indexes, memory stores, generated profile files, and provider session state before each run.
- Memory/index reset: required for all retrieval, memory, broad-owner, installer, and replacement-runtime treatments unless the memory-ablation protocol explicitly preserves memory between Task A and Task B.
