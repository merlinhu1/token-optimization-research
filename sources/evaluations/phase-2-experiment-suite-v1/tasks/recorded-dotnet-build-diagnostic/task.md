# Task: Recorded .NET build diagnostic preservation

## Identity

- Task ID: `recorded-dotnet-build-diagnostic`
- Task class: build-repair
- Repository fixture: `sources/evaluations/fixture-corpus/v1/recorded-dotnet-build-diagnostic/repo`
- Fixture snapshot: generated fixture corpus v1, reset by `sources/evaluations/fixture-corpus/v1/materialize.py recorded-dotnet-build-diagnostic`
- Date created: 2026-07-01

## Agent prompt

```text
Compact the recorded dotnet build log and preserve every required diagnostic fact in artifacts/compacted.txt.
```

## Expected result

- Required behavior: Compacted output keeps file, line/column, compiler code, type mismatch, project path, and raw log path.
- Expected files/symbols: `raw/dotnet-build.log`, `verify_compaction.py`
- Forbidden shortcuts: do not skip tests, delete assertions, remove verifier checks, hard-code only the visible assertion unless the task explicitly asks for an answer artifact, or enable unlisted token-saving surfaces.
- Acceptance verifier: `cd sources/evaluations/fixture-corpus/v1/recorded-dotnet-build-diagnostic/repo && python3 verify_compaction.py`

## Token-waste hypothesis

- Primary token-waste surface: `build-output`
- Expected useful intervention: Recorded .NET/MSBuild diagnostics cover C# compiler error shape even when the local SDK is unavailable.
- Expected failure mode: lower visible tokens by hiding the root diagnostic, broad-reading the fixture, leaking stale state, or passing by under-solving.

## Baseline and treatment profiles

- Baseline profile ID: `baseline-codex-no-mcp`
- Treatment profile IDs: `terminal-rtk`, `terminal-lowfat`, `terminal-snip`, `terminal-headroom`

## Quality gates

- Deterministic command: `cd sources/evaluations/fixture-corpus/v1/recorded-dotnet-build-diagnostic/repo && python3 verify_compaction.py`
- Human review rubric additions: focused diff, no unrelated generated noise, raw evidence paths preserved, and no unrequested overlapping surface owners.
- Critical diagnostic facts to preserve: failing command, file path, line/column or operation ID where applicable, exact compiler/error/root cause, and raw artifact recovery path.

## Reset procedure

- Repository reset: `python3 sources/evaluations/fixture-corpus/v1/materialize.py recorded-dotnet-build-diagnostic`
- Agent/tool state reset: clear treatment-specific hooks, indexes, memory stores, generated profile files, and provider session state before each run.
- Memory/index reset: required for retrieval, broad-owner, installer, and replacement-runtime treatments unless the protocol explicitly preserves state.
