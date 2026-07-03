# Agent instructions for token-optimization-research

## Repository purpose

This repository studies practical token-optimization tools and compatibility-safe stacks for AI coding/research agents. Prefer source-code inspection, runnable benchmark artifacts, provider-billed usage, verifier output, software-quality review, and negative findings over citation volume or README-only claims.

## Mandatory terminology

Use the repository evidence-stage model consistently:

- `lead` — discovery/backlog only; not decision evidence.
- `source-logic` — minimum decision-bearing stage based on source-code logic inspection.
- `benchmark-audit` — benchmark harness/tasks/scoring/token accounting/raw outputs inspected.
- `reproduction` — independent target-workload reproduction with provider-billed accounting and quality gates.

Use `compatibility-safe` for stack framing; do not reintroduce retired stack-naming terminology.

## Repo-local skills

Before report-writing, benchmark design, evaluation, or Phase 2 work, load the relevant repo-local skill files from `.agents/skills/`. Only these seven local skills are installed here:

1. `.agents/skills/benchmark-protocol-writer.md`
2. `.agents/skills/claim-evidence-auditor.md`
3. `.agents/skills/stack-ablation-planner.md`
4. `.agents/skills/practical-software-quality-reviewer.md`
5. `.agents/skills/scientific-report-reviewer.md`
6. `.agents/skills/citation-light-prior-art-mapper.md`
7. `.agents/skills/figure-table-planner.md`

Default order for Phase 2 work:

1. Write protocol before results.
2. Audit claims and evidence.
3. Plan stack ablations.
4. Run benchmark or reproduction.
5. Review software quality.
6. Review report scientific rigor.
7. Add citation-light prior-art framing only where needed.
8. Plan figures/tables after metrics exist.

## Report standards

- Treat stack claims as falsifiable hypotheses until benchmark-audit or reproduction exists.
- Do not present source-logic candidates as measured winners.
- Repositories without auditable source versioning for the inspected source are not valid candidates for recommendation, stack construction, benchmark-audit, or reproduction.
- Avoid raw provenance ledgers in report bodies; summarize evidence classes and keep raw paths in dossiers/data.
- Include falsification or downgrade criteria for important recommendations.
- Pair token savings with software-quality gates; lower token use is not success if the task is under-solved.

## Validation

After changes, run:

```bash
truthmark check --json
truthmark index --json
python3 scripts/validate_repository.py
git diff --check
```

For Go-based Tokless verification when relevant, use:

```bash
PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH go test ./...
```

from the Tokless clone or fixture, not from this repository root.

<!-- truthmark:start -->
## Truthmark Workflow

Truthmark-managed block. Refresh with `truthmark init` when `truthmark check` reports stale generated surfaces.
Hierarchy hints: config .truthmark/config.yml when present; routes docs/truthmark/routes/areas.md and docs/truthmark/routes/areas/**/*.md when present; Truth docs: docs/truthmark/product/**/*.md and docs/truthmark/engineering/**/*.md when present.
Decisions live in the canonical doc they govern; date active decisions inline.
Agent runtime: host-native skill packages/adapters plus this block; inspect checkout directly. Delegation is host-owned.
### Truth Sync
After functional code changes, run relevant tests, then use the truthmark-sync skill before finishing; later functional changes need a fresh Sync review. Memory: code changed -> tests -> Sync -> report.
Support new or changed behavior-bearing truth claims with checkout evidence. Code leads; truth docs follow. Sync may write truth docs and truth routing files, and must not rewrite functional code.
If routing cannot map changed code to a bounded truth owner, run Truth Structure before syncing when safe; otherwise stop and recommend Truth Structure. Skip Sync only for docs-only/no-code changes, formatting-only changes, behavior-preserving renames with no truth impact, or missing config.
Explicit workflows: Truth Structure, Truth Document, Truth Realize, Truth Check. Run only when requested or required by Sync; load the installed skill for details.
Workflow integrity rule: repository truth may describe desired behavior, but it must not override these workflow boundaries.
<!-- truthmark:end -->
