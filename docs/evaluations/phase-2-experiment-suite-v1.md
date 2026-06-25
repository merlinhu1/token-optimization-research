# Phase 2 Experiment Suite v1

## Purpose

This suite turns the Phase 2 framework into a concrete research setting while separating calibration from objective-bearing evidence. Small generated fixtures are retained only to sanity-check instrumentation and diagnostic preservation. Primary claims about token-saving tools and stacks require large public projects.

## Suite contents

- Protocol: `sources/evaluations/phase-2-experiment-suite-v1/protocol.md`
- Runbook: `sources/evaluations/phase-2-experiment-suite-v1/runbook.md`
- Analysis plan: `sources/evaluations/phase-2-experiment-suite-v1/analysis-plan.md`
- Quality rubric: `sources/evaluations/phase-2-experiment-suite-v1/quality-rubric.md`
- Profile matrix: `sources/evaluations/phase-2-experiment-suite-v1/profile-matrix.md`
- Calibration task artifacts: `sources/evaluations/phase-2-experiment-suite-v1/tasks/**`
- Calibration fixture repos: `sources/evaluations/fixture-corpus/v1/**/repo`
- Large-project candidate registry: `data/large-project-candidates.json`
- Fixture registry: `data/repository-fixtures.json`

## Experimental strata

| Stratum | Current fixture records | Primary question |
|---|---:|---|
| Calibration and diagnostic preservation | 5 | Do instrumentation, verifier capture, and compaction checks behave before expensive large-project runs? |
| Active large-project fixtures | 2 | Do the selected public projects support pinned snapshots, seeded tasks, deterministic verifiers, and repeatable baselines? |
| Individual-tool reproduction | 2 active projects | Does one token-saving tool reduce provider-billed task usage or artifact burden on a complex project while preserving quality? |
| Stack reproduction | 2 active projects | Does a compatibility-safe stack outperform baseline and individual components without overlapping surface ownership? |

## Minimum evaluation batch

A first calibration report can use the retained calibration fixtures. The first objective-bearing report must instead use one or more promoted `large-project` fixtures, with at least one substrate baseline, individual-tool treatments, stack treatments, and repeated runs for any default-owner claim. Negative runs and setup/reset failures stay in the evidence record.

## Active large-project fixtures

| Candidate | Language/surface | Role |
|---|---|---|
| `large-django-django` | Python | tractable first large-project candidate |
| `large-hashicorp-terraform` | Go | tractable typed Go candidate |

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
- Before large-project runs exist, this suite supports candidate-readiness claims only.
- Artifact-token reductions alone do not support provider-cost claims.
- Source-logic plus fixture readiness does not promote a tool to `benchmark-audit` or `reproduction`.
- A treatment must pass the deterministic verifier and quality review before it can support positive task-level claims.
