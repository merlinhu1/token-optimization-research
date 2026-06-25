# Tool dossier: ldomaradzki/xcsift

## Identity

- Repository: `ldomaradzki/xcsift`
- URL: https://github.com/ldomaradzki/xcsift
- Version/ref inspected: local shallow clone `0a4b1287bf1b`, 2026-07-01
- Snapshot status: pinned-commit
- Commit inspected: 0a4b1287bf1b698ef2bff0016ee583ed39ae6d77
- Commit URL: https://github.com/ldomaradzki/xcsift/commit/0a4b1287bf1b698ef2bff0016ee583ed39ae6d77
- Source artifact path: `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json`
- Date inspected: 2026-07-01
- Evidence stage: source-logic (fresh pinned shallow clone; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection: 444
- Forks at inspection: 21
- License: MIT
- Updated at: 2026-06-26T07:20:54Z

## Summary

xcsift parses xcodebuild/SPM output and emits structured build, error, warning, coverage, timing, and test information for coding agents.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 63 files and 42 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `Sources/XCSiftCore/CoverageParser.swift`
- `Sources/XCSiftCore/FileSystemProtocol.swift`
- `Sources/XCSiftCore/LineParser.swift`
- `Sources/XCSiftCore/Models.swift`
- `Sources/XCSiftCore/OutputParser.swift`
- `Sources/XCSiftCore/ShellRunnerProtocol.swift`
- `Sources/XCSiftCore/XCBeautifySymbols.swift`
- `Sources/XCSiftCore/XcodebuildSymbols.swift`
- `Sources/xcsift/ConfigLoader.swift`
- `Sources/xcsift/ConfigMerger.swift`
- `Sources/xcsift/Configuration.swift`
- `Sources/xcsift/Install/ClaudeCodeInstaller.swift`
- `Sources/xcsift/Install/CodexInstaller.swift`
- `Sources/xcsift/Install/CursorInstaller.swift`
- `Sources/xcsift/Install/InstallCommands.swift`
- `Sources/xcsift/Install/Templates/CodexTemplates.swift`
- `Sources/xcsift/Install/Templates/CursorTemplates.swift`
- `Sources/xcsift/Install/Templates/SharedTemplates.swift`
- `Sources/xcsift/main.swift`
- `Tests/TestUtils/MockFileSystem.swift`
- `Tests/XCSiftCoreTests/BuildPhasesTest.swift`
- `Tests/XCSiftCoreTests/BuildPhasesTimingTests.swift`
- `Tests/XCSiftCoreTests/CoverageTests.swift`
- `Tests/XCSiftCoreTests/EncodingTests.swift`
- `Tests/XCSiftCoreTests/Fixtures/build.txt`
- `Tests/XCSiftCoreTests/Fixtures/linker-error-output.txt`
- `Tests/XCSiftCoreTests/Fixtures/swift-testing-output.txt`
- `Tests/XCSiftCoreTests/GitHubActionsFormatTests.swift`
- `Tests/XCSiftCoreTests/LineParserTests.swift`
- `Tests/XCSiftCoreTests/LinkerErrorTests.swift`
- `Tests/XCSiftCoreTests/ParsingTests.swift`
- `Tests/XCSiftCoreTests/TOONFormatTests.swift`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`.

### Fresh pinned-source refresh

The 2026-07-01 refresh pins the inspected source to `0a4b1287bf1b698ef2bff0016ee583ed39ae6d77` and records a fresh tree plus selected implementation excerpts in `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` and `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`. Representative files captured for this refresh include `Sources/XCSiftCore/CoverageParser.swift`, `Sources/XCSiftCore/FileSystemProtocol.swift`, `Sources/XCSiftCore/LineParser.swift`, `Sources/XCSiftCore/Models.swift`, `Sources/XCSiftCore/OutputParser.swift`, `Sources/XCSiftCore/ShellRunnerProtocol.swift`. Treat benchmark, savings, and deployment claims below as source-logic only unless a benchmark-audit or reproduction artifact is explicitly cited.


- `Sources/XCSiftCore/OutputParser.swift` accumulates/deduplicates errors, warnings, failed tests, linker errors, executables, timings, and build phases from complete build output.
- `Sources/XCSiftCore/LineParser.swift` emits typed parse events for compiler errors, linker errors, tests, phases, dependencies, and ignored lines.
- `Sources/XCSiftCore/CoverageParser.swift` auto-detects xcresult/DerivedData or SPM coverage paths and converts coverage to structured output.
- `Sources/xcsift/main.swift` defines CLI format options including JSON/TOON-oriented output controls.
- `Sources/xcsift/Install/ClaudeCodeInstaller.swift` installs/uninstalls Claude Code integration and reports marketplace/plugin failures explicitly.

## Installation and integration behavior

- Tool: xcsift
- Primary intervention surface: Xcode/xcodebuild output parsing into token-efficient structured JSON/TOON
- Integration status: source and integration paths identified; exact production behavior should be verified per target agent before rollout.
- Disable/uninstall path: requires follow-up inspection where not covered by representative files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Xcode/xcodebuild output parsing into token-efficient structured JSON/TOON
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Xcode/xcodebuild output parsing into token-efficient structured JSON/TOON
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation is present.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: prompt-cache effects, added tool calls, stale indexes/state, failed retrieval/compression, or increased correction turns.

## Compatibility notes

Specialized Apple-build output compactor. It can coexist with a general terminal compactor if the stack avoids double-filtering xcodebuild output.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- Domain-specific to Swift/Xcode/SPM outputs.
- Consumes complete output in memory rather than streaming line-by-line per parser comments.
- Needs exact-fidelity checks for rare build/linker/coverage formats.

## Open questions and next review tasks

- [ ] Review tests for all parser event types and TOON output.
- [ ] Test interaction with RTK/TokenJuice/Snip on xcodebuild commands.
- [ ] Measure provider-billed savings on iOS/macOS repair tasks.
