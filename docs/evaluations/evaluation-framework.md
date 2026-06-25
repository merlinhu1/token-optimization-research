# Evaluation Framework

## Evaluation layers

1. **Compression layer:** raw tokens in vs reduced tokens out.
2. **Fidelity layer:** whether required facts, code, diagnostics, schemas, and line references survive.
3. **Agent-behavior layer:** tool calls, turns, retries, and task success.
4. **Billing layer:** provider-billed input/output/cache tokens and cost when available.
5. **Human-value layer:** latency, debugging usefulness, trust, and review effort.

## Core metrics

- Raw tokens and reduced tokens.
- Fresh input tokens, cached input tokens, output tokens, and total billed cost when available.
- Tool-call count and turn count.
- Task success / validator pass rate.
- Diagnostic completeness for failing tasks.
- Raw fallback availability and retrieval cost.
- Setup overhead and integration complexity.

## Experiment types

| Type | Purpose |
|---|---|
| Micro-benchmark | Isolate one transformation on fixed artifacts. |
| Task artifact benchmark | Test whether reduced artifacts preserve task answers. |
| Agentic workflow pilot | Run a real coding task with an agent and measure behavior. |
| Provider-billed evaluation | Compare actual provider usage and cache effects. |
| Quality-retention review | Human or automated review of missed details and regressions. |

## Required controls

- Same repository snapshot.
- Same task prompt.
- Same agent/model where possible.
- Same max turns/time budget.
- Captured raw artifacts and transformed artifacts.
- Deterministic validators or documented human rubric.
