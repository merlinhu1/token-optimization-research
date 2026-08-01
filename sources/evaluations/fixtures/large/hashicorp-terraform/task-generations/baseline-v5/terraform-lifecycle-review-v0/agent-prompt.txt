# Correct input-variable checkable address parsing

Review and correct the proposed input-variable address parsing change already present in the working tree. Terraform input-variable checkable addresses use the canonical `var.<name>` prefix; parsing must accept that form and preserve the existing module-instance path.

Make the correction in code, retain the current diagnostics for malformed addresses, and do not change the prefixes for output values, resources, or checks.

Implement the task completely and correctly. Search and inspect the repository as needed, including related definitions and call sites. Choose the smallest coherent repair, run relevant existing tests and checks when practical, and preserve earlier task work in the persistent checkout.

Do not modify tests, generated files, dependency locks, or evaluation controls. Do not use network-dependent commands.
