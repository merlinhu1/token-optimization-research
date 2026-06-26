# terraform-38781-policy-callback-deferred-resources-regression

## Fixture

- Fixture ID: `large-hashicorp-terraform`
- Project: `hashicorp-terraform`
- Upstream: `hashicorp/terraform`
- Real issue/PR source: `PR #38781`
- Pinned fixed commit: `e02391ad384c9c38f1d7f40b853c0d2297348094`
- Evidence stage target: `reproduction`
- Task class: `real-issue-derived-multi-file-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Repair Terraform policy callback APIs so policy evaluation handles deferred resources and data sources consistently during plan and apply.

## Why this is relatively complex

Requires tracing callback server API behavior through node policy resources and both plan/apply policy execution paths.

The seed patch reverses production-code portions of a real upstream fix across 4 production files while leaving the upstream verifier tests in place.

## Seeded start state

Apply `seed-regression.patch` after checking out the pinned fixed commit. The patch creates a controlled broken state by reverting production-code portions of the real upstream fix without using a user-owned repository.

## Agent prompt

- Path: `sources/evaluations/large-projects/hashicorp-terraform/tasks/terraform-38781-policy-callback-deferred-resources-regression/agent-prompt.txt`
- SHA-256: `8833427b7297807cc5bb4c7f10a244cee2dfff555d075d2dfe79f9ac8afcd85a`

## Verifier

```bash
sources/evaluations/large-projects/hashicorp-terraform/tasks/terraform-38781-policy-callback-deferred-resources-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
go test ./internal/terraform -run "TestContext2(Apply|Plan)_PolicyCallback_(GetDataSource|GetResources_Deferral)" -count=1
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the real issue-derived regression unless explicitly justified.
- The solution coordinates all affected production paths rather than hard-coding only the visible failing assertion.
- No forbidden ambient token-saving tools appear in the transcript for baseline runs.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
