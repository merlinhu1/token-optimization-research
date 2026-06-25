---
name: figure-table-planner
description: Use when turning token-optimization research results into report figures and tables with one clear message per visual.
---
# Figure and Table Planner

## Purpose

Plan visuals that communicate benchmark evidence clearly. Figures and tables should carry decision value, not decoration.

## When to Use

Use when drafting Phase reports, benchmark-audit reports, reproduction reports, or progress summaries with quantitative/structural evidence.

## Recommended Visuals

1. **Surface ownership matrix**
   - rows: tools/components;
   - columns: surfaces;
   - marks: owner, observer, conflict risk.
2. **Provider-billed task token table**
   - baseline vs treatment;
   - fresh/cached/cache-write/output/reasoning tokens;
   - task-level total and cost.
3. **Quality gate table**
   - verifier result;
   - quality score;
   - diagnostic preservation;
   - reset path;
   - notes.
4. **Ablation chart**
   - full stack vs removed/replaced components;
   - token and quality deltas together.
5. **Turns/tool-calls/latency table**
   - captures hidden workflow cost.
6. **Run trajectory**
   - shows benchmark development over repeated runs.
7. **Installer profile diff**
   - for Tokless-style generated profile/config evidence.

## Rules

- One visual, one message.
- Label metric direction, units, and accounting boundary.
- Include baseline and treatment in the same visual where possible.
- Pair token savings with quality/pass information.
- Do not chart estimates as if they were provider-billed values.
- Keep captions factual: setting, metric, main result, limitation.

## Common Pitfalls

- Beautiful figures without evidence value.
- Mixing unrelated metrics in one dense table.
- Reporting only percentage savings without absolute token/cost values.
- Omitting failed or excluded runs from result summaries.
