# Compatibility Graph

## Why graph, not list

Token-saving techniques are not independent features. They alter parts of an agent context pipeline. A taxonomy that only groups by marketing description misses the most important question: **can two techniques be used together without double-processing, hiding evidence, or increasing turn count?**

The compatibility graph answers that question.

## Node types

- `technique` — atomic intervention, e.g. terminal-output compression.
- `surface` — buffer/control point, e.g. shell stdout, MCP JSON, memory injection.
- `artifact` — repository or product implementing techniques.
- `bundle` — artifact that packages multiple implementations.

## Edge types

| Edge | Meaning |
|---|---|
| `owns_surface` | Technique controls a buffer or authority. |
| `conflicts_with` | Techniques should not both be active on the same surface without ordering or gating. |
| `stacks_with` | Techniques operate on different surfaces and are likely composable. |
| `requires_ordering` | Techniques may compose only in a specified order. |
| `depends_on` | One technique requires another to produce input or metadata. |
| `subsumes` | One technique includes the other as a special case. |
| `unknown` | Relationship needs evaluation. |

## Compatibility groups

Compatibility groups are first-class because they define likely conflict sets.

| Group | Surface authority | Examples of conflicts |
|---|---|---|
| `terminal_output_owner` | stdout/stderr returned to the model | RTK-like proxy vs another shell-output proxy wrapping the same command. |
| `code_retrieval_authority` | how source is selected/read | Code graph vs repo pack when both are used blindly. |
| `tool_response_owner` | fields returned by MCP/API tools | Two schema trimmers deleting different fields. |
| `workflow_execution_owner` | where multi-step analysis executes | Sandbox code-mode vs agent-native step-by-step execution. |
| `context_compression_owner` | compressed long prompts/history/logs | Learned compression plus deterministic summaries without raw fallback. |
| `memory_authority` | facts injected as persistent context | Multiple memory systems re-injecting stale or contradictory facts. |
| `output_style_controller` | model prose style | Multiple terse prompts making output too lossy. |
| `artifact_policy_controller` | generated code/doc minimalism | YAGNI/minimal-code skills with conflicting safety/style policies. |
| `routing_authority` | model/provider/cache choices | Multiple routers with inconsistent quality or privacy policies. |

## Evaluation implications

Each compatibility group needs at least three evaluations:

1. **Best single representative** — does the technique work when isolated?
2. **Conflict pair** — what happens if two same-surface tools are layered?
3. **Orthogonal stack** — what happens when paired with a different-surface technique?

## Data contract

Compatibility edges are stored in `data/compatibility-edges.json`.

Each edge requires:

- `source_id`
- `target_id`
- `edge_type`
- `rationale`
- `confidence`
- `evidence`: `architectural | documented | evaluated | unknown`
- `notes`
