# Phase 2 experiment suite v1 protocol

## Status

This is the v1 protocol for calibration and first-wave large-project reproduction. Objective-bearing reproduction protocols are now prepared for Django and Terraform with pinned commits, seeded tasks, tool manifests, and deterministic verifiers.

## Research question

Which token-optimization surfaces reduce provider-billed task usage or artifact-token burden while preserving software quality, diagnostic evidence, reproducibility, and reset safety across representative coding-agent workloads?

## Design

This suite uses a stratified, multi-fixture design rather than a single showcase task. Each stratum targets one primary token-waste surface, uses at least one deterministic verifier, and separates baseline, single-surface component tests, stack ablations, and replacement-runtime comparisons.

## Primary outcomes

1. Provider-billed task tokens and cost when available from the agent/provider logs.
2. Deterministic verifier pass/fail.
3. Practical software quality score from 0 to 5.
4. Diagnostic preservation for compaction and build-output tasks.
5. Tool-call count, turn count, wall-clock time, install/reset success, and raw-artifact recoverability.

## Secondary outcomes

- Estimated raw versus transformed artifact tokens with one fixed tokenizer.
- Expected-target retrieval success before agent execution.
- Broad-read count and unnecessary file-read count when observable in transcripts.
- State leakage, stale memory injection, or unrequested surface ownership.

## Baseline policy

Every task has a native-agent baseline with no token-saving add-ons. Baseline and treatment runs use the same prompt, fixture snapshot, model/provider family, maximum turns, verifier, and artifact-capture requirements. If exact model parity is impossible for a replacement-runtime lane, the run is labeled non-parity and cannot support a headline cost claim.

## Treatment policy

Single-surface treatments run before stack treatments. A stack treatment is eligible only when no two enabled components own the same surface unless the protocol explicitly tests that overlap as a failure-risk condition.

## Sample structure

The current evaluation setup contains 5 retained calibration/diagnostic fixtures and 2 active public large-project fixtures. Calibration fixtures are tool sanity checks only; primary objective claims require executed Django or Terraform `large-project` reproduction records. Active projects are listed in `data/large-project-candidates.json` and represented as `qualified-fixture` records in `data/repository-fixtures.json`.

## Candidate coverage

| Candidate class | Fixture records | Purpose |
|---|---:|---|
| Calibration/diagnostic | 5 | Sanity-check instrumentation, diagnostic preservation, and verifier capture. |
| Active public large-project fixtures | 2 | Source fixtures for individual-tool and stack reproduction. |

## Active large-project fixtures

| Candidate | Language/surface | Role |
|---|---|---|
| `large-django-django` | Python | tractable first large-project candidate |
| `large-hashicorp-terraform` | Go | tractable typed Go candidate |

## Exclusion and downgrade rules

- A run with missing verifier output is excluded from positive claims.
- A treatment that hides required diagnostics cannot be reported as a success even if token counts fall.
- A treatment that changes task scope, skips tests, or edits forbidden files receives quality score at most 2.
- A result without provider-billed usage can support artifact-efficiency or benchmark-audit claims, not provider-cost claims.
- Any install/reset failure is retained as negative operational evidence.

## Artifact contract

Each run writes the following files under `sources/evaluations/phase-2-experiment-suite-v1/runs/<evaluation-id>/`:

```text
task.md
profile.md
environment.json
baseline-transcript.jsonl or treatment-transcript.jsonl
provider-usage.json
verifier-output.txt
quality-review.md
artifacts/
```

The task definitions in `tasks/<fixture-id>/` are evaluator-owned. The `agent-prompt.txt` file is the only prompt text shown to an evaluated agent.
