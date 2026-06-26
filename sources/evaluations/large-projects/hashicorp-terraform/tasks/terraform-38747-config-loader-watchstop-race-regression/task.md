# terraform-38747-config-loader-watchstop-race-regression

## Fixture

- Fixture ID: `large-hashicorp-terraform`
- Project: `hashicorp-terraform`
- Upstream: `hashicorp/terraform`
- Real issue/PR source: `PR #38747`
- Shared workflow base commit: `e02391ad384c9c38f1d7f40b853c0d2297348094`
- Original fixed commit: `b4e933dd73ba8d4be04f1613808b53d5e129957c`
- Evidence stage target: `reproduction`
- Task class: `real-issue-derived-multi-file-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Repair Terraform planning/config-loading concurrency so module loading does not race with graph walk cancellation.

## Why this is relatively complex

Requires tracing config loading through command planning and Terraform graph-walk cancellation semantics.

The seed patch reverses production-code portions of a real upstream fix across 3 production files while leaving the upstream verifier tests in place.

## Seeded start state

Apply `seed-regression.patch` after checking out the shared workflow base commit. The patch creates a controlled broken state by reverting production-code portions of the real upstream fix without using a user-owned repository.

## Agent prompt

- Path: `sources/evaluations/large-projects/hashicorp-terraform/tasks/terraform-38747-config-loader-watchstop-race-regression/agent-prompt.txt`
- SHA-256: `e87dfc4669da225cfac05409518bf9f309d5fc031b2717a110366a6c643e1b98`

## Verifier

```bash
sources/evaluations/large-projects/hashicorp-terraform/tasks/terraform-38747-config-loader-watchstop-race-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
go test -race ./internal/command -run TestPlan_configLoaderRace -count=1
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the real issue-derived regression unless explicitly justified.
- The solution coordinates all affected production paths rather than hard-coding only the visible failing assertion.
- No forbidden ambient token-saving tools appear in the transcript for baseline runs.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
