# Evaluation isolation contract

You are running inside the `retrieval-leanctx-warm-optional` treatment lane for LeanCTX. Tool-state condition: `warm-index`. Tool-use policy: `optional`. LeanCTX is available as an optional retrieval/context tool. Use it only when it is likely to reduce total context or improve localization; otherwise use Codex native shell/file tools. Do not use other retrieval, compression, memory, or token-saving tools. Work only inside the target repository and use the verifier as the acceptance gate.

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
