# Restore escaped separators in function-template arguments

Function-template arguments must allow separators such as commas to be escaped and treated as literal text. Restore complete escaped-separator handling while preserving ordinary argument splitting and the existing handling of other escapable template characters.

The fix must work for separators encountered while parsing function arguments without changing top-level template behavior.

Implement the task completely and correctly. Search and inspect the repository as needed, including related definitions and call sites. Choose the smallest coherent repair, run relevant existing tests and checks when practical, and preserve earlier task work in the persistent checkout.

Do not modify tests, generated files, dependency locks, or evaluation controls. Do not use network-dependent commands.
