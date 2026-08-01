# Terraform lifecycle v0 fixture

- Upstream: `https://github.com/hashicorp/terraform.git`
- Snapshot: `e02391ad384c9c38f1d7f40b853c0d2297348094`
- Sequence: `terraform-lifecycle-sequence-v0`
- Active generation: `lifecycle-v1`
- Qualification: `qualification-lifecycle-v1.json`
- Stages: deferred policy callback propagation → provider-requirements refactor → checkable-address review

The controller applies all three semantic regressions before prompt 1. Agents receive normal engineering objectives and are expected to implement them correctly; evaluator scoring and compile commands are not model-facing. After prompt 3, the controller runs all affected-package compile commands and compiles every Go package with tests disabled. Component and final project compilation are the internal pass/fail gates; tests, behavior, style, and source-review quality are diagnostics.
