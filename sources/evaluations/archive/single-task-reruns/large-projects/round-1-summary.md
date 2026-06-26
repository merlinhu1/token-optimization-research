# Round 1 Preliminary Summary

## Scope

Round 1 executed GPT-5.5 high-effort Codex runs on the two active large-project fixtures:

- Django: `django-slugify-strip-regression`
- Terraform: `terraform-startswith-known-prefix-regression`

Profiles:

- `baseline-codex-no-mcp`
- `retrieval-leanctx`

## Execution controls

- Baseline runs were Codex no-MCP substrate runs: Codex native shell/edit/file operations were allowed, while user-configured MCP servers and token-saving plugins were not exposed.
- Lean-ctx treatment reruns used an isolated `CODEX_HOME` containing only the lean-ctx MCP server plus copied authentication.
- Codex sandbox had to be disabled because the local bubblewrap wrapper cannot create namespaces on this host. This is recorded in each run record.
- Tool-isolation audit was run against every transcript.

## Valid completed runs

| Fixture | Baseline ID | Treatment ID | Baseline total tokens | Treatment total tokens | Delta |
|---|---|---|---:|---:|---:|
| Django | `django-slugify-strip-regression-baseline-codex-no-mcp-r1` | `django-slugify-strip-regression-retrieval-leanctx-r2` | 326096 | 233174 | -28.5% |
| Terraform | `terraform-startswith-known-prefix-regression-baseline-codex-no-mcp-r1` | `terraform-startswith-known-prefix-regression-retrieval-leanctx-r2` | 238195 | 538205 | +126.0% |

Both valid baseline and treatment runs passed their deterministic verifiers and received quality score 5.

## Excluded runs retained as evidence

| Run | Reason |
|---|---|
| `planned-django-slugify-strip-regression-baseline-codex-no-mcp-r0` | Codex sandbox/bubblewrap namespace failure prevented shell commands and edits. |
| `django-slugify-strip-regression-retrieval-leanctx-r1` | Tool-isolation audit failed because ambient Codex Ponytail/Caveman plugin instructions were exposed. |
| `terraform-startswith-known-prefix-regression-retrieval-leanctx-r1` | Tool-isolation audit failed because ambient Codex Ponytail/Caveman plugin instructions were exposed. |

## Preliminary interpretation

This is not enough for a tool recommendation. It shows the additive Codex-lane experiment loop works and that lean-ctx can either reduce or increase total provider-token usage depending on the task and interaction pattern.

- Django showed lower total provider tokens and lower fresh input tokens for the isolated lean-ctx treatment.
- Terraform showed substantially higher total provider tokens and higher fresh input tokens for the isolated lean-ctx treatment.
- Both treatments preserved software quality on these seeded repair tasks.

Next steps should add replicates and inspect whether Terraform overhead came from broad lean-ctx reads, extra command/tool calls, or task simplicity making retrieval overhead dominate.
