---
name: benchmark-protocol-writer
description: Use before running Phase 2 benchmark-audit or reproduction tasks to freeze hypotheses, baselines, metrics, token accounting, quality gates, and artifacts.
---
# Benchmark Protocol Writer

## Purpose

Write the protocol before results. This prevents metric gaming and keeps Phase 2 evaluations reproducible.

## When to Use

Use before any benchmark-audit or reproduction run, especially when comparing token-saving stacks, tools, profiles, or replacement-agent runtimes.

## Required Protocol

Each protocol must define:

1. **Hypothesis** in the form `profile X improves metric Y for workload Z`.
2. **Evidence stage target**: `benchmark-audit` or `reproduction`.
3. **Task fixture**:
   - repository/path;
   - commit or snapshot;
   - task prompt;
   - allowed tools;
   - maximum turns/time.
4. **Baseline**:
   - vanilla agent or lower-intervention stack;
   - exact model/provider;
   - exact command or flow.
5. **Treatment**:
   - enabled tools/components;
   - installed profile/config;
   - reset/uninstall path.
6. **Token accounting boundary**:
   - provider-billed task usage preferred;
   - fresh input, cached input, cache-write, output, and reasoning tokens where available;
   - estimated tool-result tokens only as secondary evidence.
7. **Software-quality gates**:
   - verifier command;
   - diff quality expectations;
   - diagnostic preservation;
   - raw-output recovery;
   - safety/reversibility.
8. **Failure and exclusion rules**:
   - what counts as under-solving;
   - what counts as tool breakage;
   - what result would falsify the hypothesis.

## Artifact Locations

Use existing templates and docs:

- `templates/evaluation-task.md`
- `templates/evaluation-run-record.json`
- `docs/evaluations/token-usage-and-quality-standards.md`
- `docs/evaluations/immediately-usable-flows.md`

Store run evidence under `sources/evaluations/<evaluation-id>/` when Phase 2 data collection starts.

## Common Pitfalls

- Running the treatment first and designing the baseline afterward.
- Changing prompts or fixtures between baseline and treatment.
- Reporting only visible prompt/token estimates rather than provider-billed usage.
- Counting partial task completion as token savings.
- Treating runner preflight PATH as proof that Codex-launched login shells can see a non-MCP terminal tool.
- Keeping partial pre-fix and post-fix batch results in one summary after a harness or isolation defect is found.
