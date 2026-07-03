# Analysis Plan

## Unit of analysis

The primary unit is a `(fixture, profile, replicate)` run. Aggregation is stratified by primary token-waste surface before any cross-suite summary is reported.

## Primary comparisons

| Stratum | Primary comparison | Claim enabled only if |
|---|---|---|
| Terminal/build output | terminal treatment vs native baseline on each terminal fixture | required diagnostics preserved and artifact tokens or provider-billed usage improve |
| Retrieval/navigation | retrieval treatment vs native baseline on both retrieval fixtures | expected target appears within budget and verifier passes after agent execution |
| Memory rediscovery | memory treatment vs no-memory baseline across sequential tasks | later task uses convention with fewer broad reads and no stale-state failure |
| Broad owner / MCP trace | single broad-owner or offload profile vs native baseline | raw evidence remains recoverable and no hidden overlapping owner appears |
| Installer/orchestrator | generated profile vs hand-specified desired profile | generated config matches intended surfaces and cleanup leaves no stale hooks |
| Replacement runtime | replacement runtime vs native baseline on same verifier | same verifier passes and cost, latency, or quality justifies runtime trust boundary |

## Minimum evidence for report language

- `ready-to-run`: fixture record, prompt, verifier, reset, and artifact contract exist and validation passes.
- `benchmark-audit`: existing or generated benchmark harness, task, scoring, token accounting, raw outputs, and failure semantics are inspected and recorded.
- `reproduction`: baseline and treatment are run from the same fixture with provider-billed usage where available, verifier output, transcript, quality review, and reset notes.

## Metrics

Primary metrics:

1. verifier pass/fail;
2. provider-billed total tokens or cost when available;
3. practical software quality score `0..5`;
4. diagnostic preservation pass/fail for compaction tasks;
5. install/reset pass/fail.

Secondary metrics:

- raw artifact tokens;
- transformed artifact tokens;
- turns;
- tool calls;
- correction turns;
- wall-clock time;
- target-file retrieval rank;
- broad-read count;
- stale-state incidents.

## Aggregation

Report medians and paired deltas by fixture and stratum. Do not pool terminal-output, retrieval, memory, broad-owner, installer, and replacement-runtime results into one headline number. If repeated runs exist, show within-fixture variability before cross-fixture averages.

## Negative evidence handling

Failed setup, timeout, verifier failure, diagnostic loss, hidden overlap, and reset failure remain in the denominator. Excluding a run requires a written exclusion reason and cannot be used to improve a positive-rate claim.

## Falsification criteria

A profile is downgraded if any of the following hold:

- it reduces visible tokens while losing a required diagnostic;
- it passes only by changing task scope or weakening the verifier;
- it requires a non-resettable state change;
- it enables an unplanned overlapping surface;
- it lacks raw artifact recovery;
- it improves operation-level artifact tokens but worsens provider-billed task totals without a documented non-cost benefit.
