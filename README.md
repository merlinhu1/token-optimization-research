# Token Optimization Research

Research infrastructure for measuring provider-reported token usage and software quality in realistic coding-agent workflows.

## Current evaluation portfolio

The repository is pre-production. No baseline, treatment, comparison, or other result has been accepted or retained. The only runnable task contracts are three lifecycle v0 lanes:

| Sequence | Fixture | Ordered stages |
|---|---|---|
| `fastify-lifecycle-sequence-v0` | Fastify | feature → behavior-preserving refactor → code review |
| `beets-lifecycle-sequence-v0` | Beets | feature → behavior-preserving refactor → code review |
| `terraform-lifecycle-sequence-v0` | Terraform | feature → behavior-preserving refactor → code review |

Every lane uses one pinned repository snapshot and one persistent model session. The controller applies all three independently qualified start conditions before prompt 1, discloses prompts in order, preserves model/tool state, and runs all concealed verifiers after prompt 3.

## Source of truth

- `data/workflow-task-sequences.json` — lifecycle v0 contracts.
- `data/repository-fixtures.json` — pinned fixture readiness.
- `sources/evaluations/fixtures/` — task prompts, start patches, controller acceptance, and generated v0 qualification evidence.
- `data/workflow-sessions.json` — empty until the first production execution.
- `docs/evaluations/workflow-evaluation-runbook.md` — generated operator runbook.

## Validation

```bash
python3 scripts/validate_repository.py
python3 scripts/test_workflow_evaluation_contract.py
```

Qualification evidence is executable and generated only by:

```bash
python3 scripts/generate_workflow_qualification.py --sequence-id fastify-lifecycle-sequence-v0
python3 scripts/generate_workflow_qualification.py --sequence-id beets-lifecycle-sequence-v0
python3 scripts/generate_workflow_qualification.py --sequence-id terraform-lifecycle-sequence-v0
```

See `AGENTS.md` before changing evaluation contracts.
