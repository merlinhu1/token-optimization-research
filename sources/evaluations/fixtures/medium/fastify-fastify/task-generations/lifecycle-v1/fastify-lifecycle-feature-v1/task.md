# Restore normalized request media-type support

Fastify requests must expose the normalized media type from the incoming `Content-Type` header through `request.mediaType`. Restore the complete feature so the value is available during validation and request handling, remains `undefined` when the header is absent, and continues to use the existing Content-Type parsing behavior.

Preserve the public request API and existing request lifecycle behavior.

Implement the task completely and correctly. Search and inspect the repository as needed, including related definitions and call sites. Choose the smallest coherent repair, run relevant existing tests and checks when practical, and preserve earlier task work in the persistent checkout.

Do not modify tests, generated files, dependency locks, or evaluation controls. Do not use network-dependent commands.
