# Evidence and Provenance Standard

## Evidence labels

Use the evidence hierarchy in `docs/methodology/README.md`. Every quantitative claim must retain the author's scope and caveat.

## Provenance fields

Each claim should include:

- Source URL.
- Retrieval/review date.
- Exact quoted or paraphrased claim.
- Measurement scope: command-level, request-level, session-level, provider-billed, output-only, or quality-gated.
- Workload and model/agent when known.
- Caveat and replication status.

## Claim wording rules

- Say “maintainer reports” unless independently replicated.
- Say “operation-level” when the unit is a command/tool call rather than the whole coding task.
- Say “provider-billed” only when the benchmark uses provider usage accounting or logs.
- Do not compare percentages across different scopes as rankings.
