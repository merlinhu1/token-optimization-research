# Evaluation isolation contract

You are running inside the `baseline-codex-no-mcp` control lane. This is a Codex substrate baseline, not a model-only baseline: Codex native shell, file, git, and verifier operations are allowed. Do not use external retrieval, compression, memory, MCP, or token-saving tools. Work only inside the target repository and use the verifier as the acceptance gate.

---

You are repairing a real issue-derived regression in hashicorp/terraform.

Issue source: PR #38739
Task: Repair Terraform provider policy evaluation so sensitive paths marked on values are propagated into policy checks.

The repository has already been checked out at the pinned fixed upstream commit and then seeded with a regression that removes the relevant production fix. Do not look for a toy one-line answer; this is intentionally a multi-file large-project task.

Constraints:
- Work only inside the fixture repository.
- Use the verifier below as the acceptance gate.
- Prefer the smallest maintainable production-code change that restores the real upstream behavior.
- Do not modify tests unless you can justify that the upstream test itself is wrong.
- Preserve project style and existing public APIs.

Complexity note: Requires tracing sensitive path propagation from command policy wiring through module expansion, provider nodes, and apply-time policy evaluation.

Verifier:
go test ./internal/terraform -run TestContext2Apply_PolicyEvaluation_Full -count=1
