# Repository Fixture Framework

## Purpose

Repository fixtures are controlled codebase snapshots used for Phase 2 evaluation. They answer a narrower question than stack reports: whether a repository can support repeatable baseline and treatment runs.

Fixture readiness is not a tool evidence stage. A `qualified-fixture`, `baseline-run`, or `treatment-ready` record does not promote any tool or compatibility-safe stack to `benchmark-audit` or `reproduction`.

## Why fixtures come before stacks

A stack comparison is only interpretable when repository setup, reset, prompt, verifier, and artifact capture are stable. Without a fixture layer, a treatment can appear to fail because the repository is hard to install, the verifier is weak, the prompt drifted, or a reset path left stale state behind.

The evaluation pipeline is:

```text
candidate repositories
  -> repository fixture qualification
  -> baseline runs
  -> single-surface component tests
  -> compatibility-safe stack ablations
  -> benchmark-audit or reproduction evidence
```

## Fixture lifecycle

| State | Meaning | Promotion condition |
|---|---|---|
| `candidate-fixture` | A repository may support an evaluation task, but one or more readiness fields remain incomplete. | Identify repository source, task class, primary token-waste surface, setup/reset/verifier blockers or commands, and artifact policy. |
| `qualified-fixture` | The repository has enough concrete setup, reset, verifier, prompt, and snapshot information for a protocol to be frozen. | Verify setup, reset, verifier, fixture snapshot, prompt path or prompt policy, and artifact paths. |
| `baseline-run` | A substrate baseline, such as Codex no-MCP for additive Codex experiments, has been run and preserved for this fixture. | Store baseline transcript, verifier output, environment record, usage record when available, and reset notes. |
| `treatment-ready` | The fixture has a baseline and can be used for one or more treatment profiles. | Baseline artifacts exist, reset is repeatable, and treatment install/disable boundaries are understood. |
| `retired-fixture` | The repository should no longer be used for new evaluation runs. | Record reason, such as unstable dependencies, weak verifier, inaccessible platform, or superseded fixture. |

## Task classes

| Task class | Token-waste target | Minimum verifier expectation |
|---|---|---|
| `noisy-terminal-repair` | Long test logs, repeated command output, and diagnostic extraction. | Failing test becomes passing or expected diagnostic is localized. |
| `build-repair` | Compiler, typechecker, or build output. | Build/typecheck passes or a frozen diagnostic is correctly localized. |
| `large-codebase-navigation` | Broad file reads and imprecise code search. | Correct file, symbol, or module is identified and task-specific question is answered. |
| `multi-file-refactor` | Retrieval precision and edit quality across multiple files. | Tests pass and diff implements the requested behavior. |
| `memory-rediscovery` | Re-reading project conventions or repeated decisions. | Later task applies the known convention without broad documentation reread. |
| `broad-owner-context` | Broad context, graph/wiki, proxy, archive, or memory ownership. | Single-owner profile completes task without hidden overlap and preserves raw evidence. |
| `mcp-tool-heavy` | Large MCP/tool traces and offloaded execution. | Final artifact passes verifier while trace artifacts stay recoverable. |
| `apple-build-repair` | Xcode/SPM output and Apple build diagnostics. | Build/test issue is localized and fix passes when environment permits. |
| `replacement-runtime-comparison` | Whole-agent runtime trade-off. | Same verifier and prompt are usable across native and replacement runtimes. |

## Fixture record requirements

Each fixture record in `data/repository-fixtures.json` must include:

- `id`: stable kebab-case fixture ID.
- `status`: one lifecycle state.
- `fixture_scale`: `synthetic-micro`, `recorded-diagnostic`, or `large-project`.
- `evaluation_use`: `calibration`, `diagnostic-preservation`, `primary-candidate`, or `primary-objective`.
- `repository`: repository ID, path, or URL.
- `snapshot`: commit, tag, archive, or explicit snapshot policy.
- `task_classes`: one or more supported task classes.
- `primary_token_waste_surface`: one primary surface for the first evaluation pass.
- `setup`: command or blocker.
- `reset`: command or blocker.
- `verifier`: deterministic command or blocker.
- `prompt`: prompt path or prompt policy once the fixture is qualified.
- `artifact_paths`: root path for future raw artifacts.
- `future_evaluation_lanes`: later lanes this fixture can support.
- `candidate_profiles`: profile IDs from `data/evaluation-profiles.json` that may use this fixture; these are not active treatments until a protocol freezes them.
- `blockers` and `caveats`: open readiness issues.

Primary objective claims require `fixture_scale = large-project` plus reproduction records. Synthetic and recorded fixtures are calibration or diagnostic evidence unless a report explicitly scopes its claim to that smaller setting.

## Promotion rules

A fixture can move from `candidate-fixture` to `qualified-fixture` only when setup, reset, verifier, snapshot, prompt, and artifact path are concrete enough for another operator to freeze a protocol without rereading Phase 1 reports.

A fixture can move to `baseline-run` only after the substrate baseline is stored under `sources/evaluations/<evaluation-id>/` with verifier output and environment notes.

A fixture can move to `treatment-ready` only after baseline artifacts exist and reset behavior is repeatable.

A fixture should move to `retired-fixture` instead of being deleted when it has useful negative evidence or a known blocker.

## Validation

Repository validation checks fixture records for required structure, duplicate IDs, known lifecycle states, known task classes, one primary token-waste surface, artifact roots, repository identity, and setup/reset/verifier commands or blockers.

Readiness states stricter than `candidate-fixture` require concrete setup, reset, verifier, snapshot, and prompt information.

## Non-goals

This framework does not run baselines, run treatments, select stack winners, claim provider-billed savings, or promote tool evidence stages. Those actions belong in later progressive evaluation changes with frozen protocols.
