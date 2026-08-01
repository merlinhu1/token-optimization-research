# Terraform lifecycle v0 fixture

- Upstream: `https://github.com/hashicorp/terraform.git`
- Snapshot: `e02391ad384c9c38f1d7f40b853c0d2297348094`
- Sequence: `terraform-lifecycle-sequence-v0`
- Active generation: `baseline-v5`
- Qualification: `qualification-lifecycle-v0-baseline-v5.json`
- Stages: policy-callback feature compilation → configuration refactor compilation → address review compilation

The controller applies all three Baseline V5 production seeds before prompt 1, evaluates all three affected-package compile commands after prompt 3, and then compiles every Go package with tests disabled. Component and final project compilation are the sole pass/fail gates; tests, behavior, style, and source-review quality are diagnostics only.
