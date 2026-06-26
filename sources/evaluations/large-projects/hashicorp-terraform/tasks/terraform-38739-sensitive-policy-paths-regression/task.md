# terraform-38739-sensitive-policy-paths-regression

## Fixture

- Fixture ID: `large-hashicorp-terraform`
- Project: `hashicorp-terraform`
- Upstream: `hashicorp/terraform`
- Real issue/PR source: `PR #38739`
- Pinned fixed commit: `5ef60fcc6c11de94d6af1011d65b55be76325cd8`
- Evidence stage target: `reproduction`
- Task class: `real-issue-derived-multi-file-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Repair Terraform provider policy evaluation so sensitive paths marked on values are propagated into policy checks.

## Why this is relatively complex

Requires tracing sensitive path propagation from command policy wiring through module expansion, provider nodes, and apply-time policy evaluation.

The seed patch reverses production-code portions of a real upstream fix across 3 production files while leaving the upstream verifier tests in place.

## Seeded start state

Apply `seed-regression.patch` after checking out the pinned fixed commit. The patch creates a controlled broken state by reverting production-code portions of the real upstream fix without using a user-owned repository.

## Agent prompt

- Path: `sources/evaluations/large-projects/hashicorp-terraform/tasks/terraform-38739-sensitive-policy-paths-regression/agent-prompt.txt`
- SHA-256: `e2e0eb267402a3993b1a9a40b79c77d5786c093ac07fe0d543c770ee3609b353`

## Verifier

```bash
sources/evaluations/large-projects/hashicorp-terraform/tasks/terraform-38739-sensitive-policy-paths-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
go test ./internal/terraform -run TestContext2Apply_PolicyEvaluation_Full -count=1
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the real issue-derived regression unless explicitly justified.
- The solution coordinates all affected production paths rather than hard-coding only the visible failing assertion.
- No forbidden ambient token-saving tools appear in the transcript for baseline runs.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
