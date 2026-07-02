# Tool dossier: zdk/lowfat

## Identity

- Repository: `zdk/lowfat`
- URL: https://github.com/zdk/lowfat
- Version/ref inspected: local shallow clone `b9f6f99d02e5`, 2026-07-01
- Snapshot status: pinned-commit
- Commit inspected: b9f6f99d02e5774296305a591bfb13ef24548c38
- Commit URL: https://github.com/zdk/lowfat/commit/b9f6f99d02e5774296305a591bfb13ef24548c38
- Source artifact path: `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json`
- Date inspected: 2026-07-01
- Evidence stage: source-logic + reproduction (one isolation-clean, one-workflow-replicate screening result exists for the narrow Lowfat v0.8.0 prompted/preferred direct-use estimand; native automatic shell integration remains unevaluated)
- Stars at inspection: 543
- Forks at inspection: 17
- License: Apache-2.0
- Updated at: 2026-06-26T05:59:45Z

## Summary

Lowfat filters command output through built-in and plugin pipelines, routing content to compressors and retaining raw failure output in tee logs.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API where available; local shallow clone fallback for rate-limited repos | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` | Used to identify source, hook, MCP, test, benchmark, and runtime paths beyond README. |
| Runtime/source content | `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json` | Representative files fetched from raw GitHub or read from local clones with SHA-256 prefixes and behavior excerpts. |
| README/docs | README/docs paths identified when present. | README claims are not used as behavior evidence. |
| Tests/benchmarks | Paths identified where present. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 143 files and 98 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `crates/lowfat-compress/Cargo.toml`
- `crates/lowfat-compress/src/code.rs`
- `crates/lowfat-compress/src/data.rs`
- `crates/lowfat-compress/src/detect.rs`
- `crates/lowfat-compress/src/html.rs`
- `crates/lowfat-compress/src/lib.rs`
- `crates/lowfat-compress/src/lock.rs`
- `crates/lowfat-compress/src/markdown.rs`
- `crates/lowfat-compress/src/text.rs`
- `crates/lowfat-core/Cargo.toml`
- `crates/lowfat-core/benches/core_bench.rs`
- `crates/lowfat-core/src/config.rs`
- `crates/lowfat-core/src/db.rs`
- `crates/lowfat-core/src/level.rs`
- `crates/lowfat-core/src/lf.rs`
- `crates/lowfat-core/src/lib.rs`
- `crates/lowfat-core/src/pipeline.rs`
- `crates/lowfat-core/src/redact.rs`
- `crates/lowfat-core/src/structured.rs`
- `crates/lowfat-core/src/tee.rs`
- `crates/lowfat-core/src/tokens.rs`
- `crates/lowfat-plugin/Cargo.toml`
- `crates/lowfat-plugin/benches/plugin_bench.rs`
- `crates/lowfat-plugin/embedded/docker/docker-compact/BENCHMARK.md`
- `crates/lowfat-plugin/embedded/docker/docker-compact/bench.sh`
- `crates/lowfat-plugin/embedded/git/git-compact/BENCHMARK.md`
- `crates/lowfat-plugin/embedded/git/git-compact/bench.sh`
- `crates/lowfat-plugin/embedded/ls/ls-compact/BENCHMARK.md`
- `crates/lowfat-plugin/embedded/ls/ls-compact/bench.sh`
- `crates/lowfat-plugin/src/discovery.rs`
- `crates/lowfat-plugin/src/embedded.rs`
- `crates/lowfat-plugin/src/lib.rs`


## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`.

### Fresh pinned-source refresh

The 2026-07-01 refresh pins the inspected source to `b9f6f99d02e5774296305a591bfb13ef24548c38` and records a fresh tree plus selected implementation excerpts in `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` and `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`. Representative files captured for this refresh include `crates/lowfat-compress/Cargo.toml`, `crates/lowfat-compress/src/code.rs`, `crates/lowfat-compress/src/data.rs`, `crates/lowfat-compress/src/detect.rs`, `crates/lowfat-compress/src/html.rs`, `crates/lowfat-compress/src/lib.rs`. Treat benchmark, savings, and deployment claims below as source-logic only unless a benchmark-audit or reproduction artifact is explicitly cited.


- `crates/lowfat-core/src/pipeline.rs` selects conditional pipelines based on exit code, empty output, and output size/token budget.
- `crates/lowfat-core/src/tee.rs` saves raw command output on failures when output is large, keeping a bounded history of raw logs.
- `crates/lowfat-compress/src/detect.rs` routes files/content by extension and lockfile detection to appropriate compressors.
- `crates/lowfat-runner/src/runner.rs` loads embedded or disk plugins and dispatches `.lf` filters or process filters.
- `crates/lowfat-plugin/src/plugin.rs` defines filter plugin input/output contracts including raw merged stdout/stderr and passthrough status.

## Installation and integration behavior

- Tool: Lowfat
- Primary intervention surface: Terminal/tool-output filtering and command-specific compression plugins
- Integration status: direct use prefixes commands with `lowfat`; native shell integration evaluates `lowfat shell-init bash|zsh` in the agent shell and automatically wraps only configured command filters. `terminal-lowfat` preserves the historical prompted direct-use arm; `terminal-lowfat-shell-integrated-v0.8.0` is the blocked future native-integration arm.
- Disable/uninstall path: requires follow-up inspection where not covered by representative files.
- Failure behavior if dependency is missing: partially inspected where representative code exposes it; complete failure-mode review remains open.

## Runtime behavior

- Intervention surface: Terminal/tool-output filtering and command-specific compression plugins
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Terminal/tool-output filtering and command-specific compression plugins
- Reduction method: implementation-level mechanism identified in representative source files where runtime implementation is present.
- Quality-preservation mechanism: partially identified; benchmark/reproduction review remains required.
- Cases where transformed-output savings may not reduce provider-reported total tokens: prompt-cache effects, added model turns, stale indexes/state, failed retrieval/compression, or increased correction work.

## Compatibility notes

Terminal-output compression owner. It overlaps directly with RTK, TokenJuice, Snip, xcsift for Xcode workflows, and LeanCTX shell compression.

A compatibility-safe stack has components that do not fight over the same hook, context surface, retrieval authority, memory authority, proxy, output channel, behavior controller, artifact policy, or state boundary.

## Failure modes and limits

- The pinned v0.8.0 binary bundles filters only for `docker`, `find`, `git`, `grep`, `ls`, and `tree`; unknown commands are pass-through unless an external plugin is installed.
- Command-output filtering can hide needed diagnostics if raw recovery is not surfaced.
- Plugin/process filters add execution and security surface.
- Token savings need fidelity checks for compiler/test/log outputs.
- Prompted/preferred direct use was the predeclared historical treatment and is not invalid merely because a later natural-use principle chose a different estimand. Fastify and Terraform are causally excluded because only treatment used external retrieval. Beets remains valid one-replicate screening evidence for the narrow preferred-direct-use arm: +42.25% provider tokens with accepted baseline/treatment correctness and quality. This is not evidence for native automatic shell integration. Its high pass-through count limits mechanism attribution. See `docs/research/lowfat-three-lane-evaluation.md`.

## Open questions and next review tasks

- [x] Inspect built-in embedded filters and command coverage.
- [x] Audit the historical preferred-direct-use guidance, treatment timing, and external-retrieval contamination.
- [ ] Implement and preflight native `lowfat shell-init` in the actual model shell before any natural-use protocol is eligible.
- [ ] Review raw-output retrieval/user workflow.
- [ ] Add or install target-specific test/build filters before evaluating those command families.
- [ ] Benchmark against RTK/TokenJuice/Snip on terminal-heavy tasks under the corrected network and coverage contract.
