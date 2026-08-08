# Restore deferred data-source policy callback propagation

Policy data-source callbacks return both a result and whether evaluation is deferred. Restore the complete feature so the callback server propagates the returned deferred state into `GetDataSourceResponse` instead of discarding it.

Preserve callback lookup, MessagePack decoding and encoding, error handling, and non-deferred behavior.

Implement the task completely and correctly. Search and inspect the repository as needed, including related definitions and call sites. Choose the smallest coherent repair, run relevant existing tests and checks when practical, and preserve earlier task work in the persistent checkout.

Do not modify tests, generated files, dependency locks, or evaluation controls. Do not use network-dependent commands.
