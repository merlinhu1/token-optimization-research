# Phase 2 Experiment Suite v1

## Purpose

This suite turns the Phase 2 framework into a concrete continuous workflow research setting. Small generated fixtures are retained only to sanity-check instrumentation and diagnostic preservation. Primary claims about token-saving tools and stacks require medium or large public projects run as persistent workflow sessions.

## Suite contents

- Protocol: `sources/evaluations/phase-2-experiment-suite-v1/protocol.md`
- Runbook: `sources/evaluations/phase-2-experiment-suite-v1/runbook.md`
- Analysis plan: `sources/evaluations/phase-2-experiment-suite-v1/analysis-plan.md`
- Quality rubric: `sources/evaluations/phase-2-experiment-suite-v1/quality-rubric.md`
- Profile matrix: `sources/evaluations/phase-2-experiment-suite-v1/profile-matrix.md`
- Workflow task sequences: `data/workflow-task-sequences.json`
- Workflow session registry: `data/workflow-sessions.json`
- Calibration task artifacts: `sources/evaluations/phase-2-experiment-suite-v1/tasks/**`
- Calibration fixture repos: `sources/evaluations/fixture-corpus/v1/**/repo`
- Large-project candidate registry: `data/large-project-candidates.json`
- Medium-project candidate registry: `data/medium-project-candidates.json`
- Fixture registry: `data/repository-fixtures.json`

## Experimental strata

| Stratum | Current fixture records | Primary question |
|---|---:|---|
| Calibration and diagnostic preservation | 5 | Do instrumentation, verifier capture, and compaction checks behave before expensive workflow sessions? |
| Active large-project fixtures | 2 active / 1 target replacement candidate | Do the selected public projects support pinned snapshots, task sequences, deterministic verifiers, and repeatable workflow baselines? |
| Active medium-project fixtures | 2 historical active / 2 target replacement candidates | Do smaller mature public projects provide lower-cost realistic workflow sessions without over-weighting foundational Python projects? |
| Individual-tool workflow reproduction | 4-flow target matrix | Does one token-saving tool reduce cumulative provider-billed workflow usage while preserving quality? |
| Stack workflow reproduction | 4-flow target matrix | Does a compatibility-safe stack reduce cumulative provider-billed workflow usage without overlapping surface ownership? |

## Minimum evaluation batch

The first objective-bearing report must use one or more promoted `large-project` or `medium-project` workflow sequences. It needs at least one substrate baseline workflow session and one treatment workflow session on the same sequence, runtime, provider, model, and model condition. Negative runs and setup/reset failures stay in the evidence record.

## Active large-project fixtures

| Candidate | Language/surface | Role |
|---|---|---|
| `large-django-django` | Python | historical active fixture; to be retired from the default matrix after C# replacement qualification |
| `large-hashicorp-terraform` | Go | retained large Go fixture |
| `large-orchardcms-orchardcore` | C# | target large C# replacement candidate; not active until .NET setup, five prompts, seed regressions, and bounded verifiers are qualified |

## Active medium-project fixtures

| Candidate | Language/surface | Role |
|---|---|---|
| `medium-pallets-flask` | Python | historical active fixture; target replacement is Fastify to avoid another Python web framework |
| `medium-psf-requests` | Python | historical active fixture; target replacement is Beets to avoid foundational Python libraries |
| `medium-fastify-fastify` | JavaScript/TypeScript | target medium TS/JS replacement candidate; not active until five prompts, seed regressions, and bounded verifiers are qualified |
| `medium-beetbox-beets` | Python | target medium Python replacement candidate; chosen as a real app/CLI/plugin system rather than a foundational library |

## Active workflow sequences

| Sequence | Fixture | Status |
|---|---|---|
| `django-maintenance-sequence-v1` | `large-django-django` | historical active shared-snapshot 5-task workflow; not in target default matrix after C# qualification |
| `terraform-maintenance-sequence-v1` | `large-hashicorp-terraform` | retained active shared-snapshot 5-task workflow |
| `requests-maintenance-sequence-v1` | `medium-psf-requests` | historical active shared-snapshot 5-task workflow; not in target default matrix after Beets qualification |
| `flask-maintenance-sequence-v1` | `medium-pallets-flask` | historical active shared-snapshot 5-task workflow; not in target default matrix after Fastify qualification |

## Target default matrix

The next default four-flow matrix should use one project per language/runtime family: large C# OrchardCore, large Go Terraform, medium TS/JS Fastify, and medium Python Beets. Keep five tasks per flow. Do not mark the replacement candidates as active reproduction flows until setup, reset, five task prompts, seed-regression patches, bounded verifiers, and provider-usage artifact paths are frozen.

| Slot | Target fixture | Language/runtime | Qualification status |
|---|---|---|---|
| Large C# | `large-orchardcms-orchardcore` | C#/.NET | active runnable workflow; five seeded tasks qualified |
| Large Go | `large-hashicorp-terraform` | Go | active retained fixture |
| Medium TS/JS | `medium-fastify-fastify` | Node / JavaScript / TypeScript | active runnable workflow; five seeded tasks qualified |
| Medium Python | `medium-beetbox-beets` | Python | active runnable workflow; five seeded tasks qualified |


## Complexity upgrade status

The OrchardCore, Fastify, and Beets replacement flows were upgraded from shallow one-line smoke regressions to controlled regressions with at least five changed production files per task.

Each upgraded task has a bounded verifier that fails in the seeded state and passes after reversing the seed.

Each upgraded workflow passed runner `--prepare-only`, proving the five seed patches stack on the shared snapshot and the runner dependency path still works.

## Retained calibration coverage

| Fixture | Purpose |
|---|---|
| `py-noisy-unit-failure` | noisy Python terminal-output sanity check |
| `go-interface-cache-repair` | Go compiler/test diagnostic sanity check |
| `node-esm-import-repair` | Node ESM runtime diagnostic sanity check |
| `recorded-dotnet-build-diagnostic` | recorded .NET/MSBuild diagnostic preservation |
| `recorded-xcodebuild-diagnostic` | recorded Apple/Xcode diagnostic preservation |

## Claim boundaries

- Calibration fixtures do not support primary objective claims.
- Single-task isolated runs are sanity/debug evidence, not tool-ranking evidence.
- Primary objective claims require continuous workflow simulation with cumulative provider-billed token accounting.
- Artifact-token reductions alone do not support provider-cost claims.
- Source-logic plus fixture readiness does not promote a tool to `benchmark-audit` or `reproduction`.
- A treatment must pass deterministic verifiers and quality review before it can support positive workflow-level claims.
