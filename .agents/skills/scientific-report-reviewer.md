---
name: scientific-report-reviewer
description: Use after drafting a research report to score evidence relevance, falsifiability, scope calibration, argument coherence, exploration integrity, and methodological rigor.
---
# Scientific Report Reviewer

## Purpose

Review report quality as an epistemic artifact, not just as prose. This adapts AI/CS paper-review and ARA-style rigor checks to practical software-evaluation reports.

## When to Use

Use after drafting Phase reports, benchmark-audit reports, reproduction reports, or major methodology updates.

## Six Review Dimensions

Score each dimension 1-5 and list concrete edits.

1. **Evidence relevance** — does cited evidence substantively support each claim?
2. **Falsifiability** — are important claims testable with concrete metrics and thresholds?
3. **Scope calibration** — does wording match evidence stage and workload scope?
4. **Argument coherence** — does the report move from problem to hypothesis to evidence to limits?
5. **Exploration integrity** — are negative findings, exclusions, pivots, and uncertainty visible?
6. **Methodological rigor** — are baselines, ablations, token accounting, quality gates, and reproducibility details adequate?

## Procedure

1. Read the target report and relevant templates/framework docs.
2. Extract the report thesis in one sentence.
3. Reverse-outline each section: one section message, one paragraph message.
4. Build a claim-evidence map for major claims.
5. Score the six dimensions.
6. Produce severity-ranked findings: `critical`, `major`, `minor`, `suggestion`.
7. Recommend exact edits or new experiments.

## Output

```json
{
  "overall": {"score": 0, "summary": ""},
  "dimensions": {},
  "findings": [],
  "recommended_edits": []
}
```

## Common Pitfalls

- Polishing prose while leaving unsupported claims intact.
- Allowing a report to read like a ledger instead of an argument.
- Omitting negative findings because they seem inconvenient.
- Confusing source-logic confidence with benchmark-audit confidence.
