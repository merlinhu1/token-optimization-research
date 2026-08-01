# Restore the named provider-requirements contract

Complete the behavior-preserving state-migration refactor. `StateStoreProviderRequirement.Requirement` should use Terraform's named `providerreqs.Requirements` type so the parsed requirement can be passed directly to provider download and selection APIs.

Preserve the single-provider map contents, parsing behavior, diagnostics, and downstream compatibility.

Implement the task completely and correctly. Search and inspect the repository as needed, including related definitions and call sites. Choose the smallest coherent repair, run relevant existing tests and checks when practical, and preserve earlier task work in the persistent checkout.

Do not modify tests, generated files, dependency locks, or evaluation controls. Do not use network-dependent commands.
