# terraform-38745-config-parser-concurrency-regression

## Fixture

- Fixture ID: `large-hashicorp-terraform`
- Project: `hashicorp-terraform`
- Upstream: `hashicorp/terraform`
- Real issue/PR source: `PR #38745`
- Shared workflow base commit: `e02391ad384c9c38f1d7f40b853c0d2297348094`
- Original fixed commit: `8de90a32ef3d48017db4b14ab591bef313348d70`
- Evidence stage target: `reproduction`
- Task class: `real-issue-derived-multi-file-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Repair Terraform config parsing so parser and source-bundle loading remain safe under concurrent directory loads.

## Why this is relatively complex

Requires understanding shared parser state across configload and source-bundle parser entry points under race detection.

The seed patch reverses production-code portions of a real upstream fix across 4 production files while leaving the upstream verifier tests in place.

## Seeded start state

Apply `seed-regression.patch` after checking out the shared workflow base commit. The patch creates a controlled broken state by reverting production-code portions of the real upstream fix without using a user-owned repository.

## Agent prompt

- Path: `sources/evaluations/large-projects/hashicorp-terraform/tasks/terraform-38745-config-parser-concurrency-regression/agent-prompt.txt`
- SHA-256: `2b9492d68d402cf659963ab2f23b50a58e6d13e4a1619de3b09b3cbde3458e03`

## Verifier

```bash
sources/evaluations/large-projects/hashicorp-terraform/tasks/terraform-38745-config-parser-concurrency-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
go test -race ./internal/configs/configload ./internal/configs -run "TestLoaderSourcesConcurrentWithParserWrite|TestSourceBundleParserConcurrentLoadConfigDir|TestParserLoadConfigDirSuccess" -count=1
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the real issue-derived regression unless explicitly justified.
- The solution coordinates all affected production paths rather than hard-coding only the visible failing assertion.
- No forbidden ambient token-saving tools appear in the transcript for baseline runs.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
