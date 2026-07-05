# Research Standards

## Naming

- Repository IDs: lowercase owner/repo converted to `owner__repo`.
- Technique IDs: stable `TNN-name` IDs in `data/techniques.json`.
- Evaluation IDs: `eval-YYYYMMDD-technique-shortname`.
- Literature IDs: `firstauthor-year-shorttitle`.

## Required caveat classes

- `scope-mismatch`: operation-level vs task-level or billed usage mismatch.
- `quality-risk`: reduced context may omit required facts or diagnostics.
- `integration-overhead`: extra tool calls/turns may dominate savings.
- `benchmark-limited`: small-N, maintainer-run, synthetic, or non-representative benchmark.
- `compatibility-risk`: conflicts with another technique on the same surface.

## Output standards

Research outputs should be:

- Source-grounded.
- Reproducible or explicitly labeled exploratory.
- Technique-level before bundle-level.
- Honest about negative results.
- Clear about provider-billed vs estimated tokens.
