---
name: practical-software-quality-reviewer
description: Use after a workflow run when optional independent model-behavior diagnostics are useful. Report source quality separately; never decide token-sample eligibility.
---
# Practical Software Quality Reviewer

## Purpose

Provide an independent diagnostic review of model-produced changes. The review explains correctness, regression safety, maintainability, and scope control; it does not accept, exclude, or select a provider-token sample.

## When to Use

Use after a benchmark/reproduction run when independent source-quality context is worth its review cost. Operationally complete runs remain token-accounting eligible whether this review is present or favorable.

## Diagnostic dimensions

1. **Functional correctness**
   - verifier command passes;
   - failure is explained if not passing;
   - no hidden skipped tests.
2. **Diagnostic preservation**
   - raw logs recoverable;
   - critical error lines retained;
   - compaction did not remove root-cause evidence.
3. **Code/config quality**
   - minimal focused diff;
   - follows project conventions;
   - no duplicate stack or unnecessary framework;
   - no generated noise.
4. **Maintainability**
   - readable names;
   - simple control flow;
   - reset/uninstall path documented for configs/tools.
5. **Safety/security**
   - no secrets in artifacts;
   - no unsafe permission broadening;
   - no unexpected network or credential behavior.
6. **Reviewability**
   - diff can be reviewed by a human;
   - command outputs and run records are preserved.

## Scoring

Use 0-5:

- 5: verifier passes and quality is clearly acceptable.
- 4: verifier passes with minor style or documentation concerns.
- 3: functional but quality concerns may affect maintainability.
- 2: partial success or significant diagnostic/reviewability loss.
- 1: task mostly failed or likely under-solved.
- 0: unsafe, unusable, or unverifiable.

## Common Pitfalls

- Counting token savings when the agent avoided necessary work.
- Trusting final text without checking diff/test evidence.
- Ignoring diagnostic loss from aggressive shell-output compaction.
- Treating benchmark pass/fail as the only quality metric.
