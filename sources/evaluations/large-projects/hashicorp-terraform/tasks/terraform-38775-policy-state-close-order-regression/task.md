# terraform-38775-policy-state-close-order-regression

## Fixture

- Fixture ID: `large-hashicorp-terraform`
- Project: `hashicorp-terraform`
- Upstream: `hashicorp/terraform`
- Real issue/PR source: `PR #38775`
- Pinned fixed commit: `afc607b675afef6995612fdff767fa65ecea681e`
- Evidence stage target: `reproduction`
- Task class: `real-issue-derived-multi-file-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Repair Terraform policy graph ordering so state is closed only after all graph nodes that may mutate state have finished.

## Why this is relatively complex

Requires coordinating saved-plan apply behavior with graph transforms and policy-client state lifecycle ordering.

The seed patch reverses production-code portions of a real upstream fix across 3 production files while leaving the upstream verifier tests in place.

## Seeded start state

Apply `seed-regression.patch` after checking out the pinned fixed commit. The patch creates a controlled broken state by reverting production-code portions of the real upstream fix without using a user-owned repository.

## Agent prompt

- Path: `sources/evaluations/large-projects/hashicorp-terraform/tasks/terraform-38775-policy-state-close-order-regression/agent-prompt.txt`
- SHA-256: `6fc01069b150bb206727622cc527094af96aa66861e17c041109103fbbc054b1`

## Verifier

```bash
sources/evaluations/large-projects/hashicorp-terraform/tasks/terraform-38775-policy-state-close-order-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
go test ./internal/command ./internal/terraform -run "TestApply_PolicyResultsJSON_WithSavedPlan|TestApplyGraphBuilder_PolicyClient|TestPlanGraphBuilder_PolicyClient" -count=1
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the real issue-derived regression unless explicitly justified.
- The solution coordinates all affected production paths rather than hard-coding only the visible failing assertion.
- No forbidden ambient token-saving tools appear in the transcript for baseline runs.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
