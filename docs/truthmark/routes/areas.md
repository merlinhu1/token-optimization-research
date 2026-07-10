---
status: active
doc_type: route-index
last_reviewed: 2026-07-07
---

# Truthmark Areas

## Evidence Stages

Truth documents:
```yaml
truth_documents:
  - path: docs/truthmark/engineering/research/evidence-stages.md
    lane: engineering
    kind: engineering-contract
```

Code surface:
- docs/methodology/README.md
- data/repositories.json
- data/evaluations.json
- docs/tool-dossiers/**
- docs/reports/**
- docs/research/tool-research-strategy.md
- scripts/validate_repository.py
- scripts/audit_dossier_snapshots.py
- templates/tool-dossier.md

Update truth when:
- the allowed evidence-stage taxonomy changes
- dossier promotion rules, decision-bearing thresholds, or report claim wording rules change
- validation starts accepting or rejecting a different evidence-stage shape

## Methodology And Reporting Workflow

Truth documents:
```yaml
truth_documents:
  - path: docs/truthmark/engineering/research/methodology.md
    lane: engineering
    kind: engineering-workflow
```

Code surface:
- docs/methodology/README.md
- docs/research/**
- docs/reports/**
- docs/standards/**
- prompts/researcher.md
- prompts/paper-writer.md
- templates/report.md
- templates/claim-entry.md
- .agents/skills/claim-evidence-auditor.md
- .agents/skills/scientific-report-reviewer.md
- .agents/skills/citation-light-prior-art-mapper.md
- .agents/skills/figure-table-planner.md

Update truth when:
- research-report writing, claim audit, prior-art framing, or figure/table planning rules change
- report standards or reusable methodology docs change what future agents must do

## Token Accounting And Benchmark Protocols

Truth documents:
```yaml
truth_documents:
  - path: docs/truthmark/engineering/research/token-accounting.md
    lane: engineering
    kind: engineering-contract
```

Code surface:
- data/evaluations.json
- data/workflow-task-sequences.json
- data/workflow-sessions.json
- docs/evaluations/**
- docs/evaluations/sequential-workflow-runner.md
- scripts/audit_tool_isolation.py
- scripts/extract_codex_usage.py
- scripts/run_codex_fixture_evaluation.py
- scripts/run_codex_workflow_evaluation.py
- scripts/run_sequential_workflow_matrix.py
- scripts/run_sequential_workflow_pair.sh
- scripts/test_workflow_evaluation_contract.py
- scripts/update_workflow_runbook.py
- sources/evaluations/fixtures/container/Dockerfile

- prompts/evaluator.md
- templates/evaluation-record.md
- templates/evaluation-task.md
- templates/evaluation-run-record.json
- templates/workflow-session-record.json
- schemas/evaluation-run-record.schema.json
- schemas/workflow-session-record.schema.json
- docs/tool-dossiers/**
- .agents/skills/benchmark-protocol-writer.md

Update truth when:
- token-accounting boundaries, benchmark protocols, metrics, task fixtures, or evaluation artifact requirements change
- Phase 2 benchmark plans change what counts as benchmark-audit or reproduction evidence

## Software Quality Gates

Truth documents:
```yaml
truth_documents:
  - path: docs/truthmark/engineering/research/software-quality-gates.md
    lane: engineering
    kind: engineering-contract
```

Code surface:
- docs/evaluations/token-usage-and-quality-standards.md
- docs/evaluations/evaluation-framework.md
- docs/evaluations/immediately-usable-flows.md
- prompts/evaluator.md
- templates/evaluation-record.md
- templates/evaluation-run-record.json
- .agents/skills/practical-software-quality-reviewer.md

Update truth when:
- verification, quality scoring, diagnostic preservation, reviewability, or safety gates change
- evaluation rules change how token savings are paired with software quality

## Stack Compatibility

Truth documents:
```yaml
truth_documents:
  - path: docs/truthmark/engineering/research/stack-compatibility.md
    lane: engineering
    kind: engineering-architecture
```

Code surface:
- data/compatibility-edges.json
- data/techniques.json
- docs/taxonomy/compatibility-taxonomy.md
- docs/architecture/compatibility-graph.md
- docs/reports/phase-1-compatibility-safe-token-saving-stacks.md
- docs/tool-dossiers/**
- .agents/skills/stack-ablation-planner.md

Update truth when:
- owned surfaces, compatibility edges, stack hypotheses, or ablation expectations change
- source-logic or benchmark evidence changes the compatibility-safe stack framing

## Current Findings

Truth documents:
```yaml
truth_documents:
  - path: docs/truthmark/engineering/research/current-findings.md
    lane: engineering
    kind: engineering-behavior
```

Code surface:
- README.md
- docs/research/roadmap.md
- data/repositories.json
- data/tool-analysis-backlog.json
- docs/reports/**
- docs/tool-dossiers/**

Update truth when:
- the current phase, active research direction, durable findings, limitations, or backlog interpretation changes
- a lead becomes source-logic, benchmark-audit, or reproduction evidence

## Agent Research Workflow

Truth documents:
```yaml
truth_documents:
  - path: docs/truthmark/engineering/research/agent-workflow.md
    lane: engineering
    kind: engineering-workflow
```

Code surface:
- AGENTS.md
- .agents/skills/**
- .truthmark/config.yml
- docs/truthmark/**
- scripts/validate_repository.py
- README.md

Update truth when:
- repo-local agent instructions, installed local skills, Truthmark routing, or validation workflow changes
- future agents need a different maintenance sequence for research-truth work

## Research Route Support

Area files:
- docs/truthmark/routes/areas/research.md

Code surface:
- docs/truthmark/routes/areas/research.md

Update truth when:
- Truthmark requires a child route file for generated hierarchy metadata

## Source References

- ../../../.truthmark/config.yml
- ../../../AGENTS.md
- ../../../docs/research/report-writing-and-methodology-skill-patterns.md
