# hashicorp/terraform primary workflow fixture

Fixture ID: `large-hashicorp-terraform`
Status: active large-project reproduction fixture

- Upstream: `https://github.com/hashicorp/terraform`
- Pinned snapshot: `e02391ad384c9c38f1d7f40b853c0d2297348094`
- Runtime: Go
- Sequence: `terraform-maintenance-sequence-v1`

The five tasks reconstruct real upstream Terraform maintenance changes. Every seed changes at least five causally related production files, applies without conflicts to the pinned snapshot, and is accepted by controller-hidden behavior checks.

The controller injects one seed only after the previous repair passes, conceals post-fix tests and verifier assets from the model repository, and keeps future prompts, all seeds, provenance, and qualification evidence fixture-local.

`repo/` and `runs/` are generated locally and are not evaluation evidence unless a frozen protocol explicitly records them.
