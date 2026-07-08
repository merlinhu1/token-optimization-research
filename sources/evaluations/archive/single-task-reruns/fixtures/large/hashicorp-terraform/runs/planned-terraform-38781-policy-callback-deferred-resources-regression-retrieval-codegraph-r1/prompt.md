# Evaluation isolation contract

You are running inside the `retrieval-codegraph` treatment lane for CodeGraph. Tool-state condition: `cold`. Tool-use policy: `optional`. CodeGraph is available as an optional retrieval/context tool. Use it only when graph-backed navigation is likely to reduce total context or improve localization; otherwise use Codex native shell/file tools. Do not use other retrieval, compression, memory, or token-saving tools. Work only inside the target repository and use the verifier as the acceptance gate.

---

You are repairing a real issue-derived regression in hashicorp/terraform.

Issue source: PR #38781
Task: Repair Terraform policy callback APIs so policy evaluation handles deferred resources and data sources consistently during plan and apply.

The repository has already been checked out at the pinned fixed upstream commit and then seeded with a regression that removes the relevant production fix. Do not look for a toy one-line answer; this is intentionally a multi-file large-project task.

Constraints:
- Work only inside the fixture repository.
- Use the verifier below as the acceptance gate.
- Prefer the smallest maintainable production-code change that restores the real upstream behavior.
- Do not modify tests unless you can justify that the upstream test itself is wrong.
- Preserve project style and existing public APIs.

Complexity note: Requires tracing callback server API behavior through node policy resources and both plan/apply policy execution paths.

Verifier:
go test ./internal/terraform -run "TestContext2(Apply|Plan)_PolicyCallback_(GetDataSource|GetResources_Deferral)" -count=1
