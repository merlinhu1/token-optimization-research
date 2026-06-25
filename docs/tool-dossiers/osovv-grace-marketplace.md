# Tool dossier: osovv/grace-marketplace

## Identity

- Repository: `osovv/grace-marketplace`
- URL: https://github.com/osovv/grace-marketplace
- Version/ref inspected: local shallow clone `73f2b207cfcd`, 2026-06-29
- Snapshot status: pinned-commit
- Commit inspected: 73f2b207cfcd
- Commit URL: https://github.com/osovv/grace-marketplace/commit/73f2b207cfcd
- Source artifact path: `sources/discovery/2026-06-29-graph-leads-a-source-logic.json`
- Date inspected: 2026-06-29
- Evidence stage: source-logic (local source inspection of package/CLI entrypoints, query/indexing, lint, verification reference checks, file command, and representative tests)
- License: MIT (`package.json`)

## Summary

Grace Marketplace provides a Bun-powered `grace` CLI and packaged agent skills for GRACE project artifacts: semantic markup, module contracts, knowledge/development/verification XML, linting, status, and artifact queries. Source inspection confirms artifact parsing/query logic, governed-file lookup, lint checks for semantic markers and XML anti-patterns, and verification reference consistency checks. It is a governance/artifact navigation tool, not a measured token-saving tool at this evidence stage.

## Evidence inventory

| Evidence type | Files inspected | Notes |
|---|---|---|
| Manifest/entrypoint | `package.json`, `src/grace.ts` | Bun package `@osovv/grace-cli`; `grace` bin with `file`, `lint`, `module`, `status`, `verification` subcommands. |
| Query/index logic | `src/query/core.ts`, `src/query/render.ts` (path identified), `src/grace-file.ts` | Loads XML docs and governed files into a queryable artifact index; file-local display command. |
| Lint logic | `src/lint/core.ts`, `src/lint/config.ts` (imported), adapters under `src/lint/adapters/` (identified) | Required docs, marker pair checks, semantic markup rules, module/test reference checks. |
| Verification logic | `src/verification/check-references.ts` | Ensures verification test files are referenced by module-check commands, with cwd normalization. |
| Tests | `src/grace-query.test.ts`, `src/grace-lint.test.ts`, `src/grace-status.test.ts`, `src/verification/check-references.test.ts`, `src/lint/adapters/dart.test.ts` identified; `check-references.ts` implementation inspected. | Test paths found in source tree; representative verification logic inspected directly. |

## Installation and integration behavior

- `package.json` publishes `@osovv/grace-cli` with Bun engine `>=1.3.8` and bin `grace = ./src/grace.ts`.
- Package files include CLI source, lint/query directories, README, and license; skills/plugins directories are present in the repository for agent-marketplace packaging.
- Main CLI is a `citty` command with subcommands: `file`, `lint`, `module`, `status`, and `verification`.
- `grace file show` loads artifact index from a project root, resolves a governed file path, and emits either JSON or formatted text with optional contracts/blocks.
- The inspected source does not implement an MCP server; integration appears via CLI plus packaged skills/plugin artifacts.

## Runtime behavior

- `loadGraceArtifactIndex` requires `docs/knowledge-graph.xml`, `docs/development-plan.xml`, and `docs/verification-plan.xml`; it parses modules, graph entries, verification entries, plan steps, and governed source files.
- Module records merge development-plan, knowledge-graph, verification, and local file evidence by module ID; helper functions expose name/type/path/dependencies/verification IDs/implementation files.
- `findModules` scores query matches across module id/name/type, plan/graph purpose, dependencies, verification IDs, interface/annotation tags, file paths, file purpose/scope, and path proximity.
- `findVerifications` scores verification matches across id, module id/name, priority, test files, module-check commands, scenarios, log markers, and trace assertions.
- `resolveModule` and `resolveGovernedFile` normalize target paths relative to root and throw on missing or ambiguous matches.
- Lint core checks required docs, module/verification ID formats, generic XML anti-patterns, marker pairing/nesting, contract fields, language adapter analysis, and module-check references.
- `checkModuleCheckReferences` returns false if any declared test file is not referenced by module-check commands, with cwd-prefix stripping for monorepos.

## Token-saving mechanism

- Addressable token surface: agent navigation of project governance artifacts and semantically marked source files.
- Reduction method: query commands retrieve specific modules/files/verifications/contracts instead of requiring an agent to read all XML docs and source annotations; lint/status commands turn artifact consistency checks into structured output.
- Quality-preservation mechanisms seen in source: required-doc enforcement, deterministic XML/marker parsing, scoring with explicit matched fields, ambiguity errors, semantic anti-pattern linting, and verification-reference checks.
- Cases where savings may not translate to billed reductions: projects must already maintain GRACE markup; missing/incorrect XML or markers can block queries; CLI calls may add turns; no source path shows automatic context compression for arbitrary codebases.

## Benchmarks and claims

No benchmark-audit was performed. No inspected benchmark artifact supports token-saving claims. Treat any README/marketplace statements as discovery evidence only until source-driven runs or benchmark artifacts are reviewed.

## Compatibility notes

Grace is primarily a project governance/semantic-markup and artifact-query authority. It can complement code retrieval if used only for GRACE-governed contracts/verifications, but it overlaps with other memory/knowledge-graph governance systems if both attempt to own module plans, verification plans, or semantic annotations.

## Failure modes and limits

- Requires Bun runtime and GRACE-specific project documents; absent required docs cause index loading to fail.
- XML parsing is regex/string based, so malformed or unexpected nesting may be missed or parsed imperfectly.
- Query coverage depends on disciplined module IDs, unique tags, and semantic markers in source files.
- Lint can report many project-governance errors but does not prove implementation correctness.
- No inspected MCP/server or automatic live retrieval integration was present.

## Open questions

- How are `plugins/grace` and `skills/grace` installed into the intended host marketplaces?
- What is the minimum GRACE markup required before the CLI becomes useful on an existing repo?
- Does GRACE artifact querying reduce provider-billed tokens compared with direct doc/source reading in real tasks?

## Next review tasks

- [ ] Inspect `grace-module.ts`, `grace-status.ts`, and `grace-verification.ts` subcommand behavior in more detail.
- [ ] Run `grace lint/status/file/module/verification` on a sample GRACE project and capture exact outputs.
- [ ] Review plugin/skill packaging files for host-specific side effects and uninstall/disable behavior.
