# Evaluation isolation contract

You are running inside the `retrieval-leanctx` treatment lane for LeanCTX. Tool-state condition: `cold`. Tool-use policy: `optional`. LeanCTX is available as an optional retrieval/context tool. Use it only when it is likely to reduce total context or improve localization; otherwise use Codex native shell/file tools. Do not use other retrieval, compression, memory, or token-saving tools. Work only inside the target repository and use the verifier as the acceptance gate.

---

You are repairing a real issue-derived regression in hashicorp/terraform.

Issue source: PR #38775
Task: Repair Terraform policy graph ordering so state is closed only after all graph nodes that may mutate state have finished.

The repository has already been checked out at the pinned fixed upstream commit and then seeded with a regression that removes the relevant production fix. Do not look for a toy one-line answer; this is intentionally a multi-file large-project task.

Constraints:
- Work only inside the fixture repository.
- Use the verifier below as the acceptance gate.
- Prefer the smallest maintainable production-code change that restores the real upstream behavior.
- Do not modify tests unless you can justify that the upstream test itself is wrong.
- Preserve project style and existing public APIs.

Complexity note: Requires coordinating saved-plan apply behavior with graph transforms and policy-client state lifecycle ordering.

Verifier:
go test ./internal/command ./internal/terraform -run "TestApply_PolicyResultsJSON_WithSavedPlan|TestApplyGraphBuilder_PolicyClient|TestPlanGraphBuilder_PolicyClient" -count=1
