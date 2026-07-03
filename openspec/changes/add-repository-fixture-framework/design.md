## Context

Phase 1 produced 42 source-logic dossiers and a broad portfolio of compatibility-safe stack hypotheses. Phase 2 must avoid running expensive stack comparisons before repository fixtures are qualified. A fixture-first framework gives each future evaluation a frozen repository snapshot, verifier, reset path, task class, token-waste hypothesis, and artifact contract.

The repository already contains progressive evaluation-change templates and Phase 2 benchmark planning. This change adds the missing layer between "many candidate repositories" and "run a baseline/treatment experiment": repository fixture qualification.

## Goals / Non-Goals

**Goals:**

- Define a repository fixture schema and lifecycle that can be validated before experiments.
- Register a small starter set of candidate fixtures for Step 2.
- Require deterministic verifiers, reset/install paths, frozen commits, task classes, token-waste surfaces, and raw artifact paths before baseline or treatment runs.
- Make fixture records usable by later progressive evaluation changes.
- Preserve negative, blocked, and retired fixture states rather than silently dropping unsuitable repositories.

**Non-Goals:**

- No baseline or treatment execution in this change.
- No provider-billed measurement in this change.
- No stack ranking or measured savings claim.
- No promotion from source-logic to benchmark-audit or reproduction.
- No full automation runner unless validation needs a small structural checker.

## Decisions

### Decision 1: Use repository fixtures before stack profiles

Fixture qualification SHALL happen before stack ablation. A stack evaluation can reference only fixture records that have at least a qualified verifier and reset path.

Alternative rejected: start with stack profiles and backfill fixture metadata. That makes failures hard to interpret and allows metric boundaries to drift after results exist.

### Decision 2: Store fixture records in a structured data file

Use `data/repository-fixtures.json` as the compact canonical registry. Human-facing docs and templates explain the model, but the registry owns machine-checkable fixture status.

Alternative rejected: store only markdown fixture notes. Markdown is useful for context but weak for detecting duplicate IDs, invalid states, missing verifier commands, and unsupported task classes.

### Decision 3: Keep fixture lifecycle separate from evidence stages

Fixture states describe repository readiness, not tool evidence. A `qualified-fixture` does not imply benchmark-audit or reproduction evidence for any tool or stack.

Lifecycle states:

- `candidate-fixture`
- `qualified-fixture`
- `baseline-run`
- `treatment-ready`
- `retired-fixture`

### Decision 4: Register starter fixtures as candidates first

The first registration pass should create candidate records, not overstate readiness. A candidate can be promoted only after its verifier, reset command, fixture commit, and task prompt path are concrete.

### Decision 5: Start broad, then narrow

The first 3-5 candidate fixtures should cover different token-waste patterns rather than many variants of the same pattern:

- noisy terminal/build failure repair;
- large-codebase navigation;
- repeated-task memory rediscovery;
- broad-owner/context evaluation;
- Apple/Xcode build repair only if a realistic local fixture and verifier are available.

## Risks / Trade-offs

- Fixture schema becomes too heavy → keep required fields minimal and put optional narrative detail in markdown notes.
- Candidate records look like evidence → docs and schema must state that fixture status is not an evidence stage.
- Apple fixture is hard to reproduce on Linux → allow it to remain blocked or omitted until a realistic fixture exists.
- Validation script becomes brittle → validate structure and known enum values first; avoid enforcing experiment-specific details too early.
- Too many fixtures get registered → cap the first pass at 3-5 candidates and require one token-waste surface per candidate.

## Migration Plan

1. Add framework docs, schema/template, and validation.
2. Register the starter candidate fixtures.
3. Run repository validation and OpenSpec validation.
4. Use future evaluation changes to promote individual fixtures through baseline and treatment readiness.

## Open Questions

- Which exact repositories should be used for the first fixture records?
- Should Apple/Xcode be represented as a blocked candidate now, or deferred until a runnable fixture exists?
- Should `scripts/validate_repository.py` directly validate fixtures, or should it call a dedicated `scripts/validate_fixtures.py`?
