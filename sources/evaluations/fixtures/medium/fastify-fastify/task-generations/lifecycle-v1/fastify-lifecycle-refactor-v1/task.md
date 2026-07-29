# Restore the shared bounded Content-Type cache

Restore the behavior-preserving Content-Type parsing refactor. Repeated parsing of the same raw header value should reuse one shared bounded cache instead of creating a new parsed object each time.

Keep parsing, normalization, serialization, and invalid-input behavior unchanged. The cache must remain shared by `ContentType.from` and bounded to avoid unbounded growth.

Implement the task completely and correctly. Search and inspect the repository as needed, including related definitions and call sites. Choose the smallest coherent repair, run relevant existing tests and checks when practical, and preserve earlier task work in the persistent checkout.

Do not modify tests, generated files, dependency locks, or evaluation controls. Do not use network-dependent commands.
