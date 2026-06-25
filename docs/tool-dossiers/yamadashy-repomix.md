# Tool dossier: yamadashy/repomix

## Identity

- Repository: `yamadashy/repomix`
- URL: https://github.com/yamadashy/repomix
- Version/ref inspected: local shallow clone `6873d5212227`, 2026-07-01
- Snapshot status: pinned-commit
- Commit inspected: 6873d5212227998a4de7395744acc1f2d894cc20
- Commit URL: https://github.com/yamadashy/repomix/commit/6873d5212227998a4de7395744acc1f2d894cc20
- Source artifact path: `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json`
- Date inspected: 2026-07-01
- Evidence stage: source-logic (fresh pinned shallow clone; representative source/config/test files inspected; benchmark-audit and reproduction still required for measured savings)
- Stars at inspection: 26,583
- Forks at inspection: 1,390
- License: MIT
- Updated at: 2026-06-26T07:03:59Z

## Summary

Repomix packs repository contents into AI-friendly context files. It can save tokens when selective compression/filtering replaces ad hoc file reading, but it can also increase context if used as a full-repository dump.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| Repository metadata | GitHub API repository metadata | Popularity and license signals only; not effectiveness evidence. |
| Source tree | `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` | Used to identify installer, plugin, MCP, test, and benchmark paths beyond README. |
| README/docs | README path identified when present. | README claims require source and benchmark follow-up. |
| Installer/config/plugin files | Paths identified below. | Integration review started. |
| Runtime source | Representative implementation files inspected; see code-detail section. | Source-logic review is recorded for representative modules; uninspected modules remain benchmark-audit/reproduction follow-up. |
| Tests/benchmarks | Representative tests or metrics files inspected where available. | Full benchmark-method review remains open. |

## Initial source-structure finding

Repository tree inspection found 1,141 files and 878 files matching integration, source, test, benchmark, or documentation patterns. Relevant paths include:

- `scripts/memory/src/memory-test.ts`
- `scripts/memory/src/types.ts`
- `src/cli/actions/defaultAction.ts`
- `src/cli/actions/initAction.ts`
- `src/cli/actions/mcpAction.ts`
- `src/cli/actions/migrationAction.ts`
- `src/cli/actions/remoteAction.ts`
- `src/cli/actions/versionAction.ts`
- `src/cli/actions/watch/watchIgnore.ts`
- `src/cli/actions/watchAction.ts`
- `src/cli/cliReport.ts`
- `src/cli/cliRun.ts`
- `src/cli/cliSpinner.ts`
- `src/cli/cliTokenBudget.ts`
- `src/cli/prompts/skillPrompts.ts`
- `src/cli/reporters/tokenCountTreeReporter.ts`
- `src/cli/types.ts`
- `src/config/configLoad.ts`
- `src/config/configSchema.ts`
- `src/config/defaultIgnore.ts`
- `src/config/globalDirectory.ts`
- `src/core/file/fileCollect.ts`
- `src/core/file/fileManipulate.ts`
- `src/core/file/filePathSort.ts`
- `src/core/file/fileProcess.ts`
- `src/core/file/fileProcessContent.ts`
- `src/core/file/fileRead.ts`
- `src/core/file/fileSearch.ts`
- `src/core/file/fileStdin.ts`
- `src/core/file/fileTreeGenerate.ts`
- `src/core/file/fileTypes.ts`
- `src/core/file/packageJsonParse.ts`
- `src/core/file/permissionCheck.ts`
- `src/core/file/truncateBase64.ts`
- `src/core/file/workers/fileProcessWorker.ts`
- `src/core/git/archiveEntryFilter.ts`
- `src/core/git/gitCommand.ts`
- `src/core/git/gitDiffHandle.ts`
- `src/core/git/gitHubArchive.ts`
- `src/core/git/gitHubArchiveApi.ts`



## Code-detail inspection findings

Evidence artifact: `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`.

### Fresh pinned-source refresh

The 2026-07-01 refresh pins the inspected source to `6873d5212227998a4de7395744acc1f2d894cc20` and records a fresh tree plus selected implementation excerpts in `sources/discovery/2026-07-01-pinned-dossier-refresh-source-structures.json` and `sources/discovery/2026-07-01-pinned-dossier-refresh-code-inspection.json`. Representative files captured for this refresh include `scripts/memory/src/memory-test.ts`, `scripts/memory/src/types.ts`, `src/cli/actions/defaultAction.ts`, `src/cli/actions/initAction.ts`, `src/cli/actions/mcpAction.ts`, `src/cli/actions/migrationAction.ts`. Treat benchmark, savings, and deployment claims below as source-logic only unless a benchmark-audit or reproduction artifact is explicitly cited.
 The artifact contains raw GitHub file paths, byte sizes, SHA-256 prefixes, and behavior-line excerpts from the inspected implementation files.

- `src/core/packager.ts` coordinates repository search, token-count cache loading, sort-data prefetch, file processing, and output production.
- `src/core/output/outputGenerate.ts` renders outputs through style templates and computes file line counts and summaries for consolidated output.
- `src/core/metrics/TokenCounter.ts` loads GPT-tokenizer encodings asynchronously and caches count functions, making token accounting an explicit local metric rather than an inferred README claim.
- `src/mcp/tools/packCodebaseTool.ts` registers an MCP tool that packages a local code directory, exposes a `compress` option, creates a temporary workspace, and returns output metrics including `totalTokens`.
- `src/core/security/filterOutUntrustedFiles.ts` filters raw files that match suspicious-file results before output generation.

### Implementation-level limits

- Repomix can reduce ad hoc file-reading cost when selective packing/compression is used, but full-repository packing can increase prompt size.
- Packed output is a snapshot and can become stale during active editing.
- It is better treated as a digest/handoff surface than as a concurrent retrieval authority beside CodeGraph or Serena.

## Installation and integration behavior

- Tool type: Repository packing/digest tool
- Primary intervention surface: Repository packing and optional compression/digest generation
- Integration status: documented integration paths and/or source locations were identified, but exact runtime behavior has not yet been fully reviewed.
- Disable/uninstall path: requires follow-up inspection of installer/plugin code and documentation.
- Failure behavior if dependency is missing: partially inspected in representative files; complete deployment failure-mode review remains open.

## Runtime behavior

- Intervention surface: Repository packing and optional compression/digest generation
- Input captured: see code-detail findings; remaining modules require follow-up.
- Output emitted: see code-detail findings; benchmark-level output effects require follow-up.
- State/cache/files written: see code-detail findings where inspected; full state review remains open.
- Network/subprocess behavior: see code-detail findings where inspected; full process/network review remains open.
- Raw-output recovery path: partially inspected where relevant; full recovery behavior remains open.
- Security/privacy considerations: initial code-level risks recorded; deeper deployment review remains open.

## Token-saving mechanism

- Addressable token surface: Repository packing and optional compression/digest generation
- Reduction method: identified from representative implementation files; full benchmark/reproduction review remains open.
- Quality-preservation mechanism: partially identified from representative source where present; benchmark/reproduction review remains required.
- Cases where savings may not translate to provider-billed reductions: depends on turn count, prompt caching, failure/retry behavior, and whether the tool changes agent workflow length.

## Benchmarks and claims

| Claim | Source | Measurement scope | Reviewed method | Caveats |
|---|---|---|---|---|
| Token-saving or context-reduction claims exist or are implied by repository description/metadata. | Repository metadata, existing catalog records, and pinned source-logic refresh. | Varies by tool. | Reviewed at source-logic level through representative implementation files; not benchmark-audited or reproduced. | Maintainer claims must not be treated as reproduced evidence. |

## Compatibility notes

Best treated as a one-shot handoff or digest generator, not a default retrieval owner inside an agent stack. It overlaps with targeted retrieval tools when used as a full-repository context source.

Compatibility-safe stack selection means the tools should not fight over the same hook, context surface, retrieval authority, memory authority, proxy, or output channel.

## Failure modes and limits

- Full-repository packing can greatly increase prompt size.
- Generated digests can become stale during active editing.
- Aggressive compression/filtering may omit details needed for edits.

## Open questions and next review tasks

- [ ] Inspect packer and compression strategy source.
- [ ] Inspect ignore/filter/default include behavior.
- [ ] Review token-counting or compression tests.
- [ ] Compare against CodeGraph/Serena targeted retrieval for representative tasks.
