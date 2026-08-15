---
name: practical-software-quality-reviewer
description: Use only when an optional diagnostic review of model-produced changes is useful. Report evidence-backed findings separately; never decide token-sample eligibility or task acceptance.
---
# Practical Software Quality Reviewer

## Purpose

Provide an independent diagnostic review of model-produced changes. The review records evidence-backed concerns about correctness, regression safety, maintainability, scope, and safety. It does not accept, exclude, score, or select a provider-token sample.

## When to Use

Use after a run only when independent source-quality context is worth its review cost. Operationally complete runs remain token-accounting eligible whether this review is absent, favorable, or unfavorable. Compilation remains the controller's task/workflow acceptance gate; this review is diagnostic.

## Diagnostic dimensions

1. **Observed behavior**
   - report compile and other diagnostic outcomes exactly as captured;
   - inspect the diff rather than trusting the model's final message;
   - identify likely semantic gaps without rewriting acceptance policy.
2. **Scope and regression risk**
   - changes are limited to the requested objective;
   - unrelated or prohibited files are untouched;
   - likely affected behavior and missing diagnostic coverage are explicit.
3. **Code quality**
   - minimal focused diff;
   - follows project conventions;
   - no duplicate stack or unnecessary framework;
   - no generated noise.
4. **Maintainability**
   - readable names;
   - simple control flow;
5. **Safety/security**
   - no secrets in artifacts;
   - no unsafe permission broadening;
   - no unexpected network or credential behavior.
6. **Evidence quality**
   - each finding cites a file, diff hunk, or captured diagnostic;
   - missing evidence is stated as uncertainty, not inferred as failure.

## Output

List only actionable findings, ordered by severity, with the evidence and likely effect. If none are found, say so. Do not produce a numeric score, acceptance decision, rerun recommendation, or token-sample eligibility judgment.

## Common Pitfalls

- Counting token savings when the agent avoided necessary work.
- Trusting final text without checking diff/test evidence.
- Treating a diagnostic test failure as operational invalidity.
- Turning an optional review into a second acceptance gate.
