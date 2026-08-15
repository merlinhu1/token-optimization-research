# Evaluation record template

## Identity

- Evaluation ID:
- Task ID:
- Technique/tool/stack IDs:
- Evidence stage: benchmark-audit | reproduction
- Run role: baseline | treatment | audit-only
- Date:
- Operator:

## Setup

- Agent/model/provider:
- Repository fixture and commit:
- Dataset/task:
- Baseline profile:
- Treatment profile:
- Enabled surfaces:
- Disabled overlapping surfaces:
- Reset procedure:

## Token usage

| Metric | Baseline | Treatment | Source/notes |
|---|---:|---:|---|
| Weighted token cost (`fresh + 0.1 × cached + 6 × output`) | | | Sole token metric |

## Agent behavior

| Metric | Baseline | Treatment | Notes |
|---|---:|---:|---|
| Turns | | | |
| Tool calls | | | |
| Correction turns | | | |
| Wall time | | | |
| Raw-output recovery used | | | |

## Software quality

| Gate | Baseline | Treatment | Notes |
|---|---|---|---|
| Deterministic verifier | | | |
| Static checks | | | |
| Diagnostic preservation | | | |
| Quality score | | | |
| Critical failures | | | |

## Interpretation

- Accepted result:
- Main uncertainty:
- Falsification or downgrade condition:

## Raw artifacts

- Transcript:
- Provider usage:
- Verifier output:
- Quality review:
- Raw/transformed artifacts:

## Caveats
