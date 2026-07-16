# Repository guidance

## Evaluation contract

This repository is pre-production. The sole evaluation portfolio is lifecycle v0:

1. feature implementation;
2. behavior-preserving refactor;
3. code review/correction.

Every active sequence, task ID, qualification file, and frozen execution contract must be v0. Do not add any non-v0 lane record or parallel compatibility surface. `data/workflow-sessions.json` stays empty until a production run actually executes.

## Fixture design

- Pin the upstream repository commit.
- Build authentic tasks from upstream code/history.
- Start patches must be independently applicable and compose without overlap.
- Feature and review start states fail semantic acceptance.
- Refactor starts must pass behavior acceptance and fail only the disclosed structural/performance gate.
- Model-facing prompts disclose public behavior and any required structural outcome; controller tests remain concealed.
- Review tasks include the exact proposed patch under review.
- Run all concealed verifiers after the final prompt in one persistent workflow.

## Evidence and execution

Qualification JSON is generated executable evidence; never hand-edit it. Production runs require provider-reported cumulative tokens, full software-quality review, and isolated baseline/treatment conditions. Do not infer a result from qualification readiness.

## Required checks

```bash
python3 scripts/validate_repository.py
python3 scripts/test_workflow_evaluation_contract.py
```

When task contracts change, regenerate the affected `qualification-lifecycle-v0.json`, update the generated runbook, and refresh only current v0 execution contracts.

## Local review skills

Use the repository-local skill matching the work:

- `.agents/skills/benchmark-protocol-writer.md`
- `.agents/skills/claim-evidence-auditor.md`
- `.agents/skills/stack-ablation-planner.md`
- `.agents/skills/practical-software-quality-reviewer.md`
- `.agents/skills/scientific-report-reviewer.md`
- `.agents/skills/citation-light-prior-art-mapper.md`
- `.agents/skills/figure-table-planner.md`
