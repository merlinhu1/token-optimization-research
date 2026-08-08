---
status: active
doc_type: area-route
source_of_truth:
  - ../../../../.truthmark/config.yml
  - ../areas.md
last_reviewed: 2026-08-05
---

# Research Route Support

## Research Truth Documents

Truth documents:
```yaml
truth_documents:
  - path: docs/truthmark/engineering/research/agent-workflow.md
    kind: engineering-workflow
    lane: engineering
  - path: docs/truthmark/engineering/research/current-findings.md
    kind: engineering-behavior
    lane: engineering
  - path: docs/truthmark/engineering/research/evidence-stages.md
    kind: engineering-contract
    lane: engineering
  - path: docs/truthmark/engineering/research/methodology.md
    kind: engineering-workflow
    lane: engineering
  - path: docs/truthmark/engineering/research/software-quality-diagnostics.md
    kind: engineering-contract
    lane: engineering
  - path: docs/truthmark/engineering/research/stack-compatibility.md
    kind: engineering-architecture
    lane: engineering
  - path: docs/truthmark/engineering/research/token-accounting.md
    kind: engineering-contract
    lane: engineering
```

Code surface:
- docs/truthmark/engineering/research/**
- docs/truthmark/routes/areas.md
- .truthmark/config.yml

Update truth when:
- research truth documents or their route ownership changes
- Truthmark routing or configuration changes
